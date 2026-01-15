from fastapi import FastAPI
from contextlib import asynccontextmanager
from .config import get_settings
from .routers import mcp_router
from .core.security import SecurityMiddleware
from fastapi.middleware.cors import CORSMiddleware
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_mcp_server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # In a real app, initialize DB connections here
    yield
    logger.info("Shutting down")

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )

    # Add Security Middleware
    app.add_middleware(SecurityMiddleware)
    
    # Enable CORS for UI
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount MCP Router
    app.include_router(mcp_router.router)

    @app.get("/health")
    def health_check():
        return {"status": "ok", "version": settings.APP_VERSION}

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_mcp_server.main:app", host="0.0.0.0", port=8000, reload=True)
