import streamlit as st
import time
from utils.api_client import api_client
from components.results import render_results
from components.charts import render_chart
from components.insights import render_insights

def handle_user_input(question: str):
    if not st.session_state.get("connected"):
        st.error("Please connect to a database first!")
        return

    st.session_state.messages.append({"role": "user", "content": question})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = api_client.chat(question, st.session_state.session_id)
            
            if "error" in res:
                st.error(f"Error: {res['error']}")
                msg = {"role": "assistant", "error": res["error"]}
            else:
                msg = {
                    "role": "assistant",
                    "content": "Here is what I found:",
                    "data": res
                }
                
                # Add to query history
                st.session_state.query_history.append({
                    "question": question,
                    "timestamp": time.time()
                })
            
            st.session_state.messages.append(msg)
            
            st.rerun()

def render_chat():
    # Display chat history
    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["content"])
            else:
                if "error" in msg:
                    st.error(msg["error"])
                else:
                    st.write(msg.get("content", ""))
                    data = msg.get("data", {})
                    
                    if data.get("generated_sql"):
                        st.code(data["generated_sql"], language="sql")
                        
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.button("Explain", key=f"explain_{idx}"):
                                with st.spinner("Explaining..."):
                                    explanation = api_client.explain_query(data["generated_sql"])
                                    if not explanation.get("error"):
                                        st.info(explanation.get("explanation", "No explanation available."))
                                    else:
                                        st.error(explanation.get("error"))

                    validation = data.get("validation", {})
                    if not validation.get("is_valid", True) and validation:
                        if validation.get("warnings"):
                            st.warning(f"SQL Warnings: {validation.get('warnings')}")
                        if validation.get("errors"):
                            st.error(f"SQL Errors: {validation.get('errors')}")
                        
                    results = data.get("results")
                    if results:
                        render_results(results)
                        
                    chart = data.get("chart")
                    if chart and st.session_state.get("auto_charts", True):
                        render_chart(chart)
                        
                    insights = data.get("insights")
                    if insights and st.session_state.get("auto_insights", True):
                        render_insights(insights)

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        handle_user_input(prompt)
