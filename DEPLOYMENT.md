# Deployment Guide

This guide explains how to deploy the StepFlow AI service in different environments.

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/elove333/stepflow-ai.git
cd stepflow-ai

# Install dependencies
pip install -r requirements.txt

# Create environment file (optional)
cp .env.example .env
# Edit .env with your configuration

# Run the service
python main.py
```

The service will start on http://localhost:8000.

### Test the service
```bash
# Run tests
pytest tests/ -v

# Or use the example script
python example.py
```

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose (optional)

### Build and Run

#### Using Docker Compose (Recommended)
```bash
# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop the service
docker-compose down
```

#### Using Docker directly
```bash
# Build the image
docker build -t stepflow-ai .

# Run the container
docker run -d -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  --name stepflow-ai \
  stepflow-ai

# Check logs
docker logs -f stepflow-ai

# Stop the container
docker stop stepflow-ai
docker rm stepflow-ai
```

## Cloud Deployment

### AWS ECS

1. **Build and push Docker image to ECR:**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and tag
docker build -t stepflow-ai .
docker tag stepflow-ai:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/stepflow-ai:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/stepflow-ai:latest
```

2. **Create ECS task definition:**
```json
{
  "family": "stepflow-ai",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "stepflow-ai",
      "image": "YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/stepflow-ai:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "HOST", "value": "0.0.0.0"},
        {"name": "PORT", "value": "8000"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 5
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```

3. **Create ECS service with Application Load Balancer**

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/stepflow-ai
gcloud run deploy stepflow-ai \
  --image gcr.io/PROJECT_ID/stepflow-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars HOST=0.0.0.0,PORT=8000
```

### Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name stepflow-rg --location eastus

# Create container registry
az acr create --resource-group stepflow-rg --name stepflowregistry --sku Basic

# Build and push
az acr build --registry stepflowregistry --image stepflow-ai:latest .

# Deploy container
az container create \
  --resource-group stepflow-rg \
  --name stepflow-ai \
  --image stepflowregistry.azurecr.io/stepflow-ai:latest \
  --dns-name-label stepflow-ai \
  --ports 8000 \
  --environment-variables HOST=0.0.0.0 PORT=8000
```

### Heroku

```bash
# Login to Heroku
heroku login
heroku container:login

# Create app
heroku create stepflow-ai

# Build and push
heroku container:push web --app stepflow-ai
heroku container:release web --app stepflow-ai

# Open app
heroku open --app stepflow-ai
```

## Kubernetes

### Deploy to Kubernetes

1. **Create deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stepflow-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: stepflow-ai
  template:
    metadata:
      labels:
        app: stepflow-ai
    spec:
      containers:
      - name: stepflow-ai
        image: YOUR_REGISTRY/stepflow-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: HOST
          value: "0.0.0.0"
        - name: PORT
          value: "8000"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: stepflow-ai-service
spec:
  selector:
    app: stepflow-ai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

2. **Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get services stepflow-ai-service
```

## Configuration

### Environment Variables

Set these environment variables for your deployment:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `AI_SERVICE_URL` | Service URL for backend | `http://localhost:8000` | No |
| `MODEL_VERSION` | Model version | `1.0.0` | No |
| `SCORING_THRESHOLD` | Minimum score threshold | `0.7` | No |
| `MAX_WORKERS` | Max worker threads | `4` | No |
| `TIMEOUT_SECONDS` | Request timeout | `5` | No |

### Production Considerations

1. **Security:**
   - Use HTTPS/TLS in production
   - Implement API authentication (JWT, API keys)
   - Set up rate limiting
   - Configure CORS properly in `main.py`

2. **Monitoring:**
   - Set up health check monitoring
   - Add logging and metrics (Prometheus, CloudWatch, etc.)
   - Use APM tools (DataDog, New Relic, etc.)

3. **Scaling:**
   - Use horizontal pod autoscaling in Kubernetes
   - Configure auto-scaling groups in AWS/Azure
   - Use managed services for easier scaling

4. **Performance:**
   - Enable caching if appropriate
   - Use CDN for static assets
   - Consider async workers for heavy processing
   - Monitor and optimize database queries (if added)

## Backend Integration

The backend can access the AI service at the configured URL:

```python
import requests

# Motion data from your backend
motion_data = {
    "frames": [...],
    "audio_bpm": 120.0
}

# Call AI service
response = requests.post(
    "http://ai-service-url/predict",
    json=motion_data,
    timeout=5
)

if response.status_code == 200:
    result = response.json()
    # Use the predictions
    score = result['overall_score']
    feedback = result['feedback']
```

## Troubleshooting

### Service won't start
- Check if port 8000 is available
- Verify all dependencies are installed
- Check logs for error messages

### Tests failing
- Ensure service is not running when running tests
- Check Python version (3.11+ required)
- Verify all dependencies are installed

### Docker build fails
- Check Docker version
- Ensure sufficient disk space
- Verify internet connection for pulling base images

### Health check failing
- Verify service is listening on correct port
- Check firewall rules
- Review application logs

## Support

For issues and questions:
- GitHub Issues: https://github.com/elove333/stepflow-ai/issues
- Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
