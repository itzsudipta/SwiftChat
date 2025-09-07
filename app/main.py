from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.routes import auth, chat
from app import websocket
from app.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS, DEBUG

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
