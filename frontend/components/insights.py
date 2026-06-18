import streamlit as st

def render_insights(insights: list[str]):
    if not insights:
        return
        
    st.markdown("### 💡 AI Insights")
    
    for idx, insight in enumerate(insights):
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-icon">💡</span>
            <strong>Insight {idx+1}:</strong> {insight}
        </div>
        """, unsafe_allow_html=True)
