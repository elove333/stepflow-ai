"""Test suite for the AI service."""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import MotionData, Frame, KeyPoint


# Test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["service"] == "StepFlow AI"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPredictEndpoint:
    """Test /predict endpoint with various scenarios."""
    
    def test_predict_basic_motion(self):
        """Test basic motion data prediction."""
        # Create simple motion data with 5 frames
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [
                        {"x": 0.5, "y": 0.5, "z": 0.0, "confidence": 0.9},
                        {"x": 0.6, "y": 0.4, "z": 0.0, "confidence": 0.85}
                    ]
                },
                {
                    "timestamp": 0.033,
                    "keypoints": [
                        {"x": 0.52, "y": 0.52, "z": 0.0, "confidence": 0.92},
                        {"x": 0.62, "y": 0.42, "z": 0.0, "confidence": 0.88}
                    ]
                },
                {
                    "timestamp": 0.066,
                    "keypoints": [
                        {"x": 0.54, "y": 0.54, "z": 0.0, "confidence": 0.91},
                        {"x": 0.64, "y": 0.44, "z": 0.0, "confidence": 0.87}
                    ]
                },
                {
                    "timestamp": 0.099,
                    "keypoints": [
                        {"x": 0.56, "y": 0.56, "z": 0.0, "confidence": 0.90},
                        {"x": 0.66, "y": 0.46, "z": 0.0, "confidence": 0.86}
                    ]
                },
                {
                    "timestamp": 0.132,
                    "keypoints": [
                        {"x": 0.58, "y": 0.58, "z": 0.0, "confidence": 0.89},
                        {"x": 0.68, "y": 0.48, "z": 0.0, "confidence": 0.85}
                    ]
                }
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "overall_score" in result
        assert "timing_metrics" in result
        assert "movement_metrics" in result
        assert "feedback" in result
        assert "processing_time_ms" in result
        
        # Validate score range
        assert 0 <= result["overall_score"] <= 100
        
        # Validate timing metrics
        timing = result["timing_metrics"]
        assert 0 <= timing["sync_score"] <= 1
        assert 0 <= timing["on_beat_percentage"] <= 100
        
        # Validate movement metrics
        movement = result["movement_metrics"]
        assert 0 <= movement["smoothness_score"] <= 1
        assert 0 <= movement["accuracy_score"] <= 1
        assert 0 <= movement["energy_score"] <= 1
        assert 0 <= movement["form_score"] <= 1
        
        # Validate feedback
        assert isinstance(result["feedback"], list)
        assert len(result["feedback"]) > 0
        
        # Validate processing time
        assert result["processing_time_ms"] > 0
    
    def test_predict_with_bpm(self):
        """Test motion prediction with BPM for beat alignment."""
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [{"x": 0.5, "y": 0.5, "confidence": 0.9}]
                },
                {
                    "timestamp": 0.5,
                    "keypoints": [{"x": 0.6, "y": 0.6, "confidence": 0.9}]
                },
                {
                    "timestamp": 1.0,
                    "keypoints": [{"x": 0.5, "y": 0.5, "confidence": 0.9}]
                },
                {
                    "timestamp": 1.5,
                    "keypoints": [{"x": 0.6, "y": 0.6, "confidence": 0.9}]
                }
            ],
            "audio_bpm": 120.0
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["timing_metrics"]["avg_lag_ms"] >= 0
    
    def test_predict_high_energy_motion(self):
        """Test prediction with high-energy motion."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + i * 0.1, "y": 0.5 + i * 0.1, "confidence": 0.9},
                        {"x": 0.3 - i * 0.05, "y": 0.7 + i * 0.05, "confidence": 0.85}
                    ]
                }
                for i in range(10)
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        # High energy motion should have higher energy score
        assert result["movement_metrics"]["energy_score"] > 0.3
    
    def test_predict_smooth_motion(self):
        """Test prediction with smooth, consistent motion."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + i * 0.01, "y": 0.5 + i * 0.01, "confidence": 0.95},
                        {"x": 0.6 + i * 0.01, "y": 0.4 + i * 0.01, "confidence": 0.95}
                    ]
                }
                for i in range(20)
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        # Smooth motion should have high smoothness score
        assert result["movement_metrics"]["smoothness_score"] > 0.5
    
    def test_predict_jerky_motion(self):
        """Test prediction with jerky, inconsistent motion."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + ((-1) ** i) * 0.2, "y": 0.5 + ((-1) ** i) * 0.2, "confidence": 0.8}
                    ]
                }
                for i in range(10)
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        # Jerky motion should have smoothness score in valid range
        assert 0.0 <= result["movement_metrics"]["smoothness_score"] <= 1.0
    
    def test_predict_empty_frames(self):
        """Test prediction with empty frames list."""
        motion_data = {"frames": []}
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 422  # Validation error
    
    def test_predict_single_frame(self):
        """Test prediction with single frame."""
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [{"x": 0.5, "y": 0.5, "confidence": 0.9}]
                }
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["overall_score"] >= 0
    
    def test_predict_missing_confidence(self):
        """Test prediction with keypoints missing confidence values."""
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [{"x": 0.5, "y": 0.5}]
                },
                {
                    "timestamp": 0.033,
                    "keypoints": [{"x": 0.52, "y": 0.52}]
                }
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
    
    def test_predict_2d_keypoints(self):
        """Test prediction with 2D keypoints (no z coordinate)."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + i * 0.01, "y": 0.5 + i * 0.01, "confidence": 0.9}
                    ]
                }
                for i in range(5)
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
    
    def test_predict_3d_keypoints(self):
        """Test prediction with 3D keypoints."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + i * 0.01, "y": 0.5 + i * 0.01, "z": 1.0 + i * 0.01, "confidence": 0.9}
                    ]
                }
                for i in range(5)
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
    
    def test_predict_multiple_keypoints_per_frame(self):
        """Test prediction with multiple keypoints per frame (full body)."""
        # Simulate 17 keypoints (typical pose estimation output)
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [
                        {"x": 0.5 + j * 0.05, "y": 0.5 + j * 0.03, "confidence": 0.9}
                        for j in range(17)
                    ]
                },
                {
                    "timestamp": 0.033,
                    "keypoints": [
                        {"x": 0.5 + j * 0.05 + 0.01, "y": 0.5 + j * 0.03 + 0.01, "confidence": 0.9}
                        for j in range(17)
                    ]
                }
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["overall_score"] >= 0
    
    def test_predict_latency(self):
        """Test that prediction is fast (< 1 second for typical input)."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + i * 0.01, "y": 0.5 + i * 0.01, "confidence": 0.9}
                        for _ in range(17)
                    ]
                }
                for i in range(30)  # 1 second of motion at 30fps
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        # Processing should be fast for live interactions
        assert result["processing_time_ms"] < 1000  # Less than 1 second
    
    def test_predict_long_sequence(self):
        """Test prediction with longer motion sequence."""
        motion_data = {
            "frames": [
                {
                    "timestamp": i * 0.033,
                    "keypoints": [
                        {"x": 0.5 + (i % 20) * 0.01, "y": 0.5 + (i % 20) * 0.01, "confidence": 0.9}
                    ]
                }
                for i in range(100)  # ~3 seconds
            ],
            "audio_bpm": 128.0
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        assert 0 <= result["overall_score"] <= 100


class TestFeedbackGeneration:
    """Test feedback generation logic."""
    
    def test_feedback_contains_required_fields(self):
        """Test that feedback items have required fields."""
        motion_data = {
            "frames": [
                {
                    "timestamp": 0.0,
                    "keypoints": [{"x": 0.5, "y": 0.5, "confidence": 0.9}]
                }
            ]
        }
        
        response = client.post("/predict", json=motion_data)
        assert response.status_code == 200
        
        result = response.json()
        for feedback_item in result["feedback"]:
            assert "category" in feedback_item
            assert "message" in feedback_item
            assert "severity" in feedback_item
            assert feedback_item["severity"] in ["info", "warning", "critical"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
