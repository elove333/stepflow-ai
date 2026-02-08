# StepFlow AI Service

AI/ML pipeline for STEPFLOW, providing motion data analysis, scoring, and coaching feedback through a REST API.

## Features

- **Motion Analysis**: Process motion capture data (pose keypoints) to evaluate performance
- **Beat Alignment**: Synchronize movement with music tempo (BPM)
- **Timing Analysis**: Measure lag and synchronization accuracy
- **Movement Scoring**: Evaluate smoothness, accuracy, energy, and form
- **Coaching Feedback**: Generate actionable feedback based on performance metrics
- **Low Latency**: Optimized for real-time user interactions
- **Configurable**: Environment-based configuration for deployment flexibility

## API Endpoints

### POST /predict

Analyze motion data and return predictions.

**Request Body:**
```json
{
  "frames": [
    {
      "timestamp": 0.0,
      "keypoints": [
        {
          "x": 0.5,
          "y": 0.5,
          "z": 0.0,
          "confidence": 0.9
        }
      ]
    }
  ],
  "audio_bpm": 120.0,
  "reference_motion": "dance_move_123"
}
```

**Response:**
```json
{
  "overall_score": 85.5,
  "timing_metrics": {
    "avg_lag_ms": 45.2,
    "sync_score": 0.87,
    "on_beat_percentage": 82.5
  },
  "movement_metrics": {
    "smoothness_score": 0.91,
    "accuracy_score": 0.83,
    "energy_score": 0.79,
    "form_score": 0.88
  },
  "feedback": [
    {
      "category": "timing",
      "message": "Great timing! Keep it up.",
      "severity": "info",
      "timestamp": null
    }
  ],
  "processing_time_ms": 25.3
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "stepflow-ai",
  "version": "1.0.0"
}
```

### GET /

Service information endpoint.

**Response:**
```json
{
  "service": "StepFlow AI",
  "version": "1.0.0",
  "status": "running"
}
```

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/elove333/stepflow-ai.git
cd stepflow-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the service:
```bash
python main.py
```

The service will start on `http://localhost:8000`.

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up -d
```

2. Or build and run manually:
```bash
docker build -t stepflow-ai .
docker run -p 8000:8000 stepflow-ai
```

## Configuration

Configure the service via environment variables or `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `AI_SERVICE_URL` | Service URL for backend integration | `http://localhost:8000` |
| `MODEL_VERSION` | Model version identifier | `1.0.0` |
| `SCORING_THRESHOLD` | Minimum score threshold | `0.7` |
| `MAX_WORKERS` | Maximum worker threads | `4` |
| `TIMEOUT_SECONDS` | Request timeout | `5` |

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Usage Examples

### Python Client

```python
import requests

# Motion data
motion_data = {
    "frames": [
        {
            "timestamp": 0.0,
            "keypoints": [
                {"x": 0.5, "y": 0.5, "confidence": 0.9}
            ]
        },
        {
            "timestamp": 0.033,
            "keypoints": [
                {"x": 0.52, "y": 0.52, "confidence": 0.91}
            ]
        }
    ],
    "audio_bpm": 120.0
}

# Make prediction
response = requests.post(
    "http://localhost:8000/predict",
    json=motion_data
)

result = response.json()
print(f"Overall Score: {result['overall_score']}")
print(f"Feedback: {result['feedback']}")
```

### cURL

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "frames": [
      {
        "timestamp": 0.0,
        "keypoints": [
          {"x": 0.5, "y": 0.5, "confidence": 0.9}
        ]
      }
    ],
    "audio_bpm": 120.0
  }'
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const motionData = {
  frames: [
    {
      timestamp: 0.0,
      keypoints: [
        { x: 0.5, y: 0.5, confidence: 0.9 }
      ]
    }
  ],
  audio_bpm: 120.0
};

axios.post('http://localhost:8000/predict', motionData)
  .then(response => {
    console.log('Overall Score:', response.data.overall_score);
    console.log('Feedback:', response.data.feedback);
  });
```

## Motion Data Format

### Keypoint Format

Each keypoint represents a body joint position:

- `x`: X coordinate (normalized 0-1 or pixel coordinates)
- `y`: Y coordinate (normalized 0-1 or pixel coordinates)
- `z`: (Optional) Z coordinate for 3D depth
- `confidence`: (Optional) Detection confidence (0-1)

### Frame Format

Each frame represents a snapshot in time:

- `timestamp`: Time in seconds from start
- `keypoints`: Array of keypoint objects

### Complete Motion Data

- `frames`: Array of frame objects (required)
- `audio_bpm`: (Optional) Music tempo in beats per minute
- `reference_motion`: (Optional) Reference motion ID for comparison

## Metrics Explained

### Overall Score (0-100)
Weighted combination of all metrics representing overall performance quality.

### Timing Metrics
- **avg_lag_ms**: Average delay between movement and beat (milliseconds)
- **sync_score**: How well movements align with music (0-1)
- **on_beat_percentage**: Percentage of movements hitting the beat

### Movement Metrics
- **smoothness_score**: How fluid and continuous the movement is (0-1)
- **accuracy_score**: Consistency and precision of movement patterns (0-1)
- **energy_score**: Intensity and amplitude of movements (0-1)
- **form_score**: Posture and alignment quality (0-1)

## Performance Optimization

The service is optimized for low latency:

- Async processing with FastAPI
- Efficient numpy-based calculations
- Minimal external dependencies
- Sub-second response times for typical inputs

Typical processing times:
- 30 frames (1 sec @ 30fps): ~25-50ms
- 90 frames (3 sec @ 30fps): ~50-100ms
- 300 frames (10 sec @ 30fps): ~150-300ms

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
         ├──────────┐
         │          │
    ┌────▼─────┐ ┌─▼──────────┐
    │ Models   │ │  Analyzer  │
    │ (models) │ │ (analyzer) │
    └──────────┘ └────────────┘
         │            │
         └──────┬─────┘
                │
         ┌──────▼──────┐
         │ Config      │
         │ (config)    │
         └─────────────┘
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use production-appropriate values
2. **CORS**: Configure `allow_origins` in `main.py` for your domain
3. **Health Checks**: Use `/health` endpoint for load balancer checks
4. **Scaling**: Deploy multiple instances behind a load balancer
5. **Monitoring**: Add logging and metrics collection
6. **Security**: Use HTTPS, API authentication, rate limiting

### Cloud Deployment

The service can be deployed to:
- AWS (ECS, EKS, Lambda with API Gateway)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- Heroku, Railway, Render, etc.

Example for Cloud Run:
```bash
gcloud run deploy stepflow-ai \
  --image gcr.io/PROJECT_ID/stepflow-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: https://github.com/elove333/stepflow-ai/issues
- Documentation: This README

## Version History

- **1.0.0** (2026-02): Initial release
  - Motion analysis with pose keypoints
  - Beat alignment and timing metrics
  - Movement quality scoring
  - Coaching feedback generation
  - REST API with /predict endpoint
  - Docker deployment support
