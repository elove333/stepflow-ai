"""Data models for the AI service."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class KeyPoint(BaseModel):
    """3D keypoint representing a body joint."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: Optional[float] = Field(None, description="Z coordinate (depth)")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Detection confidence")


class Frame(BaseModel):
    """Single frame of motion data."""
    timestamp: float = Field(..., description="Timestamp in seconds")
    keypoints: List[KeyPoint] = Field(..., description="Body keypoints for this frame")
    
    @field_validator('keypoints')
    @classmethod
    def validate_keypoints(cls, v):
        if len(v) == 0:
            raise ValueError("Frame must contain at least one keypoint")
        return v


class MotionData(BaseModel):
    """Input motion data for prediction."""
    frames: List[Frame] = Field(..., description="Sequence of motion frames")
    audio_bpm: Optional[float] = Field(None, gt=0, description="Music tempo in BPM")
    reference_motion: Optional[str] = Field(None, description="Reference motion ID for comparison")
    
    @field_validator('frames')
    @classmethod
    def validate_frames(cls, v):
        if len(v) == 0:
            raise ValueError("Motion data must contain at least one frame")
        return v


class TimingMetrics(BaseModel):
    """Timing analysis results."""
    avg_lag_ms: float = Field(..., description="Average lag in milliseconds")
    sync_score: float = Field(..., ge=0.0, le=1.0, description="Synchronization score")
    on_beat_percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of moves on beat")


class MovementMetrics(BaseModel):
    """Movement quality metrics."""
    smoothness_score: float = Field(..., ge=0.0, le=1.0, description="Movement smoothness")
    accuracy_score: float = Field(..., ge=0.0, le=1.0, description="Movement accuracy")
    energy_score: float = Field(..., ge=0.0, le=1.0, description="Movement energy/intensity")
    form_score: float = Field(..., ge=0.0, le=1.0, description="Movement form quality")


class FeedbackItem(BaseModel):
    """Individual feedback item."""
    category: str = Field(..., description="Feedback category (e.g., timing, form, energy)")
    message: str = Field(..., description="Feedback message")
    severity: str = Field(..., description="Severity level: info, warning, critical")
    timestamp: Optional[float] = Field(None, description="Timestamp where issue occurs")


class PredictionResult(BaseModel):
    """Prediction result returned by the AI service."""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall performance score")
    timing_metrics: TimingMetrics = Field(..., description="Timing analysis results")
    movement_metrics: MovementMetrics = Field(..., description="Movement quality metrics")
    feedback: List[FeedbackItem] = Field(..., description="Coaching feedback items")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
