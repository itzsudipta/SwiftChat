from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app import models, database
from app.routes import auth, chat
from app import websocket
from app.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS, DEBUG
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG
)

# Add CORS middleware with environment-specific origins
if DEBUG:
    # In development, allow all origins for easier testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
        allow_headers=["*"],  # Allow all headers
    )
else:
    # In production, use specific configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,  # Use configured origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods including OPTIONS
        allow_headers=["*"],  # Allow all headers
    )

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(websocket.router)

# Serve static files (frontend)
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

if os.path.exists(frontend_dir):
    # Mount static files
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
    
    # Serve frontend pages
    @app.get("/")
    async def serve_home():
        """Serve the main page (redirect to login)"""
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    
    @app.get("/login")
    async def serve_login():
        """Serve login page"""
        return FileResponse(os.path.join(frontend_dir, "login.html"))
    
    @app.get("/register")
    async def serve_register():
        """Serve registration page"""
        return FileResponse(os.path.join(frontend_dir, "register.html"))
    
    @app.get("/chat")
    async def serve_chat():
        """Serve chat page"""
        return FileResponse(os.path.join(frontend_dir, "chat.html"))
    
    @app.get("/{filename}")
    async def serve_static_files(filename: str):
        """Serve CSS, JS, and other static files"""
        file_path = os.path.join(frontend_dir, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        # If file doesn't exist, redirect to login page
        return FileResponse(os.path.join(frontend_dir, "login.html"))

# Health check endpoint for deployment
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "SwiftChat API"}
