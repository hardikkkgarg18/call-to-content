from __future__ import annotations
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

load_dotenv()

app = FastAPI(
    title="Call Content Pipeline",
    description="AI-native conversation intelligence — extract signals, generate insights and content from customer calls",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
