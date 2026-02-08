"""FastAPI service for motion data prediction."""
import time
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from models import MotionData, PredictionResult
from analyzer import MotionAnalyzer
from config import settings


# Initialize analyzer
analyzer = MotionAnalyzer(scoring_threshold=settings.scoring_threshold)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    print(f"Starting AI service on {settings.host}:{settings.port}")
    print(f"Model version: {settings.model_version}")
    yield
    # Shutdown
    print("Shutting down AI service")


# Create FastAPI app
app = FastAPI(
    title="StepFlow AI Service",
    description="AI/ML pipeline for motion data analysis and coaching feedback",
    version=settings.model_version,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "StepFlow AI",
        "version": settings.model_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "stepflow-ai",
        "version": settings.model_version
    }


@app.post("/predict", response_model=PredictionResult)
async def predict(motion_data: MotionData):
    """
    Predict motion performance and generate coaching feedback.
    
    Args:
        motion_data: Input motion data containing frames with keypoints
        
    Returns:
        PredictionResult with scores, metrics, and feedback
        
    Raises:
        HTTPException: If processing fails
    """
    try:
        # Start timing
        start_time = time.perf_counter()
        
        # Validate input
        if not motion_data.frames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Motion data must contain at least one frame"
            )
        
        # Analyze motion data
        timing_metrics, movement_metrics, feedback = analyzer.analyze(motion_data)
        
        # Calculate overall score
        overall_score = analyzer.calculate_overall_score(timing_metrics, movement_metrics)
        
        # Calculate processing time
        processing_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Return prediction result
        return PredictionResult(
            overall_score=overall_score,
            timing_metrics=timing_metrics,
            movement_metrics=movement_metrics,
            feedback=feedback,
            processing_time_ms=processing_time_ms
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
