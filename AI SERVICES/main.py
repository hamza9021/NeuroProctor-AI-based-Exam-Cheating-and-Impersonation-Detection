from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import time
import random
import json


@dataclass
class DetectionResult:
    timestamp: float
    student_id: str
    suspicion_score: float
    reasons: List[str]


@dataclass
class FaceData:
    face_id: int
    confidence: float
    location: Dict[str, float]
    features: List[float]


@dataclass
class EyeGazeData:
    direction: str
    confidence: float
    fixation_duration: float


@dataclass
class HeadPoseData:
    pitch: float
    yaw: float
    roll: float


@dataclass
class StudentProfile:
    student_id: str
    enrollment_id: str
    exam_id: str
    known_features: List[float]
    baseline_behavior: Dict[str, Any]
    risk_level: str


@dataclass
class SessionRecord:
    session_id: str
    student_id: str
    start_time: float
    end_time: Optional[float]
    total_frames: int
    suspicious_frames: int
    alerts: List[str]
    final_report: Optional[str]


class VideoCaptureService:

    def __init__(self, fps: int = 30):
        self.frame_index = 0
        self.fps = fps
        self.frame_width = 1920
        self.frame_height = 1080
        self.start_time = time.time()

    def get_frame(self) -> Dict[str, Any]:
        self.frame_index += 1
        timestamp = time.time() - self.start_time
        frame_data = {
            "frame_id": self.frame_index,
            "timestamp": timestamp,
            "data": b"FRAME_" + str(self.frame_index).encode(),
            "width": self.frame_width,
            "height": self.frame_height,
            "quality": random.uniform(0.7, 1.0)
        }
        return frame_data

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "fps": self.fps,
            "total_frames": self.frame_index,
            "width": self.frame_width,
            "height": self.frame_height,
            "uptime": time.time() - self.start_time
        }


class FaceRecognitionService:

    def __init__(self, known_students: Dict[str, StudentProfile]):
        self.known_students = known_students
        self.detection_confidence_threshold = 0.85
        self.recognition_confidence_threshold = 0.90

    def detect(self, frame: Dict[str, Any]) -> List[FaceData]:
        faces = []
        if frame["frame_id"] % 5 != 0:
            num_faces = (frame["frame_id"] % 3) + 1
            for i in range(num_faces):
                face = FaceData(
                    face_id=i,
                    confidence=random.uniform(0.88, 0.99),
                    location={"x": random.uniform(0.1, 0.9), "y": random.uniform(0.1, 0.8)},
                    features=[random.uniform(-1, 1) for _ in range(128)]
                )
                faces.append(face)
        return faces

    def identify(self, frame: Dict[str, Any]) -> List[str]:
        if frame["frame_id"] % 5 == 0:
            return []
        return [f"student_{(frame['frame_id'] % 3) + 1}"]

    def match_face(self, face_features: List[float], student_id: str) -> float:
        if student_id not in self.known_students:
            return 0.0
        known_features = self.known_students[student_id].known_features
        similarity = sum(1 for a, b in zip(face_features, known_features) if abs(a - b) < 0.1) / len(face_features)
        return min(similarity, 1.0)

    def get_confidence(self, face: FaceData) -> float:
        return face.confidence


class EyeTrackingService:

    def __init__(self):
        self.gaze_history: List[EyeGazeData] = []
        self.normal_gaze_threshold = 0.7

    def extract_gaze(self, frame: Dict[str, Any], face: FaceData) -> EyeGazeData:
        direction_choices = ["center", "left", "right", "up", "down"]
        direction = direction_choices[frame["frame_id"] % 5]
        confidence = random.uniform(0.7, 0.98)
        fixation_duration = random.uniform(0.1, 5.0)
        
        gaze = EyeGazeData(
            direction=direction,
            confidence=confidence,
            fixation_duration=fixation_duration
        )
        self.gaze_history.append(gaze)
        return gaze

    def is_looking_away(self, gaze: EyeGazeData) -> bool:
        return gaze.direction in ["left", "right", "down"] and gaze.confidence > 0.75

    def get_gaze_pattern(self, window_size: int = 10) -> Dict[str, float]:
        if len(self.gaze_history) < window_size:
            window = self.gaze_history
        else:
            window = self.gaze_history[-window_size:]
        
        counts = {}
        for gaze in window:
            counts[gaze.direction] = counts.get(gaze.direction, 0) + 1
        
        total = len(window)
        return {k: v / total for k, v in counts.items()}


class HeadPoseEstimator:

    def __init__(self):
        self.pose_history: List[HeadPoseData] = []
        self.normal_threshold = 15.0

    def estimate_pose(self, frame: Dict[str, Any], face: FaceData) -> HeadPoseData:
        pitch = random.uniform(-30, 30)
        yaw = random.uniform(-45, 45)
        roll = random.uniform(-20, 20)
        
        pose = HeadPoseData(pitch=pitch, yaw=yaw, roll=roll)
        self.pose_history.append(pose)
        return pose

    def is_unusual_pose(self, pose: HeadPoseData) -> bool:
        return (abs(pose.pitch) > self.normal_threshold or 
                abs(pose.yaw) > self.normal_threshold or 
                abs(pose.roll) > self.normal_threshold)

    def get_pose_stability(self, window_size: int = 15) -> float:
        if len(self.pose_history) < window_size:
            return 0.0
        
        window = self.pose_history[-window_size:]
        pitch_values = [p.pitch for p in window]
        yaw_values = [p.yaw for p in window]
        
        pitch_var = sum((x - sum(pitch_values) / len(pitch_values)) ** 2 for x in pitch_values) / len(pitch_values)
        yaw_var = sum((x - sum(yaw_values) / len(yaw_values)) ** 2 for x in yaw_values) / len(yaw_values)
        
        avg_variance = (pitch_var + yaw_var) / 2
        return 1.0 - min(avg_variance / 100, 1.0)


class BehaviorAnalysisService:

    def __init__(self):
        self.eye_tracker = EyeTrackingService()
        self.head_pose_estimator = HeadPoseEstimator()
        self.behavior_baseline = {}

    def analyze(self, frame: Dict[str, Any], student_ids: List[str], faces: List[FaceData]) -> DetectionResult:
        ts = time.time()
        
        if not student_ids:
            return DetectionResult(ts, "unknown", 0.2, ["no_face_detected"])

        sid = student_ids[0]
        score = 0.1 + (frame["frame_id"] % 7) * 0.12
        reasons = []

        if faces:
            gaze = self.eye_tracker.extract_gaze(frame, faces[0])
            if self.eye_tracker.is_looking_away(gaze):
                score += 0.15
                reasons.append("looking_away")
            
            pose = self.head_pose_estimator.estimate_pose(frame, faces[0])
            if self.head_pose_estimator.is_unusual_pose(pose):
                score += 0.10
                reasons.append("unusual_head_pose")

        if len(faces) > 1:
            score += 0.20
            reasons.append("multiple_people")

        if frame["frame_id"] % 11 == 0:
            reasons.append("rapid_movement")
            score += 0.05

        return DetectionResult(ts, sid, min(score, 1.0), reasons)


class AnomalyDetectionService:

    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.baseline_features: Dict[str, List[float]] = {}
        self.anomaly_scores: List[float] = []

    def compute_anomaly_score(self, current_features: List[float], student_id: str) -> float:
        if student_id not in self.baseline_features:
            self.baseline_features[student_id] = current_features
            return 0.0

        baseline = self.baseline_features[student_id]
        distance = sum((a - b) ** 2 for a, b in zip(current_features, baseline)) ** 0.5
        anomaly_score = min(distance * self.sensitivity, 1.0)
        self.anomaly_scores.append(anomaly_score)
        return anomaly_score

    def get_anomaly_trend(self, window_size: int = 20) -> float:
        if len(self.anomaly_scores) < window_size:
            return sum(self.anomaly_scores) / len(self.anomaly_scores) if self.anomaly_scores else 0.0
        
        window = self.anomaly_scores[-window_size:]
        return sum(window) / len(window)


class AlertingService:

    def __init__(self, high_threshold: float = 0.75, medium_threshold: float = 0.5):
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self.alerts: List[Dict[str, Any]] = []

    def generate_alert(self, result: DetectionResult) -> Optional[Dict[str, Any]]:
        if result.suspicion_score >= self.high_threshold:
            alert = {
                "level": "HIGH",
                "timestamp": result.timestamp,
                "student_id": result.student_id,
                "score": result.suspicion_score,
                "reasons": result.reasons
            }
            self.alerts.append(alert)
            return alert
        elif result.suspicion_score >= self.medium_threshold:
            alert = {
                "level": "MEDIUM",
                "timestamp": result.timestamp,
                "student_id": result.student_id,
                "score": result.suspicion_score,
                "reasons": result.reasons
            }
            self.alerts.append(alert)
            return alert
        return None

    def get_alert_summary(self) -> Dict[str, int]:
        summary = {"HIGH": 0, "MEDIUM": 0}
        for alert in self.alerts:
            summary[alert["level"]] += 1
        return summary


class ReportService:

    def __init__(self):
        self.records: List[DetectionResult] = []
        self.session_records: List[SessionRecord] = []
        self.current_session: Optional[SessionRecord] = None

    def start_session(self, session_id: str, student_id: str):
        self.current_session = SessionRecord(
            session_id=session_id,
            student_id=student_id,
            start_time=time.time(),
            end_time=None,
            total_frames=0,
            suspicious_frames=0,
            alerts=[],
            final_report=None
        )

    def add(self, result: DetectionResult):
        self.records.append(result)
        if self.current_session:
            self.current_session.total_frames += 1
            if result.suspicion_score > 0.5:
                self.current_session.suspicious_frames += 1
            if result.reasons:
                self.current_session.alerts.extend(result.reasons)
        
        print(f"[Report] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.timestamp))} - "
              f"{result.student_id} - score={result.suspicion_score:.2f} reasons={result.reasons}")

    def end_session(self):
        if self.current_session:
            self.current_session.end_time = time.time()
            duration = self.current_session.end_time - self.current_session.start_time
            suspicious_rate = (self.current_session.suspicious_frames / self.current_session.total_frames 
                             if self.current_session.total_frames > 0 else 0)
            
            self.current_session.final_report = {
                "duration": duration,
                "total_frames": self.current_session.total_frames,
                "suspicious_frames": self.current_session.suspicious_frames,
                "suspicious_rate": suspicious_rate,
                "unique_alerts": list(set(self.current_session.alerts))
            }
            self.session_records.append(self.current_session)
            self.current_session = None

    def get_report_summary(self) -> Dict[str, Any]:
        if not self.records:
            return {"total_records": 0}
        
        avg_score = sum(r.suspicion_score for r in self.records) / len(self.records)
        max_score = max(r.suspicion_score for r in self.records)
        high_risk_count = sum(1 for r in self.records if r.suspicion_score > 0.7)
        
        reason_counts = {}
        for record in self.records:
            for reason in record.reasons:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return {
            "total_records": len(self.records),
            "average_score": avg_score,
            "max_score": max_score,
            "high_risk_count": high_risk_count,
            "reason_distribution": reason_counts
        }


class ExamProctorSystem:

    def __init__(self, exam_id: str, num_students: int = 5):
        self.exam_id = exam_id
        self.num_students = num_students
        
        self.video_service = VideoCaptureService()
        self.known_students = {
            f"student_{i+1}": StudentProfile(
                student_id=f"student_{i+1}",
                enrollment_id=f"ENR{1000+i+1}",
                exam_id=exam_id,
                known_features=[random.uniform(-1, 1) for _ in range(128)],
                baseline_behavior={"gaze_pattern": "center-focused", "head_stability": 0.95},
                risk_level="low"
            ) for i in range(num_students)
        }
        
        self.face_recognition_service = FaceRecognitionService(self.known_students)
        self.behavior_analysis_service = BehaviorAnalysisService()
        self.anomaly_detection_service = AnomalyDetectionService()
        self.alerting_service = AlertingService()
        self.report_service = ReportService()
        self.system_start_time = time.time()

    def run_monitoring_frame(self) -> Optional[Dict[str, Any]]:
        frame = self.video_service.get_frame()
        faces = self.face_recognition_service.detect(frame)
        student_ids = self.face_recognition_service.identify(frame)
        result = self.behavior_analysis_service.analyze(frame, student_ids, faces)
        
        alert = self.alerting_service.generate_alert(result)
        
        self.report_service.add(result)
        
        anomaly_features = [random.uniform(-1, 1) for _ in range(10)]
        if student_ids:
            anomaly_score = self.anomaly_detection_service.compute_anomaly_score(
                anomaly_features, student_ids[0]
            )
        
        frame_result = {
            "frame_id": frame["frame_id"],
            "timestamp": frame["timestamp"],
            "faces_detected": len(faces),
            "students_identified": student_ids,
            "detection_result": result,
            "alert": alert,
            "frame_quality": frame["quality"]
        }
        
        return frame_result

    def run_monitoring_session(self, duration_seconds: int = 30):
        self.report_service.start_session(f"session_{self.exam_id}_{int(time.time())}", "monitored_students")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration_seconds:
            frame_result = self.run_monitoring_frame()
            frame_count += 1
            time.sleep(0.05)
        
        self.report_service.end_session()
        
        return {
            "session_id": f"session_{self.exam_id}_{int(start_time)}",
            "total_frames": frame_count,
            "duration": time.time() - start_time,
            "alert_summary": self.alerting_service.get_alert_summary(),
            "report_summary": self.report_service.get_report_summary()
        }

    def get_system_status(self) -> Dict[str, Any]:
        uptime = time.time() - self.system_start_time
        return {
            "exam_id": self.exam_id,
            "uptime": uptime,
            "total_records": len(self.report_service.records),
            "video_metadata": self.video_service.get_metadata(),
            "alert_summary": self.alerting_service.get_alert_summary(),
            "known_students": list(self.known_students.keys())
        }


def run_demo_loop(iterations: int = 20):
    video = VideoCaptureService()
    face = FaceRecognitionService(known_students={
        "student_1": StudentProfile("student_1", "ENR1001", "EXAM001", 
                                   [random.uniform(-1, 1) for _ in range(128)],
                                   {}, "low"),
        "student_2": StudentProfile("student_2", "ENR1002", "EXAM001",
                                   [random.uniform(-1, 1) for _ in range(128)],
                                   {}, "low"),
        "student_3": StudentProfile("student_3", "ENR1003", "EXAM001",
                                   [random.uniform(-1, 1) for _ in range(128)],
                                   {}, "low")
    })
    behavior = BehaviorAnalysisService()
    report = ReportService()

    for _ in range(iterations):
        frame = video.get_frame()
        faces = face.detect(frame)
        ids = face.identify(frame)
        result = behavior.analyze(frame, ids, faces)
        report.add(result)
        time.sleep(0.05)


def run_full_system_demo():
    system = ExamProctorSystem(exam_id="EXAM_2024_001", num_students=3)
    
    print("\n" + "="*60)
    print("NeuroProctor - Exam Proctoring System Demo")
    print("="*60)
    
    print("\nStarting monitoring session...")
    session_result = system.run_monitoring_session(duration_seconds=15)
    
    print("\nSession Results:")
    print(json.dumps(session_result, indent=2, default=str))
    
    print("\nSystem Status:")
    status = system.get_system_status()
    print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    run_demo_loop(30)
    print("\n")
    run_full_system_demo()
