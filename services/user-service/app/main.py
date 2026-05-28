from fastapi import FastAPI
from app.routes import router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="user-service", version="1.0.0")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}
