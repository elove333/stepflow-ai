# stepflow-ai
AI/ML pipeline for STEPFLOW, including pose estimation, beat alignment, timing analysis, movement scoring, and coaching feedback generation.

## Features

- **REST API**: `/predict` endpoint for motion data analysis
- **Motion Analysis**: Process pose keypoints to evaluate performance  
- **Beat Alignment**: Synchronize movements with music tempo (BPM)
- **Real-time Feedback**: Generate coaching feedback with sub-second latency
- **Comprehensive Metrics**: Timing, smoothness, accuracy, energy, and form scoring
- **Flexible Deployment**: Docker support with configurable environment

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py
```

Service runs on `http://localhost:8000` by default.

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed usage instructions.
