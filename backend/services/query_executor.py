from typing import Optional
from backend.services.database import db_service as default_db_service, DatabaseService
from backend.models.responses import QueryResult
from sqlalchemy.exc import OperationalError, ProgrammingError, IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class QueryExecutor:
    def execute(self, sql: str, db_service: Optional[DatabaseService] = None, max_rows: int = 1000) -> QueryResult:
        """
        Executes the query securely using db_service.
        Enforces SELECT-only and LIMIT constraints.
        """
        service = db_service or default_db_service
        
        # Defense in depth: Verify it's a SELECT query
        sql_clean = sql.strip().rstrip(';')
        if not sql_clean.upper().startswith("SELECT"):
            raise ValueError("Execution blocked: Only SELECT queries are permitted.")
            
        # Add LIMIT if not present
        if "LIMIT" not in sql_clean.upper():
            sql_clean = f"{sql_clean} LIMIT {max_rows}"
            
        try:
            # Execute via the database service
            result = service.execute_query(sql_clean)
            return result
            
        except ProgrammingError as e:
            # Handle SQL syntax errors
            logger.error(f"SQL Syntax Error: {str(e)}")
            raise ValueError(f"SQL Syntax Error. The generated query was invalid: {getattr(e, 'orig', str(e))}")
        except OperationalError as e:
            # Handle connection/database errors
            logger.error(f"Database Operational Error: {str(e)}")
            raise ValueError(f"Database error. Please check connection and try again: {getattr(e, 'orig', str(e))}")
        except SQLAlchemyError as e:
            # Generic SQLAlchemy errors
            logger.error(f"Database Execution Error: {str(e)}")
            raise ValueError(f"Error executing query: {str(e)}")
        except Exception as e:
            # Any other errors
            logger.error(f"Unexpected execution error: {str(e)}")
            raise ValueError(f"An unexpected error occurred during execution: {str(e)}")

# Singleton
query_executor = QueryExecutor()
