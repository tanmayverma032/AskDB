from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any, List

from backend.config import settings
from backend.services.database import db_service
from backend.services.gemini import gemini_service  
from backend.services.query_validator import query_validator
from backend.services.query_executor import query_executor
from backend.services.visualization import viz_service
from backend.services.memory import memory
from backend.models.requests import ChatRequest
from backend.models.responses import ChatResponse, ValidationResult, QueryResult

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main endpoint for natural language database querying.
    Takes a natural language question and returns SQL, results, insights, and visualizations.
    """
    try:
        # 1. Get schema context
        if not db_service.is_connected:
            raise HTTPException(status_code=400, detail="Database not connected or schema unavailable")
            
        schema_context = db_service.schema_context or db_service.build_schema_context()
        if not schema_context:
            raise HTTPException(status_code=400, detail="Database schema unavailable")

        # 2. Get chat history from memory
        history = memory.get_history(request.session_id)

        # 3. Generate SQL via gemini_service
        try:
            sql_query = gemini_service.generate_sql(request.question, schema_context, history)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate SQL query: {str(e)}")

        if not sql_query:
            raise HTTPException(status_code=500, detail="Failed to generate SQL query")

        # 4. Validate SQL via query_validator
        validation: ValidationResult = query_validator.validate(sql_query)
        
        # If validation fails, return early with errors
        if not validation.is_valid:
            response = ChatResponse(
                question=request.question,
                generated_sql=sql_query,
                validation=validation,
                results=None,
                insights=[],
                chart=None,
                session_id=request.session_id
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
        insights: List[str] = []
        try:
            insights = gemini_service.generate_insights(
                question=request.question,
                sql=sql_query,
                columns=query_result.columns,
                rows=query_result.rows
            )
        except Exception as e:
            insights = [f"Could not generate insights: {str(e)}"]

        # 7. Suggest chart type and generate chart via viz_service
        chart_data = None
        if query_result.rows and len(query_result.rows) > 0:
            try:
                chart_type = viz_service.suggest_chart_type(query_result.columns, query_result.rows)
                if chart_type:
                    chart_data = viz_service.generate_chart(
                        columns=query_result.columns,
                        rows=query_result.rows,
                        chart_type=chart_type,
                        question=request.question
                    )
            except Exception:
                # Ignore viz errors to not block the main response
                pass

        # 8. Construct response matching ChatResponse model
        response = ChatResponse(
            question=request.question,
            generated_sql=sql_query,
            validation=validation,
            results=query_result,
            insights=insights,
            chart=chart_data,
            session_id=request.session_id
        )

        # 9. Save to memory
        memory.add_interaction(request.session_id, request.question, response.model_dump())

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
