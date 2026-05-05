from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from routers import analysis, compare

app = FastAPI(title="Fake Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analysis.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
