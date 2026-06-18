from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any

from backend.config import settings
from backend.services.database import db_service
from backend.services.gemini import gemini_service  
from backend.services.query_validator import query_validator
from backend.services.query_executor import query_executor
from backend.services.visualization import viz_service
from backend.services.memory import memory
from backend.models.requests import ChatRequest
from backend.models.responses import ChatResponse, ValidationResult, QueryResult, InsightResponse

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for natural language database querying.
    Takes a natural language question and returns SQL, results, insights, and visualizations.
    """
    try:
        # 1. Get schema context
        schema_info = db_service.get_schema()
        if not schema_info:
            raise HTTPException(status_code=400, detail="Database not connected or schema unavailable")

        # 2. Get chat history from memory
        history = memory.get_history(request.session_id)

        # 3. Generate SQL via gemini_service
        sql_query = await gemini_service.generate_sql(request.question, schema_info, history)
        if not sql_query:
            raise HTTPException(status_code=500, detail="Failed to generate SQL query")

        # 4. Validate SQL via query_validator
        validation: ValidationResult = query_validator.validate(sql_query)
        
        # If validation fails, return early with errors
        if not validation.is_valid:
            response = ChatResponse(
                question=request.question,
                sql_query=sql_query,
                is_valid=False,
                validation_errors=validation.errors,
                results=None,
                insights=None,
                visualization=None
            )
            # Save failed attempt to memory
            memory.add_interaction(request.session_id, request.question, response.model_dump())
            return response

        # 5. If valid, execute via query_executor
        try:
            query_result: QueryResult = query_executor.execute(sql_query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")

        # 6. Generate insights via gemini_service
        try:
            insights = await gemini_service.generate_insights(request.question, query_result, sql_query)
            insights_obj = InsightResponse(
                summary=insights.get("summary", ""),
                key_findings=insights.get("key_findings", []),
                business_implications=insights.get("business_implications", ""),
                recommendations=insights.get("recommendations", [])
            )
        except Exception as e:
            # Fallback if insight generation fails
            insights_obj = InsightResponse(
                summary=f"Failed to generate insights: {str(e)}",
                key_findings=[],
                business_implications="",
                recommendations=[]
            )

        # 7. Suggest chart type and generate chart via viz_service
        chart_data = None
        if query_result.data and len(query_result.data) > 0:
            try:
                chart_type = viz_service.suggest_chart_type(query_result.columns, query_result.data)
                if chart_type:
                    chart_data = viz_service.generate_chart(query_result.columns, query_result.data, chart_type)
            except Exception as e:
                # Log or ignore viz errors to not block the main response
                pass

        # 8. Construct response
        response = ChatResponse(
            question=request.question,
            sql_query=sql_query,
            is_valid=True,
            validation_errors=[],
            results=query_result,
            insights=insights_obj,
            visualization=chart_data
        )

        # 9. Save to memory
        memory.add_interaction(request.session_id, request.question, response.model_dump())

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
