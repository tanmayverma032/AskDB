from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import urllib.parse

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API Key")
    GEMINI_MODEL: str = Field(default="gemini-flash-latest", description="Gemini model to use")
    
    DB_TYPE: str = Field(default="mysql", description="Database type (mysql or postgresql)")
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=3306, description="Database port")
    DB_USER: str = Field(default="root", description="Database user")
    DB_PASSWORD: str = Field(default="", description="Database password")
    DB_NAME: str = Field(default="askdb_sample", description="Database name")
    
    FASTAPI_HOST: str = Field(default="0.0.0.0", description="Host to run FastAPI on")
    FASTAPI_PORT: int = Field(default=8000, description="Port to run FastAPI on")
    
    MAX_ROWS: int = Field(default=1000, description="Maximum rows to return in query")
    MAX_CHAT_HISTORY: int = Field(default=20, description="Maximum chat history messages to keep")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    @field_validator('DB_PORT', 'FASTAPI_PORT')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    @property
    def DB_URL(self) -> str:
        """Computes the database URL for SQLAlchemy."""
        encoded_password = urllib.parse.quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        driver = "pymysql" if self.DB_TYPE.lower() == "mysql" else "psycopg2"
        return f"{self.DB_TYPE.lower()}+{driver}://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
