"""Test script for AI Pipeline Phase 1.

This script demonstrates the pipeline framework functionality:
1. Create a pipeline
2. Register a dummy stage
3. Process a FrameContext
4. Verify the same frame is returned
"""

import logging
from datetime import datetime

from app.services.ai.pipeline import (
    FrameContext,
    OfflinePipeline,
    PipelineFactory,
    PipelineStage,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


class DummyStage(PipelineStage):
    """Dummy pipeline stage for testing.
    
    This stage does not modify the frame, it simply returns
    the context unchanged. Used for validation only.
    """
    
    def process(self, context: FrameContext) -> FrameContext:
        """Process frame context (no-op for testing).
        
        Args:
            context: The frame context to process.
            
        Returns:
            The unchanged frame context.
        """
        return context


def main() -> None:
    """Run the pipeline test."""
    print("=" * 60)
    print("AI Pipeline Phase 1 - Test Script")
    print("=" * 60)
    
    # Step 1: Create pipeline
    print("\n[1] Creating pipeline...")
    pipeline = PipelineFactory.create_offline_pipeline()
    pipeline.initialize()
    print("✓ Pipeline created and initialized")
    
    # Step 2: Register dummy stage
    print("\n[2] Registering dummy stage...")
    dummy_stage = DummyStage()
    pipeline.manager.register_stage(dummy_stage)
    print(f"✓ Stage registered: {dummy_stage.__class__.__name__}")
    print(f"  Total stages: {pipeline.manager.stage_count}")
    
    # Step 3: Create FrameContext
    print("\n[3] Creating FrameContext...")
    dummy_frame = {"data": "test_frame_data"}
    timestamp = datetime.now()
    context = FrameContext(
        frame=dummy_frame,
        frame_number=1,
        timestamp=timestamp,
        metadata={"test": True},
    )
    print(f"✓ FrameContext created")
    print(f"  Frame number: {context.frame_number}")
    print(f"  Timestamp: {context.timestamp}")
    print(f"  Metadata: {context.metadata}")
    
    # Step 4: Process frame
    print("\n[4] Processing frame through pipeline...")
    result_context = pipeline.process_frame(context)
    print("✓ Frame processed")
    
    # Step 5: Verify result
    print("\n[5] Verifying results...")
    assert result_context.frame == dummy_frame, "Frame data mismatch!"
    assert result_context.frame_number == 1, "Frame number mismatch!"
    assert result_context.metadata == {"test": True}, "Metadata mismatch!"
    print("✓ Frame data unchanged (as expected)")
    print("✓ Frame number unchanged (as expected)")
    print("✓ Metadata unchanged (as expected)")
    
    # Step 6: Cleanup
    print("\n[6] Shutting down pipeline...")
    pipeline.shutdown()
    print("✓ Pipeline shutdown complete")
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    print("\nThe pipeline framework is ready for AI module integration.")
    print("Future stages can be added by implementing PipelineStage")
    print("and registering them with the PipelineManager.")


if __name__ == "__main__":
    main()
