from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Senelec"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:8080",
        "http://localhost:4200",
        "http://localhost",
        "https://*.senelec.com"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # SQL Server Database configuration (Driver 18)
    DATABASE_URL: str = "mssql+pyodbc://sa:YourStrong!Pass@db/SmartSenelec?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    # Configuration Redis (Ajoutée pour corriger le crash)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
