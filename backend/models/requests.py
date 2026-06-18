from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import uuid4

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question to translate to SQL")
    session_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session identifier for chat history")

class DatabaseConnectionRequest(BaseModel):
    db_type: str = Field(..., description="Type of database: mysql or postgresql")
    host: str = Field(..., description="Database host address")
    port: int = Field(..., description="Database port")
    user: str = Field(..., description="Database username")
    password: str = Field(default="", description="Database password")
    database: str = Field(..., description="Database name")

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v
        
    @field_validator('db_type')
    @classmethod
    def validate_db_type(cls, v: str) -> str:
        if v.lower() not in ["mysql", "postgresql"]:
            raise ValueError("Unsupported database type. Use 'mysql' or 'postgresql'")
        return v.lower()

class QueryExecuteRequest(BaseModel):
    sql: str = Field(..., description="The SQL query to execute")
    session_id: str = Field(..., description="Session identifier")

class ExplainRequest(BaseModel):
    sql: str = Field(..., description="The SQL query to explain")

class VisualizeRequest(BaseModel):
    columns: List[str] = Field(..., description="List of column names")
    data: List[Dict[str, Any]] = Field(..., description="Row data as list of dictionaries")
    chart_type: Optional[str] = Field(default=None, description="Requested chart type (bar, line, etc.)")
