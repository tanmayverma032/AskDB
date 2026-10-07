from sqlalchemy import create_engine, inspect, text, Engine
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
import urllib.parse
import time
import logging

from backend.models.responses import SchemaInfo, TableInfo, ColumnInfo, ForeignKeyInfo, QueryResult

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.inspector = None
        self.schema_context: str = ""
        self._schema_info: Optional[SchemaInfo] = None

    @property
    def is_connected(self) -> bool:
        """Returns True if the engine is initialized and connection is alive."""
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def connect(self, db_type: str, host: str, port: int, user: str, password: str, database: str) -> bool:
        """
        Creates SQLAlchemy engine, tests connection, and runs introspection.
        """
        try:
            encoded_password = urllib.parse.quote_plus(password) if password else ""
            driver = "pymysql" if db_type.lower() == "mysql" else "psycopg2"
            db_url = f"{db_type.lower()}+{driver}://{user}:{encoded_password}@{host}:{port}/{database}"
            
            connect_args = {}
            if host.lower() not in ["localhost", "127.0.0.1", "mysql"]:
                # Cloud databases (TiDB Cloud, Aiven, AWS RDS) require SSL/TLS
                import os
                ssl_dict = {}
                if os.path.exists("/etc/ssl/certs/ca-certificates.crt"):
                    ssl_dict["ca"] = "/etc/ssl/certs/ca-certificates.crt"
                else:
                    try:
                        import certifi
                        ssl_dict["ca"] = certifi.where()
                    except Exception:
                        pass
                if ssl_dict:
                    connect_args["ssl"] = ssl_dict
                else:
                    connect_args["ssl"] = {"check_hostname": False}

            self.engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            # Run introspection
            self.inspector = inspect(self.engine)
            self._schema_info = self.get_schema()
            self.schema_context = self.build_schema_context()
            
            logger.info(f"Successfully connected to database: {database}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self.engine = None
            self.inspector = None
            return False

    def disconnect(self):
        """Disposes the SQLAlchemy engine."""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.inspector = None
            self.schema_context = ""
            self._schema_info = None

    def get_schema(self) -> SchemaInfo:
        """Uses sqlalchemy.inspect() to get all tables, columns, types, PKs, FKs."""
        if not self.inspector:
            raise ValueError("Database is not connected.")
            
        tables = []
        for table_name in self.inspector.get_table_names():
            columns = []
            for col in self.inspector.get_columns(table_name):
                columns.append(ColumnInfo(
                    name=col['name'],
                    type=str(col['type']),
                    nullable=col['nullable']
                ))
            
            pk_constraint = self.inspector.get_pk_constraint(table_name)
            primary_keys = pk_constraint.get('constrained_columns', []) if pk_constraint else []
            
            foreign_keys = []
            for fk in self.inspector.get_foreign_keys(table_name):
                for col, ref_col in zip(fk['constrained_columns'], fk['referred_columns']):
                    foreign_keys.append(ForeignKeyInfo(
                        column=col,
                        referred_table=fk['referred_table'],
                        referred_column=ref_col
                    ))
                    
            tables.append(TableInfo(
                name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys
            ))
            
        return SchemaInfo(tables=tables)

    def build_schema_context(self) -> str:
        """Formats schema into natural language prompt context."""
        if not self._schema_info:
            return ""
            
        context_parts = []
        for table in self._schema_info.tables:
            table_desc = f"Table: {table.name}\n  Columns: "
            
            col_descs = []
            for col in table.columns:
                pk_indicator = ", PK" if col.name in table.primary_keys else ""
                col_descs.append(f"{col.name} ({col.type}{pk_indicator})")
                
            table_desc += ", ".join(col_descs)
            
            if table.foreign_keys:
                fk_descs = []
                for fk in table.foreign_keys:
                    fk_descs.append(f"{fk.column} -> {fk.referred_table}.{fk.referred_column}")
                table_desc += f"\n  Foreign Keys: " + ", ".join(fk_descs)
                
            context_parts.append(table_desc)
            
        return "\n\n".join(context_parts)

    def execute_query(self, sql_query: str) -> QueryResult:
        """Uses text() and conn.execute(), measures execution time, converts to list of dicts."""
        if not self.engine:
            raise ValueError("Database is not connected.")
            
        start_time = time.perf_counter()
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                
                columns = list(result.keys())
                # Using mappings to convert row objects to dicts
                rows = [dict(row) for row in result.mappings().all()]
                
                execution_time_ms = (time.perf_counter() - start_time) * 1000
                
                return QueryResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                    execution_time_ms=execution_time_ms
                )
        except SQLAlchemyError as e:
            raise ValueError(f"Query execution failed: {str(e)}")

    def get_table_names(self) -> List[str]:
        """Returns a list of all table names."""
        if self._schema_info:
            return [t.name for t in self._schema_info.tables]
        return []

    def get_column_names(self, table_name: str) -> List[str]:
        """Returns a list of column names for a specific table."""
        if self._schema_info:
            for t in self._schema_info.tables:
                if t.name == table_name:
                    return [c.name for c in t.columns]
        return []

    def get_all_columns(self) -> Dict[str, List[str]]:
        """Returns {table: [columns]} for validation."""
        result = {}
        if self._schema_info:
            for t in self._schema_info.tables:
                result[t.name] = [c.name for c in t.columns]
        return result

# Singleton instance
db_service = DatabaseService()
