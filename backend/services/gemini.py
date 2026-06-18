from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
import json
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_sql(self, question: str, schema_context: str, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generates SQL from a natural language question using the provided schema context."""
        
        system_instruction = f"""
You are an expert SQL generator. Your task is to translate natural language questions into executable SQL queries.
You must ONLY use the tables and columns provided in the schema context below.
Do NOT use any fictional tables or columns.
Output ONLY the raw SQL query. Do not wrap it in markdown block quotes (```sql). Do not add any explanation or trailing comments.
Ensure the SQL is syntactically correct and compatible with standard SQL databases.

Schema Context:
{schema_context}
"""
        # Format chat history
        history_text = ""
        if chat_history:
            history_text = "Previous Chat History:\n"
            for msg in chat_history:
                role = "User" if msg['role'] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"
            history_text += "\n"

        prompt = f"{history_text}Current Question: {question}\n\nGenerate the SQL query for the current question."

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.0, # Use low temperature for more deterministic SQL generation
                )
            )
            
            sql = response.text.strip()
            # Clean up markdown formatting if the model still returns it
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
                
            return sql.strip()
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise

    def generate_insights(self, question: str, sql: str, columns: List[str], rows: List[Dict[str, Any]]) -> List[str]:
        """Takes query results and generates 3-5 business insights."""
        
        # Limit rows for prompt context to avoid token limits
        sample_data = rows[:50] 
        
        system_instruction = """
You are a data analyst. Your task is to analyze the results of a SQL query and provide 3-5 clear, concise, and actionable business insights.
Format your response as a JSON array of strings. 
Example: ["Insight 1 about the data", "Insight 2 about the data", "Insight 3 about the data"]
Do not return anything other than the JSON array.
"""
        prompt = f"""
Original Question: {question}
Executed SQL: {sql}
Columns: {columns}
Sample Data: {json.dumps(sample_data, default=str)}

Generate 3-5 insights based on this data.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            
            insights = json.loads(response.text)
            if isinstance(insights, list):
                return insights
            return ["Could not generate properly formatted insights."]
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return ["Error generating insights from data."]

    def explain_sql(self, sql: str, schema_context: str) -> Dict[str, Any]:
        """Explains SQL in plain English and identifies tables and operations used."""
        
        system_instruction = """
You are an expert SQL teacher. Explain the following SQL query in simple, plain English so that a non-technical user can understand it.
Also, list the tables used and the key SQL operations performed (e.g., JOIN, GROUP BY, ORDER BY).
Return the result STRICTLY as a JSON object with keys: "explanation" (string), "tables_used" (array of strings), and "operations" (array of strings).
"""
        prompt = f"""
Schema Context:
{schema_context}

SQL Query:
{sql}

Provide the explanation in JSON format.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            result = json.loads(response.text)
            return {
                "explanation": result.get("explanation", "No explanation provided."),
                "tables_used": result.get("tables_used", []),
                "operations": result.get("operations", [])
            }
        except Exception as e:
            logger.error(f"Error explaining SQL: {str(e)}")
            return {
                "explanation": "Could not generate explanation.",
                "tables_used": [],
                "operations": []
            }

    def suggest_chart_type(self, columns: List[str], rows: List[Dict[str, Any]], question: str) -> Optional[str]:
        """Analyzes data to suggest the best chart type."""
        
        sample_data = rows[:5]
        
        system_instruction = """
You are a data visualization expert. Suggest the best basic chart type to visualize the given data based on the user's question and the data structure.
Choose exactly ONE from this list: bar, line, pie, scatter, table.
If the data is a single value or doesn't make sense as a chart, return "table".
Return ONLY the word (e.g., "bar"). No other text.
"""
        prompt = f"""
User Question: {question}
Columns: {columns}
Sample Data: {json.dumps(sample_data, default=str)}

Suggest the best chart type.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )
            
            chart_type = response.text.strip().lower()
            valid_types = ['bar', 'line', 'pie', 'scatter', 'table']
            
            for vt in valid_types:
                if vt in chart_type:
                    return vt if vt != 'table' else None
                    
            return None
        except Exception as e:
            logger.error(f"Error suggesting chart type: {str(e)}")
            return None

# Singleton instance
gemini_service = GeminiService(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
