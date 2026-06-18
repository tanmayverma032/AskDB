import streamlit as st
import pandas as pd
import io

def render_results(query_result: dict):
    if not query_result:
        return
        
    rows = query_result.get("rows", [])
    columns = query_result.get("columns", [])
    row_count = query_result.get("row_count", 0)
    exec_time = query_result.get("execution_time_ms", 0)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**Results** ({row_count} rows)")
    with col2:
        st.markdown(f"<div style='text-align: right; color: #888; font-size: 0.85em;'>⏱️ {exec_time:.2f}ms</div>", unsafe_allow_html=True)
    
    if not rows:
        st.info("No results returned for this query.")
        return
        
    df = pd.DataFrame(rows, columns=columns)
    
    # Render dataframe
    st.dataframe(df, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="query_results.csv",
        mime="text/csv",
    )
