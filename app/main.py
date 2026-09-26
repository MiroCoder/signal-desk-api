from fastapi import FastAPI

from .routers.tickets import router as tickets_router
from .routers.projects import router as projects_router
from .routers.auth import router as auth_router

from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                    "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tickets_router)
app.include_router(projects_router)
app.include_router(auth_router)


@app.get("/health")
def health():
    return {"status": "ok"}