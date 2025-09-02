from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import clustering, scraping

app = FastAPI(
    title="SNUC Club Analysis Backend",
    description="API for analyzing and clustering SNUC club data.",
    version="0.1.0",
)

# --- CORS Middleware Setup ---
# This allows the frontend (running on a different port) to communicate with the backend.
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Create React App default
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)
# --- End CORS Setup ---

# Include the routers
app.include_router(clustering.router)
app.include_router(scraping.router)

@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the SNUC Club Analysis API"}
