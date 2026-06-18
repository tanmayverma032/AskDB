from fastapi import APIRouter, HTTPException
from typing import List

from backend.models.requests import DatabaseConnectionRequest
from backend.models.responses import DatabaseStatusResponse, SchemaInfo
from backend.services.database import db_service

router = APIRouter(prefix="/api/database", tags=["database"])

@router.post("/connect", response_model=DatabaseStatusResponse)
async def connect_db(request: DatabaseConnectionRequest):
    """
    Connect to a MySQL or PostgreSQL database.
    """
    try:
        success = db_service.connect(
            db_type=request.db_type,
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database
        )
        if success:
            return DatabaseStatusResponse(
                connected=True,
                database=request.database,
                message="Successfully connected to database."
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to connect to the database. Check credentials.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect_db():
    """
    Disconnect from the current database.
    """
    try:
        db_service.disconnect()
        return {"message": "Successfully disconnected from database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=DatabaseStatusResponse)
async def get_status():
    """
    Get the current database connection status.
    """
    try:
        is_connected = db_service.is_connected
        return DatabaseStatusResponse(
            connected=is_connected,
            database="",
            message="Connected" if is_connected else "Not connected"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schema", response_model=SchemaInfo)
async def get_schema():
    """
    Get the schema information of the connected database.
    """
    try:
        if not db_service.is_connected:
            raise HTTPException(status_code=400, detail="Database not connected.")
        schema = db_service.get_schema()
        if not schema:
            raise HTTPException(status_code=404, detail="Schema information not found.")
        return schema
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables", response_model=List[str])
async def get_tables():
    """
    Get a list of table names in the connected database.
    """
    try:
        if not db_service.is_connected:
            raise HTTPException(status_code=400, detail="Database not connected.")
        schema = db_service.get_schema()
        if schema and schema.tables:
            return [table.name for table in schema.tables]
        return []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
