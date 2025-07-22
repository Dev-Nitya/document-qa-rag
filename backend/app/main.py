import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.qa import QARouter
from backend.app.routes.feedback import feedback_router
from backend.app.routes.chat import chat_router
from backend.app.routes.upload import upload_router
from backend.app.experiments.test_chains import ab_runner

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow specific origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(feedback_router, prefix="/api")
app.include_router(QARouter, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

# ab_runner()



