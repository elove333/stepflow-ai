#!/usr/bin/env python3
"""Example script demonstrating how to use the StepFlow AI service."""
import requests
import json
import time


def test_basic_motion():
    """Test basic motion prediction."""
    print("Testing basic motion prediction...")
    
    motion_data = {
        "frames": [
            {
                "timestamp": i * 0.033,
                "keypoints": [
                    {"x": 0.5 + i * 0.01, "y": 0.5 + i * 0.01, "confidence": 0.9},
                    {"x": 0.4 - i * 0.01, "y": 0.6 + i * 0.01, "confidence": 0.85}
                ]
            }
            for i in range(10)
        ],
        "audio_bpm": 120.0
    }
    
    response = requests.post(
        "http://localhost:8000/predict",
        json=motion_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Overall Score: {result['overall_score']:.2f}/100")
        print(f"✓ Timing Sync: {result['timing_metrics']['sync_score']:.2%}")
        print(f"✓ Smoothness: {result['movement_metrics']['smoothness_score']:.2%}")
        print(f"✓ Processing Time: {result['processing_time_ms']:.2f}ms")
        print(f"✓ Feedback ({len(result['feedback'])} items):")
        for item in result['feedback']:
            print(f"  - [{item['category']}] {item['message']}")
    else:
        print(f"✗ Error: {response.status_code} - {response.text}")


def test_high_energy_motion():
    """Test high-energy motion prediction."""
    print("\nTesting high-energy motion...")
    
    motion_data = {
        "frames": [
            {
                "timestamp": i * 0.033,
                "keypoints": [
                    {"x": 0.5 + i * 0.05, "y": 0.5 + i * 0.05, "confidence": 0.9}
                ]
            }
            for i in range(20)
        ]
    }
    
    response = requests.post(
        "http://localhost:8000/predict",
        json=motion_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Energy Score: {result['movement_metrics']['energy_score']:.2%}")
        print(f"✓ Overall Score: {result['overall_score']:.2f}/100")
    else:
        print(f"✗ Error: {response.status_code}")


def test_performance():
    """Test service performance with longer sequence."""
    print("\nTesting performance with 3-second motion sequence...")
    
    motion_data = {
        "frames": [
            {
                "timestamp": i * 0.033,
                "keypoints": [
                    {"x": 0.5 + (i % 20) * 0.01, "y": 0.5 + (i % 20) * 0.01, "confidence": 0.9}
                    for j in range(17)  # Full body keypoints
                ]
            }
            for i in range(90)  # 3 seconds at 30fps
        ],
        "audio_bpm": 128.0
    }
    
    start = time.time()
    response = requests.post(
        "http://localhost:8000/predict",
        json=motion_data
    )
    end = time.time()
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Frames processed: {len(motion_data['frames'])}")
        print(f"✓ Keypoints per frame: 17")
        print(f"✓ Server processing time: {result['processing_time_ms']:.2f}ms")
        print(f"✓ Total request time: {(end - start) * 1000:.2f}ms")
        print(f"✓ Overall Score: {result['overall_score']:.2f}/100")
    else:
        print(f"✗ Error: {response.status_code}")


def check_health():
    """Check service health."""
    print("Checking service health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service is healthy")
            print(f"✓ Version: {data['version']}")
            return True
        else:
            print(f"✗ Service returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to service: {e}")
        print("  Make sure the service is running: python main.py")
        return False


if __name__ == "__main__":
    print("StepFlow AI Service Example\n" + "=" * 50)
    
    # Check if service is running
    if not check_health():
        exit(1)
    
    print()
    
    # Run tests
    test_basic_motion()
    test_high_energy_motion()
    test_performance()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
