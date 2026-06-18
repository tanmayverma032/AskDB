import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class VisualizationService:
    def _prepare_dataframe(self, columns: List[str], rows: List[Dict[str, Any]]) -> pd.DataFrame:
        """Converts rows and columns to a pandas DataFrame for Plotly."""
        df = pd.DataFrame(rows, columns=columns)
        
        # Attempt to convert column types to appropriate pandas types
        for col in df.columns:
            # Try to convert to datetime
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                    continue
                except (ValueError, TypeError):
                    pass
                    
            # Try numeric
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
                
        return df

    def detect_chart_type(self, columns: List[str], rows: List[Dict[str, Any]]) -> Optional[str]:
        """
        Analyzes column types to suggest a chart.
        Fallback logic if Gemini suggestion is not used or fails.
        """
        if not rows or len(columns) < 2:
            return None
            
        df = self._prepare_dataframe(columns, rows)
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Rules for chart type detection
        if len(date_cols) >= 1 and len(numeric_cols) >= 1:
            return 'line'
        
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            # If the categorical column has few unique values, maybe pie, else bar
            unique_cats = df[categorical_cols[0]].nunique()
            if unique_cats <= 7 and len(numeric_cols) == 1:
                return 'pie'
            return 'bar'
            
        if len(numeric_cols) >= 2:
            return 'scatter'
            
        return None

    def generate_chart(self, columns: List[str], rows: List[Dict[str, Any]], chart_type: str, question: str = "") -> Optional[Dict[str, Any]]:
        """
        Generates a Plotly chart and returns the JSON configuration.
        """
        if not rows or not columns:
            return None
            
        try:
            df = self._prepare_dataframe(columns, rows)
            
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
            
            fig = None
            title = question if question else f"Data Visualization"
            
            # Vibrant color palette for dark theme
            color_sequence = px.colors.qualitative.Pastel
            
            if chart_type == 'bar':
                if categorical_cols and numeric_cols:
                    x_col = categorical_cols[0]
                    y_col = numeric_cols[0]
                    fig = px.bar(df, x=x_col, y=y_col, title=title, 
                                 template='plotly_dark', color_discrete_sequence=color_sequence)
                elif len(numeric_cols) >= 2:
                    fig = px.bar(df, x=numeric_cols[0], y=numeric_cols[1], title=title, 
                                 template='plotly_dark', color_discrete_sequence=color_sequence)
                                 
            elif chart_type == 'line':
                date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
                x_col = date_cols[0] if date_cols else (categorical_cols[0] if categorical_cols else columns[0])
                y_col = numeric_cols[0] if numeric_cols else columns[1]
                
                fig = px.line(df, x=x_col, y=y_col, title=title, 
                              template='plotly_dark', color_discrete_sequence=color_sequence, markers=True)
                              
            elif chart_type == 'pie':
                if categorical_cols and numeric_cols:
                    names_col = categorical_cols[0]
                    values_col = numeric_cols[0]
                    fig = px.pie(df, names=names_col, values=values_col, title=title, 
                                 template='plotly_dark', color_discrete_sequence=color_sequence)
                                 
            elif chart_type == 'scatter':
                if len(numeric_cols) >= 2:
                    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=title, 
                                     template='plotly_dark', color_discrete_sequence=color_sequence)
                                     
            if fig:
                # Common layout adjustments
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(t=50, l=20, r=20, b=20)
                )
                
                # Convert figure to JSON serializable dict
                chart_json_str = fig.to_json()
                return json.loads(chart_json_str)
                
            return None
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return None

# Singleton
viz_service = VisualizationService()
