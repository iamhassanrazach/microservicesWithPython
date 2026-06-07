from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    user_service_url: str = "http://localhost:8001"
    game_service_url: str = "http://localhost:8002"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    class Config:
        env_file = ".env"


settings = Settings()
