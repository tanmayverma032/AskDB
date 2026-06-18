import streamlit as st
from utils.api_client import api_client

def render_sidebar():
    with st.sidebar:
        st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🔮 AskDB</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 0.9em;'>AI-Powered Database Assistant</p>", unsafe_allow_html=True)
        st.divider()

        # Database Connection Section
        st.subheader("🔌 Connection")
        db_type = st.selectbox("Database Type", ["postgresql", "mysql"], index=0)
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="5432" if db_type == "postgresql" else "3306")
        user = st.text_input("User", value="postgres" if db_type == "postgresql" else "root")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database", value="askdb_sample")
        
        if st.button("Connect", use_container_width=True):
            with st.spinner("Connecting..."):
                res = api_client.connect_database(db_type, host, port, user, password, database)
                if res.get("connected") == True or res.get("message") == "Successfully connected to database.":
                    st.session_state.connected = True
                    st.session_state.db_info = res
                    st.success("Connected successfully!")
                    
                    # Fetch schema
                    schema_res = api_client.get_schema()
                    if "tables" in schema_res:
                        st.session_state.schema = schema_res
                else:
                    st.session_state.connected = False
                    error_msg = res.get('error') or res.get('detail') or "Unknown error"
                    st.error(f"Failed to connect: {error_msg}")
                    
        if st.session_state.get("connected"):
            if st.button("Disconnect", use_container_width=True):
                api_client.disconnect_database()
                st.session_state.connected = False
                st.session_state.schema = None
                st.success("Disconnected.")
        
        st.divider()
        
        # Schema Explorer
        if st.session_state.get("connected") and st.session_state.get("schema"):
            st.subheader("📊 Schema Explorer")
            for table in st.session_state.schema.get("tables", []):
                with st.expander(f"📁 {table['name']}"):
                    for col in table.get("columns", []):
                        st.markdown(f"• `{col['name']}` <span class='schema-badge'>{col['type']}</span>", unsafe_allow_html=True)
        
        st.divider()
        
        # Query History
        st.subheader("⏱️ History")
        if st.session_state.get("query_history"):
            for i, q in enumerate(st.session_state.query_history[-5:]):
                st.caption(f"{q['question'][:30]}...")
        else:
            st.caption("No history yet.")
            
        st.divider()
        
        # Settings
        st.subheader("⚙️ Settings")
        st.slider("Max Rows", 10, 1000, 100, key="max_rows")
        st.toggle("Auto-generate Insights", value=True, key="auto_insights")
        st.toggle("Auto-generate Charts", value=True, key="auto_charts")
        
        st.markdown("<div style='margin-top: 50px; text-align: center; color: #555; font-size: 0.8em;'>AskDB v1.0.0</div>", unsafe_allow_html=True)
