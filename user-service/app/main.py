from fastapi import FastAPI
from app.database.connection import Base, engine
from app.models.user_profile import UserProfile
from app.routes.user_profile import router as user_profile_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title = "AI Microservices - User Service",
    version="1.0.0"
)
app.include_router(user_profile_router  )

@app.get("/")
def root():
    return {"message": "User Service is running"}

