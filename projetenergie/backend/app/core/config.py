from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Senelec"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # SQL Server Database configuration (Driver 18)
    DATABASE_URL: str = "mssql+pyodbc://sa:YourStrong!Pass@localhost/SmartSenelec?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    
    # Keycloak configuration
    KEYCLOAK_URL: str = "http://localhost:8081"
    KEYCLOAK_REALM: str = "senelec"
    KEYCLOAK_CLIENT_ID: str = "senelec-backend"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
