import streamlit as st
import plotly.io as pio
import json

def render_chart(chart_json: dict, question: str = ""):
    if not chart_json:
        return
        
    st.markdown("### 📊 Visualization")
    
    try:
        # Convert dict back to Plotly figure
        fig = pio.from_json(json.dumps(chart_json))
        
        # Apply dark theme overrides
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not render chart: {str(e)}")
