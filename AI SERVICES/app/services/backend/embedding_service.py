"""
InsightFace GPU-accelerated face embedding service.

Architecture decisions:
  1. SINGLETON — The FaceAnalysis model (buffalo_l) is loaded ONCE during
     application startup inside the lifespan event.  Every subsequent API
     request reuses the already-loaded model.  Loading takes ~3–10 seconds
     depending on GPU; we pay this cost once, not on every request.

  2. THREAD-POOL — InsightFace / ONNX Runtime inference is CPU/GPU-bound
     synchronous code.  Running it directly on the asyncio event loop would
     block all other requests.  We offload it to a ThreadPoolExecutor via
     asyncio.get_event_loop().run_in_executor(None, ...) so the event loop
     stays responsive.

  3. GPU FALLBACK — Providers are ordered [CUDAExecutionProvider,
     CPUExecutionProvider].  ONNX Runtime selects the first available
     provider.  If CUDA is not installed, it silently falls back to CPU.

  4. FACE COUNT VALIDATION — Exactly ONE face must be detected.
     Zero faces  → ValidationException (400-equivalent)
     2+ faces    → ValidationException (400-equivalent)

  5. EMBEDDING DIMENSION — InsightFace buffalo_l produces 512-dimensional
     ArcFace embeddings.  Any other dimension causes a ServiceException.

Public API:
    embedding_service.initialize()          → call on startup
    embedding_service.generate_embedding()  → async, returns FaceEmbedding
    EmbeddingService.validate_embedding()   → static
    EmbeddingService.compare_embeddings()   → static, cosine similarity
    EmbeddingService.replace_pose()         → static, immutable list update
    EmbeddingService.build_placeholder_embeddings() → static
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from app.config.settings import settings
from app.core.exceptions import ServiceException, ValidationException
from app.models.student import FaceEmbedding, VALID_POSES

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Singleton service for face embedding generation and comparison.

    Do NOT instantiate this class directly.  Import and use the
    module-level `embedding_service` instance defined at the bottom.
    """

    def __init__(self) -> None:
        self._model: Optional[FaceAnalysis] = None
        self._initialized: bool = False

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def initialize(self) -> None:
        """
        Load the InsightFace model asynchronously.

        Delegates the blocking model load to a thread-pool executor so the
        event loop is never blocked during startup.

        Idempotent: calling this multiple times has no effect after the
        first successful load.

        Raises:
            ServiceException: If the model files cannot be loaded.
        """
        if self._initialized:
            logger.debug("EmbeddingService already initialised — skipping.")
            return

        logger.info(
            "Loading InsightFace model '%s' | ctx_id=%d | det_size=%d …",
            settings.INSIGHTFACE_MODEL_NAME,
            settings.INSIGHTFACE_CTX_ID,
            settings.INSIGHTFACE_DET_SIZE,
        )

        loop = asyncio.get_event_loop()
        # run_in_executor(None, ...) uses the default ThreadPoolExecutor
        await loop.run_in_executor(None, self._load_model_sync)

        self._initialized = True
        logger.info(
            "InsightFace model '%s' loaded and ready.",
            settings.INSIGHTFACE_MODEL_NAME,
        )

    def _load_model_sync(self) -> None:
        """
        Synchronous model initialisation — MUST run inside a thread-pool.

        Steps:
          1. Instantiate FaceAnalysis with the buffalo_l model name.
          2. Call prepare() to download weights (first run) and initialise
             the ONNX session with the specified execution providers.
        """
        try:
            self._model = FaceAnalysis(
                name=settings.INSIGHTFACE_MODEL_NAME,
                providers=[
                    "CUDAExecutionProvider",   # Preferred — NVIDIA GPU
                    "CPUExecutionProvider",    # Fallback — any CPU
                ],
            )
            self._model.prepare(
                ctx_id=settings.INSIGHTFACE_CTX_ID,
                det_size=(
                    settings.INSIGHTFACE_DET_SIZE,
                    settings.INSIGHTFACE_DET_SIZE,
                ),
            )
        except Exception as exc:
            logger.exception("Failed to load InsightFace model: %s", exc)
            raise ServiceException(
                "Face recognition model could not be initialised. "
                "Check that InsightFace and ONNX Runtime are installed correctly.",
                errors=[str(exc)],
            ) from exc

    def _assert_initialized(self) -> None:
        """Raise ServiceException if the model is not yet loaded."""
        if not self._initialized or self._model is None:
            raise ServiceException(
                "EmbeddingService is not initialised. "
                "Call await embedding_service.initialize() during application startup."
            )

    # =========================================================================
    # Public async API
    # =========================================================================

    async def generate_embedding(
        self, image_bytes: bytes, pose: str = "front"
    ) -> FaceEmbedding:
        """
        Detect a single face in *image_bytes* and return its 512-dim embedding.

        The heavy ONNX inference is executed in a thread-pool so the event
        loop remains responsive to other requests during GPU computation.

        Args:
            image_bytes: Raw JPEG / PNG image bytes.
            pose:        Head pose label for this embedding (default: 'front').

        Returns:
            A fully populated FaceEmbedding model with:
              - pose          : the *pose* argument
              - embedding     : list of 512 floats
              - quality_score : InsightFace detection confidence (0.0–1.0)
              - captured_at   : current UTC datetime

        Raises:
            ValidationException:
                - pose is not in VALID_POSES
                - image bytes cannot be decoded
                - 0 faces detected
                - 2+ faces detected
            ServiceException:
                - ONNX Runtime error during inference
                - Embedding dimension != 512
        """
        self._assert_initialized()

        # Validate pose before doing expensive I/O
        if pose not in VALID_POSES:
            raise ValidationException(
                f"Invalid pose '{pose}'. Must be one of: {VALID_POSES}."
            )

        # Decode image bytes into a NumPy BGR array (OpenCV format)
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValidationException(
                "The uploaded image could not be decoded. "
                "Ensure the file is a valid JPEG or PNG."
            )

        # Run blocking inference in thread-pool
        loop = asyncio.get_event_loop()
        embedding_vector, quality_score = await loop.run_in_executor(
            None, self._run_inference_sync, img_bgr
        )

        return FaceEmbedding(
            pose=pose,
            embedding=embedding_vector.tolist(),
            quality_score=float(quality_score),
            captured_at=datetime.now(timezone.utc),
        )

    def _run_inference_sync(
        self, img_bgr: np.ndarray
    ) -> tuple[np.ndarray, float]:
        """
        Run synchronous InsightFace detection and embedding extraction.

        This method MUST be called from a thread-pool executor.

        Args:
            img_bgr: OpenCV BGR NumPy image array.

        Returns:
            Tuple of (512-dim embedding ndarray, detection score float).

        Raises:
            ValidationException: 0 or 2+ faces found.
            ServiceException:    Inference error or wrong embedding dimension.
        """
        try:
            faces = self._model.get(img_bgr)
        except Exception as exc:
            logger.exception("InsightFace inference failed: %s", exc)
            raise ServiceException(
                "Face embedding extraction failed during model inference.",
                errors=[str(exc)],
            ) from exc

        # Face count validation
        if len(faces) == 0:
            raise ValidationException(
                "No face detected in the uploaded image. "
                "Please upload a clear, well-lit photo with a single visible face."
            )
        if len(faces) > 1:
            raise ValidationException(
                f"Multiple faces detected ({len(faces)} faces found). "
                "Please upload an image containing exactly one face."
            )

        face = faces[0]
        embedding: np.ndarray = face.embedding

        # Validate embedding dimension
        if not self.validate_embedding(embedding.tolist()):
            raise ServiceException(
                f"InsightFace returned an embedding of unexpected dimension "
                f"{len(embedding)} (expected {settings.EMBEDDING_DIMENSION}). "
                "Verify that the buffalo_l model is correctly installed."
            )

        detection_score: float = float(face.det_score)
        logger.debug(
            "Embedding extracted — dim=%d, quality=%.4f",
            len(embedding),
            detection_score,
        )
        return embedding, detection_score

    # =========================================================================
    # Static utility methods
    # =========================================================================

    @staticmethod
    def validate_embedding(embedding: list[float]) -> bool:
        """
        Return True if *embedding* is a non-empty 512-dimensional vector.

        Args:
            embedding: List of floats representing the face embedding.

        Returns:
            bool — True if length equals EMBEDDING_DIMENSION (512).
        """
        return len(embedding) == settings.EMBEDDING_DIMENSION

    @staticmethod
    def compare_embeddings(emb1: list[float], emb2: list[float]) -> float:
        """
        Compute cosine similarity between two 512-dimensional embeddings.

        Cosine similarity ranges from -1 (opposite) to 1 (identical).
        In practice, ArcFace embeddings for the same person yield > 0.4,
        while different individuals yield < 0.3.

        Args:
            emb1: First 512-dim embedding vector.
            emb2: Second 512-dim embedding vector.

        Returns:
            Float in [-1.0, 1.0]. Returns 0.0 if either vector is zero-norm.
        """
        a = np.array(emb1, dtype=np.float32)
        b = np.array(emb2, dtype=np.float32)
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0.0 or norm_b == 0.0:
            logger.warning("compare_embeddings: one or both vectors have zero norm.")
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def replace_pose(
        embeddings: list[FaceEmbedding],
        pose: str,
        new_embedding: FaceEmbedding,
    ) -> list[FaceEmbedding]:
        """
        Return a new list with the embedding for *pose* replaced.

        This is a pure function — the original *embeddings* list is not
        mutated.  If no embedding for the pose exists, the new one is appended.

        Args:
            embeddings:    Existing list of FaceEmbedding objects.
            pose:          The pose name to replace.
            new_embedding: The replacement FaceEmbedding.

        Returns:
            New list with the pose replaced or appended.
        """
        updated = [e for e in embeddings if e.pose != pose]
        updated.append(new_embedding)
        return updated

    @staticmethod
    def build_placeholder_embeddings(
        registered_poses: list[str],
    ) -> list[FaceEmbedding]:
        """
        Create empty placeholder embeddings for unregistered poses.

        Called during initial student registration when only a front image
        is provided.  Placeholder slots (empty embedding, zero quality score,
        no timestamp) are stored for the 4 remaining poses so that the
        MongoDB document has a consistent 5-pose structure from day one.

        These placeholders are replaced with real embeddings via the
        PUT /students/{id}/face endpoint as additional pose photos are captured.

        Args:
            registered_poses: Pose names that already have real embeddings.

        Returns:
            List of FaceEmbedding objects (with empty vectors) for each
            pose NOT in *registered_poses*.
        """
        return [
            FaceEmbedding(
                pose=pose,
                embedding=[],       # Empty — not yet captured
                quality_score=0.0,
                captured_at=None,
            )
            for pose in VALID_POSES
            if pose not in registered_poses
        ]


# =============================================================================
# Module-level singleton
# =============================================================================
# Import this instance throughout the application.  Never call EmbeddingService()
# again elsewhere — doing so would create a second model instance and waste GPU memory.
embedding_service = EmbeddingService()
