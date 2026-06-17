from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    user_service_url: str = "http://localhost:8001"
    game_service_url: str = "http://localhost:8002"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # Added in Module 6 — M2M auth against auth-service
    auth_service_url: str = "http://localhost:8005"
    m2m_secret: str = "m2m-secret"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
