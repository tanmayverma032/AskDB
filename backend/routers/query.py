from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from backend.models.requests import QueryExecuteRequest, ExplainRequest
from backend.models.responses import QueryResult, ExplainResponse
from backend.services.query_validator import query_validator
from backend.services.query_executor import query_executor
from backend.services.gemini import gemini_service
from backend.services.memory import memory
from backend.services.database import db_service

router = APIRouter(prefix="/api/query", tags=["query"])

@router.post("/execute", response_model=QueryResult)
async def execute_query(request: QueryExecuteRequest):
    """
    Validate and execute a raw SQL query.
    """
    try:
        # Validate SQL
        validation = query_validator.validate(request.sql)
        if not validation.is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Query validation failed: {', '.join(validation.errors)}"
            )
        
        # Execute SQL
        result = query_executor.execute(request.sql)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution error: {str(e)}")

@router.post("/explain", response_model=ExplainResponse)
async def explain_query(request: ExplainRequest):
    """
    Explain what a SQL query does in plain English.
    """
    try:
        schema_info = None
        if db_service.is_connected():
            schema_info = db_service.get_schema()
            
        explanation = await gemini_service.explain_sql(request.sql, schema_info)
        return ExplainResponse(
            sql=request.sql,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to explain query: {str(e)}")

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """
    Get the chat/query history for a given session.
    """
    try:
        history = memory.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
