from fastapi import FastAPI
from app.routes.analysis import router as analysis_router

app = FastAPI()
app.include_router(analysis_router)
