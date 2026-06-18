def get_custom_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body {
        font-family: 'Outfit', sans-serif;
    }

    /* Dark background */
    .stApp {
        background-color: #0a0a0f;
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #0a0a0f 70%);
        color: #e0e0e0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 20, 0.6);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Gradients for headings */
    h1, h2, h3 {
        background: linear-gradient(90deg, #b026ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(5px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
        border-color: rgba(0, 212, 255, 0.2);
    }
    
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        color: #e2e8f0;
        font-size: 1.05rem;
    }

    /* Input Field */
    .stChatInput {
        background-color: rgba(15, 15, 20, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        transition: all 0.3s ease !important;
    }
    .stChatInput:focus-within {
        border-color: #b026ff !important;
        box-shadow: 0 0 15px rgba(176, 38, 255, 0.3) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7012ce, #008eb3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #8a1be6, #00b4e3);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
        transform: scale(1.02);
    }
    
    /* Metric Cards / Insights */
    .insight-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        backdrop-filter: blur(10px);
        border-left: 4px solid #00d4ff;
        transition: all 0.3s;
    }
    .insight-card:hover {
        background: rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .insight-icon {
        font-size: 1.2rem;
        margin-right: 8px;
    }
    
    /* Dataframe dark theme overrides */
    [data-testid="stDataFrame"] {
        background: rgba(10, 10, 15, 0.8);
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 8px;
        backdrop-filter: blur(5px);
    }
    

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a0f;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4);
    }
    
    /* Schema badge */
    .schema-badge {
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 0.75rem;
        margin-left: 6px;
    }
    </style>
    """

def get_sql_highlight_css() -> str:
    return """
    <style>
    code[class*="language-sql"] {
        background: #1e1e2e !important;
        color: #cdd6f4 !important;
        text-shadow: none !important;
        font-family: 'Consolas', 'Monaco', monospace !important;
    }
    /* Syntax highlighting */
    .token.keyword { color: #cba6f7 !important; }
    .token.string { color: #a6e3a1 !important; }
    .token.number { color: #fab387 !important; }
    .token.operator { color: #89dceb !important; }
    .token.punctuation { color: #9399b2 !important; }
    .token.function { color: #89b4fa !important; }
    </style>
    """
