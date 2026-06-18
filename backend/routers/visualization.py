from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from backend.models.requests import VisualizeRequest
from backend.services.visualization import viz_service

router = APIRouter(prefix="/api", tags=["visualization"])

@router.post("/visualize")
async def visualize_data(request: VisualizeRequest):
    """
    Generate a chart configuration based on data and columns.
    """
    try:
        if not request.data or not request.columns:
            raise HTTPException(status_code=400, detail="Data and columns are required")
            
        chart_data = viz_service.generate_chart(
            columns=request.columns,
            data=request.data,
            chart_type=request.chart_type
        )
        
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")
