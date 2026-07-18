"""
NeuroProctor - AI-based Exam Cheating and Impersonation Detection

This is a lightweight, dummy representation of the project's main service module.
It outlines core components and flows (video capture, face recognition, behavior
analysis, logging, and reporting) but does not implement real ML models or I/O.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import time


@dataclass
class DetectionResult:
    timestamp: float
    student_id: str
    suspicion_score: float
    reasons: List[str]


class VideoCaptureService:

    def __init__(self):
        self.frame_index = 0

    def get_frame(self) -> Dict[str, Any]:
        self.frame_index += 1
        return {"frame_id": self.frame_index, "data": b"FAKE_FRAME"}


class FaceRecognitionService:

    def __init__(self, known_students: Dict[str, Any]):
        self.known_students = known_students

    def identify(self, frame: Dict[str, Any]) -> List[str]:
        if frame["frame_id"] % 5 == 0:
            return []  
        return [f"student_{(frame['frame_id'] % 3) + 1}"]


class BehaviorAnalysisService:
    def analyze(self, frame: Dict[str, Any], student_ids: List[str]) -> DetectionResult:
        ts = time.time()
        if not student_ids:
            return DetectionResult(ts, "unknown", 0.2, ["no_face_detected"])

        sid = student_ids[0]
        score = 0.1 + (frame["frame_id"] % 7) * 0.12
        reasons = []
        if score > 0.6:
            reasons.append("looking_away")
        if frame["frame_id"] % 11 == 0:
            reasons.append("multiple_people")
        return DetectionResult(ts, sid, min(score, 1.0), reasons)


class ReportService:


    def __init__(self):
        self.records: List[DetectionResult] = []

    def add(self, result: DetectionResult):
        self.records.append(result)
        print(f"[Report] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))} - "
              f"{result.student_id} - score={result.suspicion_score:.2f} reasons={result.reasons}")


def run_demo_loop(iterations: int = 20):

    video = VideoCaptureService()
    face = FaceRecognitionService(known_students={"student_1": {}, "student_2": {}, "student_3": {}})
    behavior = BehaviorAnalysisService()
    report = ReportService()

    for _ in range(iterations):
        frame = video.get_frame()
        ids = face.identify(frame)
        result = behavior.analyze(frame, ids)
        report.add(result)
        time.sleep(0.05)  


if __name__ == "__main__":
    run_demo_loop(30)
