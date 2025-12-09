import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import assessments, entities, orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(title="ClearanceAI Python Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assessments.router, prefix="/api", tags=["assessments"])
app.include_router(entities.router, prefix="/api", tags=["entities"])
app.include_router(orders.router, prefix="/api", tags=["orders"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "clearanceai-python-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

