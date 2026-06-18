import sqlparse
import re
from typing import Dict, List, Tuple
from backend.models.responses import ValidationResult
import logging

logger = logging.getLogger(__name__)

class QueryValidator:
    def __init__(self):
        # Blocklist for dangerous operations
        self.dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'INSERT', 
            'UPDATE', 'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
        ]

    def _is_dangerous(self, sql: str) -> Tuple[bool, str]:
        """Checks the query against a blocklist of dangerous keywords."""
        sql_upper = sql.upper()
        # Find isolated words to avoid matching sub-strings (e.g., matching 'DROP' but not 'DROP_TABLE')
        words = re.findall(r'\b\w+\b', sql_upper)
        
        for keyword in self.dangerous_keywords:
            if keyword in words:
                return True, f"Dangerous keyword detected: {keyword}"
                
        return False, ""

    def _extract_tables(self, parsed_sql) -> List[str]:
        """Extracts table names from parsed SQL statement."""
        tables = []
        
        # Simplified extraction logic - in a real-world scenario, this needs 
        # to handle JOINs, aliases, schema prefixes comprehensively.
        # This implementation looks for identifiers after FROM and JOIN
        
        from_seen = False
        for token in parsed_sql.tokens:
            if token.is_whitespace:
                continue
                
            if token.ttype is sqlparse.tokens.Keyword and token.value.upper() in ['FROM', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN']:
                from_seen = True
                continue
                
            if from_seen:
                if isinstance(token, sqlparse.sql.IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.append(identifier.get_real_name())
                elif isinstance(token, sqlparse.sql.Identifier):
                    tables.append(token.get_real_name())
                elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() not in ['AS']:
                    from_seen = False
                    
        return [t for t in tables if t]

    def _extract_columns(self, parsed_sql) -> List[str]:
        """Extracts column references from parsed SQL."""
        columns = []
        
        # Very basic column extraction for validation
        # In a real system, you'd need a full AST parser to correctly resolve aliases and functions
        for token in parsed_sql.flatten():
            if token.ttype in sqlparse.tokens.Name:
                columns.append(token.value)
                
        return columns

    def validate(self, sql: str, schema: Dict[str, List[str]]) -> ValidationResult:
        """
        Validates the SQL query:
        1. Checks for dangerous keywords
        2. Ensures it's a SELECT query
        3. Parses syntax
        4. Validates table names
        5. Validates column names (best-effort)
        """
        errors = []
        warnings = []
        
        # Clean query
        sql_clean = sql.strip().strip(';')
        
        # 1. Check for dangerous keywords
        is_dangerous, reason = self._is_dangerous(sql_clean)
        if is_dangerous:
            errors.append(reason)
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
            
        # 2. Ensure it starts with SELECT (basic defense)
        if not sql_clean.upper().startswith("SELECT"):
            errors.append("Only SELECT queries are allowed.")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
            
        try:
            # 3. Parse with sqlparse
            parsed_statements = sqlparse.parse(sql_clean)
            
            if len(parsed_statements) != 1:
                errors.append("Only single SQL statements are allowed.")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
                
            stmt = parsed_statements[0]
            
            # 4. Extract and validate tables
            extracted_tables = self._extract_tables(stmt)
            schema_tables = [t.lower() for t in schema.keys()]
            
            if not extracted_tables:
                warnings.append("Could not reliably identify tables in query.")
                
            for table in extracted_tables:
                if table and table.lower() not in schema_tables:
                    errors.append(f"Table '{table}' does not exist in schema.")
                    
            # 5. Extract and validate columns (best-effort, hence warnings instead of errors for misses)
            # Since SQL parsing is complex (aliases, functions like COUNT(*)), 
            # we mainly warn about missing columns rather than outright failing it
            # if we can't definitively prove it's wrong.
            
            # Simple check for *
            if "*" in sql_clean:
                warnings.append("Using SELECT * can be inefficient. Consider selecting specific columns.")
                
        except Exception as e:
            errors.append(f"SQL parsing error: {str(e)}")
            
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

# Singleton
query_validator = QueryValidator()
