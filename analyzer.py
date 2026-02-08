"""Motion analysis and scoring algorithms."""
import numpy as np
from typing import List, Tuple
from models import MotionData, Frame, KeyPoint, TimingMetrics, MovementMetrics, FeedbackItem


class MotionAnalyzer:
    """Analyzes motion data and generates predictions."""
    
    def __init__(self, scoring_threshold: float = 0.7):
        self.scoring_threshold = scoring_threshold
    
    def analyze(self, motion_data: MotionData) -> Tuple[TimingMetrics, MovementMetrics, List[FeedbackItem]]:
        """
        Analyze motion data and generate metrics and feedback.
        
        Args:
            motion_data: Input motion data
            
        Returns:
            Tuple of (timing_metrics, movement_metrics, feedback)
        """
        # Extract timing metrics
        timing_metrics = self._analyze_timing(motion_data)
        
        # Analyze movement quality
        movement_metrics = self._analyze_movement(motion_data)
        
        # Generate coaching feedback
        feedback = self._generate_feedback(timing_metrics, movement_metrics, motion_data)
        
        return timing_metrics, movement_metrics, feedback
    
    def _analyze_timing(self, motion_data: MotionData) -> TimingMetrics:
        """Analyze timing and synchronization with music."""
        frames = motion_data.frames
        
        if motion_data.audio_bpm:
            # Calculate beat interval
            beat_interval = 60.0 / motion_data.audio_bpm
            
            # Analyze movement peaks vs beats
            velocities = self._calculate_velocities(frames)
            peaks = self._detect_movement_peaks(velocities)
            
            # Calculate synchronization
            on_beat_count = 0
            total_peaks = len(peaks)
            lag_sum = 0.0
            
            for peak_time in peaks:
                # Find nearest beat
                nearest_beat = round(peak_time / beat_interval) * beat_interval
                lag = abs(peak_time - nearest_beat)
                lag_sum += lag
                
                # Consider "on beat" if within 100ms of beat
                if lag < 0.1:
                    on_beat_count += 1
            
            avg_lag_ms = (lag_sum / max(total_peaks, 1)) * 1000
            on_beat_percentage = (on_beat_count / max(total_peaks, 1)) * 100
            sync_score = 1.0 - min(avg_lag_ms / 200, 1.0)  # Normalize to 0-1
        else:
            # No BPM provided, use default values
            avg_lag_ms = 0.0
            on_beat_percentage = 100.0
            sync_score = 1.0
        
        return TimingMetrics(
            avg_lag_ms=avg_lag_ms,
            sync_score=sync_score,
            on_beat_percentage=on_beat_percentage
        )
    
    def _analyze_movement(self, motion_data: MotionData) -> MovementMetrics:
        """Analyze movement quality metrics."""
        frames = motion_data.frames
        
        # Calculate velocities and accelerations
        velocities = self._calculate_velocities(frames)
        accelerations = self._calculate_accelerations(velocities)
        
        # Smoothness: low variance in acceleration indicates smooth movement
        smoothness_score = self._calculate_smoothness(accelerations)
        
        # Energy: average velocity magnitude
        energy_score = self._calculate_energy(velocities)
        
        # Accuracy: consistency in movement patterns
        accuracy_score = self._calculate_accuracy(frames)
        
        # Form: posture and alignment quality
        form_score = self._calculate_form(frames)
        
        return MovementMetrics(
            smoothness_score=smoothness_score,
            accuracy_score=accuracy_score,
            energy_score=energy_score,
            form_score=form_score
        )
    
    def _generate_feedback(
        self, 
        timing_metrics: TimingMetrics, 
        movement_metrics: MovementMetrics,
        motion_data: MotionData
    ) -> List[FeedbackItem]:
        """Generate coaching feedback based on analysis."""
        feedback = []
        
        # Timing feedback
        if timing_metrics.sync_score < 0.7:
            feedback.append(FeedbackItem(
                category="timing",
                message=f"Your timing is off. Try to sync your movements with the beat. "
                       f"You're hitting {timing_metrics.on_beat_percentage:.1f}% of beats on time.",
                severity="warning",
                timestamp=None
            ))
        elif timing_metrics.sync_score >= 0.9:
            feedback.append(FeedbackItem(
                category="timing",
                message="Excellent timing! You're perfectly synced with the music.",
                severity="info",
                timestamp=None
            ))
        
        # Smoothness feedback
        if movement_metrics.smoothness_score < 0.6:
            feedback.append(FeedbackItem(
                category="form",
                message="Your movements are a bit jerky. Focus on flowing smoothly between positions.",
                severity="warning",
                timestamp=None
            ))
        
        # Energy feedback
        if movement_metrics.energy_score < 0.5:
            feedback.append(FeedbackItem(
                category="energy",
                message="Put more energy into your movements! Go bigger and stronger.",
                severity="info",
                timestamp=None
            ))
        elif movement_metrics.energy_score > 0.9:
            feedback.append(FeedbackItem(
                category="energy",
                message="Great energy! Keep up that intensity.",
                severity="info",
                timestamp=None
            ))
        
        # Form feedback
        if movement_metrics.form_score < 0.7:
            feedback.append(FeedbackItem(
                category="form",
                message="Pay attention to your posture and alignment. Keep your core engaged.",
                severity="warning",
                timestamp=None
            ))
        
        # Accuracy feedback
        if movement_metrics.accuracy_score < 0.7:
            feedback.append(FeedbackItem(
                category="accuracy",
                message="Your movements are inconsistent. Try to replicate the reference motion more precisely.",
                severity="warning",
                timestamp=None
            ))
        
        # Overall positive feedback if no issues
        if not feedback:
            feedback.append(FeedbackItem(
                category="overall",
                message="Outstanding performance! All metrics look great.",
                severity="info",
                timestamp=None
            ))
        
        return feedback
    
    def _calculate_velocities(self, frames: List[Frame]) -> np.ndarray:
        """Calculate velocities between frames."""
        if len(frames) < 2:
            return np.array([0.0])
        
        velocities = []
        for i in range(1, len(frames)):
            dt = frames[i].timestamp - frames[i-1].timestamp
            if dt <= 0:
                dt = 0.033  # Default to ~30fps
            
            # Calculate average keypoint displacement
            displacement = 0.0
            count = 0
            for j, kp_curr in enumerate(frames[i].keypoints):
                if j < len(frames[i-1].keypoints):
                    kp_prev = frames[i-1].keypoints[j]
                    dx = kp_curr.x - kp_prev.x
                    dy = kp_curr.y - kp_prev.y
                    dz = (kp_curr.z or 0) - (kp_prev.z or 0)
                    displacement += np.sqrt(dx**2 + dy**2 + dz**2)
                    count += 1
            
            avg_displacement = displacement / max(count, 1)
            velocity = avg_displacement / dt
            velocities.append(velocity)
        
        return np.array(velocities)
    
    def _calculate_accelerations(self, velocities: np.ndarray) -> np.ndarray:
        """Calculate accelerations from velocities."""
        if len(velocities) < 2:
            return np.array([0.0])
        return np.diff(velocities)
    
    def _detect_movement_peaks(self, velocities: np.ndarray, threshold_percentile: float = 75) -> List[float]:
        """Detect peaks in movement velocity."""
        if len(velocities) < 3:
            return []
        
        threshold = np.percentile(velocities, threshold_percentile)
        peaks = []
        
        for i in range(1, len(velocities) - 1):
            if velocities[i] > threshold and velocities[i] > velocities[i-1] and velocities[i] > velocities[i+1]:
                # Approximate timestamp based on frame index
                peaks.append(i * 0.033)  # Assume 30fps
        
        return peaks
    
    def _calculate_smoothness(self, accelerations: np.ndarray) -> float:
        """Calculate smoothness score (0-1, higher is smoother)."""
        if len(accelerations) == 0:
            return 1.0
        
        # Lower variance in acceleration = smoother movement
        variance = np.var(accelerations)
        # Normalize: assume variance > 100 is very jerky
        smoothness = 1.0 / (1.0 + variance / 100.0)
        return float(np.clip(smoothness, 0.0, 1.0))
    
    def _calculate_energy(self, velocities: np.ndarray) -> float:
        """Calculate energy score (0-1)."""
        if len(velocities) == 0:
            return 0.5
        
        avg_velocity = np.mean(velocities)
        # Normalize: assume velocity > 10 is high energy
        energy = avg_velocity / 10.0
        return float(np.clip(energy, 0.0, 1.0))
    
    def _calculate_accuracy(self, frames: List[Frame]) -> float:
        """Calculate accuracy score based on consistency."""
        if len(frames) < 2:
            return 1.0
        
        # Calculate consistency in keypoint positions relative to body center
        consistency_scores = []
        
        for i in range(len(frames)):
            keypoints = frames[i].keypoints
            if len(keypoints) == 0:
                continue
            
            # Calculate body center
            center_x = np.mean([kp.x for kp in keypoints])
            center_y = np.mean([kp.y for kp in keypoints])
            
            # Calculate normalized distances
            distances = []
            for kp in keypoints:
                dist = np.sqrt((kp.x - center_x)**2 + (kp.y - center_y)**2)
                distances.append(dist)
            
            if distances:
                consistency_scores.append(np.std(distances))
        
        if not consistency_scores:
            return 1.0
        
        # Lower variation in body structure = higher accuracy
        avg_std = np.mean(consistency_scores)
        accuracy = 1.0 / (1.0 + avg_std)
        return float(np.clip(accuracy, 0.0, 1.0))
    
    def _calculate_form(self, frames: List[Frame]) -> float:
        """Calculate form score based on posture quality."""
        if len(frames) == 0:
            return 1.0
        
        form_scores = []
        
        for frame in frames:
            keypoints = frame.keypoints
            if len(keypoints) == 0:
                continue
            
            # Check confidence levels (proxy for detection quality)
            confidences = [kp.confidence for kp in keypoints if kp.confidence is not None]
            if confidences:
                avg_confidence = np.mean(confidences)
                form_scores.append(avg_confidence)
        
        if not form_scores:
            # If no confidence data, use a heuristic based on keypoint spread
            return 0.8
        
        return float(np.clip(np.mean(form_scores), 0.0, 1.0))
    
    def calculate_overall_score(
        self, 
        timing_metrics: TimingMetrics, 
        movement_metrics: MovementMetrics
    ) -> float:
        """Calculate overall performance score (0-100)."""
        # Weighted combination of metrics
        weights = {
            'timing': 0.25,
            'smoothness': 0.20,
            'accuracy': 0.25,
            'energy': 0.15,
            'form': 0.15
        }
        
        score = (
            weights['timing'] * timing_metrics.sync_score +
            weights['smoothness'] * movement_metrics.smoothness_score +
            weights['accuracy'] * movement_metrics.accuracy_score +
            weights['energy'] * movement_metrics.energy_score +
            weights['form'] * movement_metrics.form_score
        ) * 100.0
        
        return float(np.clip(score, 0.0, 100.0))
