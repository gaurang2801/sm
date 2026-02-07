"""
Custom CSS styles for the Buying & Selling Dashboard Application.
Clean, professional design.
"""

import streamlit as st


def inject_custom_css() -> None:
    """Inject custom CSS styles into the Streamlit app."""
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global font */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main background */
        .stApp {
            background: #f8fafc;
        }
        
        /* Sidebar styling - Light theme */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
            border-right: 1px solid #e2e8f0;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            color: #1e293b;
        }
        
        [data-testid="stSidebar"] hr {
            border-color: #cbd5e1;
        }
        
        /* Radio buttons in sidebar */
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.25rem;
        }
        
        [data-testid="stSidebar"] .stRadio label {
            background: white;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 2px 0;
            transition: all 0.2s;
            color: #475569 !important;
            border: 1px solid #e2e8f0;
        }
        
        [data-testid="stSidebar"] .stRadio label:hover {
            background: #f1f5f9;
            border-color: #3b82f6;
        }
        
        [data-testid="stSidebar"] .stRadio label[data-checked="true"] {
            background: #3b82f6;
            color: white !important;
            border-color: #3b82f6;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        
        /* Download button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }
        
        /* Form inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
        
        /* Dataframe */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        
        .stTabs [aria-selected="true"] {
            background: #3b82f6;
            color: white;
        }
        
        /* Forms */
        [data-testid="stForm"] {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }
        
        /* Metrics */
        [data-testid="stMetric"] {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
        }
        
        /* Alert boxes */
        .stAlert {
            border-radius: 8px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
    </style>
    """, unsafe_allow_html=True)
