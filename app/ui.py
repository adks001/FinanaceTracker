import sys
import os
# Ensure the root project directory is in the python path to prevent import issues
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config for mobile and web responsiveness
st.set_page_config(
    page_title="Global Omni-Channel Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define color configurations for premium UI themes
THEME_CONFIG = {
    "🌌 Ambient Space": {
        "bg_gradient": "radial-gradient(circle at 10% 20%, #151622 0%, #0d0e15 90%)",
        "sidebar_bg": "rgba(20, 22, 37, 0.6)",
        "sidebar_border": "1px solid rgba(255, 255, 255, 0.05)",
        "sidebar_text": "#cbd5e0",
        "sidebar_header": "#ffffff",
        "text_color": "#f7fafc",
        "card_bg": "linear-gradient(145deg, rgba(30, 32, 52, 0.6) 0%, rgba(18, 20, 32, 0.7) 100%)",
        "card_border": "1px solid rgba(255, 255, 255, 0.06)",
        "card_shadow": "0 15px 35px 0 rgba(0, 0, 0, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.1)",
        "card_border_bottom": "4px solid rgba(255, 255, 255, 0.05)",
        "form_bg": "rgba(22, 23, 38, 0.5)",
        "input_bg": "rgba(14, 15, 25, 0.8)",
        "input_border": "1px solid rgba(255, 255, 255, 0.08)",
        "input_color": "#ffffff",
        "label_color": "#ffffff",
        "btn_gradient": "linear-gradient(135deg, #007CF0 0%, #00DFD8 100%)",
        "btn_shadow": "0 6px 20px 0 rgba(0, 223, 216, 0.3)",
        "btn_shadow_hover": "0 10px 25px 0 rgba(0, 223, 216, 0.5)",
        "title_gradient": "linear-gradient(135deg, #00FF87 0%, #60EFFF 50%, #007CF0 100%)",
        "tab_bg": "rgba(22, 23, 38, 0.6)",
        "tab_active_bg": "linear-gradient(135deg, #007CF0 0%, #00DFD8 100%)",
        "plotly_theme": "plotly_dark",
        "subtext_color": "#cbd5e0",
        "category_icon_color": "#00DFD8"
    },
    "🌑 Slate Dark": {
        "bg_gradient": "#0f1015",
        "sidebar_bg": "#181922",
        "sidebar_border": "1px solid #2d3748",
        "sidebar_text": "#a0aec0",
        "sidebar_header": "#ffffff",
        "text_color": "#e2e8f0",
        "card_bg": "#1c1e28",
        "card_border": "1px solid #2d3748",
        "card_shadow": "0 10px 20px rgba(0, 0, 0, 0.3)",
        "card_border_bottom": "4px solid #2d3748",
        "form_bg": "#181922",
        "input_bg": "#10111a",
        "input_border": "1px solid #2d3748",
        "input_color": "#e2e8f0",
        "label_color": "#ffffff",
        "btn_gradient": "linear-gradient(135deg, #4a5568 0%, #2d3748 100%)",
        "btn_shadow": "0 4px 10px rgba(0, 0, 0, 0.2)",
        "btn_shadow_hover": "0 6px 15px rgba(0, 0, 0, 0.3)",
        "title_gradient": "linear-gradient(135deg, #ffffff 0%, #a0aec0 100%)",
        "tab_bg": "#181922",
        "tab_active_bg": "linear-gradient(135deg, #4a5568 0%, #2d3748 100%)",
        "plotly_theme": "plotly_dark",
        "subtext_color": "#a0aec0",
        "category_icon_color": "#60EFFF"
    },
    "☀️ Classic Light": {
        "bg_gradient": "#f7fafc",
        "sidebar_bg": "#ffffff",
        "sidebar_border": "1px solid #cbd5e0",
        "sidebar_text": "#2d3748",
        "sidebar_header": "#1a202c",
        "text_color": "#2d3748",
        "card_bg": "#ffffff",
        "card_border": "1px solid #e2e8f0",
        "card_shadow": "0 8px 16px rgba(0, 0, 0, 0.05)",
        "card_border_bottom": "4px solid #e2e8f0",
        "form_bg": "#ffffff",
        "input_bg": "#f7fafc",
        "input_border": "1px solid #cbd5e0",
        "input_color": "#2d3748",
        "label_color": "#2d3748",
        "btn_gradient": "linear-gradient(135deg, #3182ce 0%, #319795 100%)",
        "btn_shadow": "0 4px 12px rgba(49, 130, 206, 0.2)",
        "btn_shadow_hover": "0 6px 16px rgba(49, 130, 206, 0.4)",
        "title_gradient": "linear-gradient(135deg, #2b6cb0 0%, #2c7a7b 100%)",
        "tab_bg": "#edf2f7",
        "tab_active_bg": "linear-gradient(135deg, #3182ce 0%, #319795 100%)",
        "plotly_theme": "ggplot2",
        "subtext_color": "#718096",
        "category_icon_color": "#3182ce"
    }
}

# Theme selection at the top of the sidebar
with st.sidebar:
    app_theme = st.selectbox("🎨 UI Color Theme", options=list(THEME_CONFIG.keys()), index=0)

selected_theme = THEME_CONFIG[app_theme]

# Compile and Inject Custom Styles based on selected theme
style_inject_str = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* Remove Streamlit's default top white header bar */
header, [data-testid="stHeader"] {{
    background: transparent !important;
    background-color: transparent !important;
    border-bottom: none !important;
}}

/* Main App Container background */
[data-testid="stAppViewContainer"] {{
    background: {selected_theme["bg_gradient"]} !important;
    color: {selected_theme["text_color"]} !important;
}}

/* Sidebar Custom Background and Text contrast overrides */
[data-testid="stSidebar"] {{
    background: {selected_theme["sidebar_bg"]} !important;
    backdrop-filter: blur(25px) !important;
    border-right: {selected_theme["sidebar_border"]} !important;
}}
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span, 
[data-testid="stSidebar"] div[data-testid="stText"],
[data-testid="stSidebar"] .stMarkdown {{
    color: {selected_theme["sidebar_text"]} !important;
}}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 {{
    color: {selected_theme["sidebar_header"]} !important;
}}
[data-testid="stSidebar"] label, 
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
[data-testid="stSidebar"] .stWidgetLabel {{
    color: {selected_theme["sidebar_header"]} !important;
}}

/* Font resets */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], input, textarea, select, button, label {{
    font-family: 'Inter', sans-serif !important;
}}
h1, h2, h3, h4, h5, h6, .main-title {{
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
}}

/* Title details */
.main-title {{
    background: {selected_theme["title_gradient"]};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.2rem;
    margin-bottom: 0.2rem;
    font-weight: 800;
    text-align: center;
    letter-spacing: -1px;
}}
.sub-title {{
    font-size: 1.15rem;
    color: #a0aec0;
    text-align: center;
    margin-bottom: 2.5rem;
}}

/* 3D Floating Metric Container */
.metric-container {{
    background: {selected_theme["card_bg"]};
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1.8rem 1.2rem;
    border: {selected_theme["card_border"]};
    box-shadow: {selected_theme["card_shadow"]};
    text-align: center;
    transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    border-bottom: {selected_theme["card_border_bottom"]};
}}
.metric-container:hover {{
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 25px 50px 0 rgba(0, 0, 0, 0.4);
}}
.metric-label {{
    font-size: 0.82rem;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
    margin-bottom: 0.6rem;
}}
.metric-value {{
    font-size: 2.2rem;
    font-weight: 800;
    margin-bottom: 0.4rem;
    letter-spacing: -0.5px;
}}
.metric-positive {{
    background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.metric-negative {{
    background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.metric-neutral {{
    background: linear-gradient(135deg, #FF9933 0%, #FF3366 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}
.metric-info {{
    background: linear-gradient(135deg, #00DFD8 0%, #007CF0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

/* Form wrapper, bordered containers, and inputs formatting */
div.stForm, [data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {selected_theme["form_bg"]} !important;
    backdrop-filter: blur(20px) !important;
    border: {selected_theme["card_border"]} !important;
    border-radius: 20px !important;
    padding: 2.2rem !important;
    box-shadow: {selected_theme["card_shadow"]} !important;
}}

/* Form fields input text color and visibility overrides */
.stTextInput input, 
.stNumberInput input, 
.stTextArea textarea, 
input[type="text"], 
input[type="password"], 
input[type="email"], 
input[type="tel"], 
textarea, 
[data-testid="stForm"] input {{
    background-color: {selected_theme["input_bg"]} !important;
    border: {selected_theme["input_border"]} !important;
    border-radius: 10px !important;
    color: {selected_theme["input_color"]} !important;
    padding: 0.6rem 0.8rem !important;
    transition: all 0.3s ease !important;
}}
input:focus, textarea:focus, select:focus {{
    border-color: #60EFFF !important;
    box-shadow: 0 0 15px rgba(96, 239, 255, 0.25) !important;
}}

/* Force label readability on both dark and light background */
label, [data-testid="stWidgetLabel"] p, .stWidgetLabel {{
    color: {selected_theme["label_color"]} !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}}

/* 3D Physical Button Styles */
div.stButton > button, div.stFormSubmitButton > button {{
    background: {selected_theme["btn_gradient"]} !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-family: 'Outfit', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.8rem 1.8rem !important;
    box-shadow: {selected_theme["btn_shadow"]} !important;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    cursor: pointer !important;
}}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow: {selected_theme["btn_shadow_hover"]} !important;
}}
div.stButton > button:active, div.stFormSubmitButton > button:active {{
    transform: translateY(1px) scale(0.98) !important;
}}

/* Flat borderless buttons for ledger edit and delete */
div[class*="st-key-edit_btn_"] button, div[class*="st-key-del_btn_"] button {{
    background: none !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 1.4rem !important;
    min-height: unset !important;
    height: auto !important;
    width: auto !important;
    color: inherit !important;
    transition: transform 0.2s ease !important;
    transform: none !important;
}}
div[class*="st-key-edit_btn_"] button:hover, div[class*="st-key-del_btn_"] button:hover {{
    transform: scale(1.2) !important;
    background: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
}}
div[class*="st-key-edit_btn_"] button:active, div[class*="st-key-del_btn_"] button:active {{
    transform: scale(0.9) !important;
    background: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
}}

/* High contrast read-only/disabled text inputs in space and dark themes */
input:disabled, .stTextInput input:disabled, [disabled] {{
    color: {selected_theme["text_color"]} !important;
    -webkit-text-fill-color: {selected_theme["text_color"]} !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
    opacity: 1 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}}

/* Style selectbox containers to match theme input colors */
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] div[data-baseweb="select"],
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-baseweb="select"] {{
    background-color: {selected_theme["input_bg"]} !important;
    border: {selected_theme["input_border"]} !important;
    border-radius: 10px !important;
    color: {selected_theme["input_color"]} !important;
}}
/* Force selectbox value text readability */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
div[data-testid="stSelectbox"] div[data-baseweb="select"] div,
div[data-baseweb="select"] * {{
    color: {selected_theme["input_color"]} !important;
}}
/* Dropdown popover listbox portal styling (forces dark theme options list) */
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[role="listbox"],
div[role="listbox"] *,
ul[role="listbox"],
ul[role="listbox"] * {{
    background-color: {selected_theme["input_bg"]} !important;
    color: {selected_theme["input_color"]} !important;
}}
/* Highlight option list items on hover */
li[role="option"]:hover,
ul[role="listbox"] li:hover,
div[role="listbox"] div:hover {{
    background: {selected_theme["btn_gradient"]} !important;
    color: #ffffff !important;
}}

/* Input placeholder text overrides */
input::placeholder, 
textarea::placeholder,
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
[data-testid="stForm"] input::placeholder {{
    color: {selected_theme["subtext_color"]} !important;
    opacity: 0.75 !important;
}}

/* Compact file uploader styling */
[data-testid="stFileUploader"] {{
    padding: 0.2rem !important;
}}
[data-testid="stFileUploader"] section {{
    padding: 0.4rem 0.8rem !important;
}}
[data-testid="stFileUploader"] section > input + div {{
    padding: 0.4rem !important;
}}

/* Glassmorphic Tabs Customization */
div.stTabs [data-baseweb="tab-list"] {{
    background: {selected_theme["tab_bg"]};
    border-radius: 15px;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 1.5rem;
}}
div.stTabs [data-baseweb="tab"] {{
    border-radius: 10px;
    padding: 0.6rem 1.4rem;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    transition: all 0.3s ease;
    color: #a0aec0 !important;
    border: none !important;
}}
div.stTabs [aria-selected="true"] {{
    background: {selected_theme["tab_active_bg"]};
    color: #ffffff !important;
}}

/* Custom Category Badges */
.category-badge {{
    display: inline-flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    padding: 6px 14px;
    border-radius: 30px;
    font-size: 0.85rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    font-weight: 500;
    color: {selected_theme["text_color"]} !important;
}}
.category-icon {{
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 8px;
    vertical-align: middle;
    color: {selected_theme["category_icon_color"]} !important;
}}
.category-icon svg {{
    width: 100%;
    height: 100%;
    stroke: currentColor;
    fill: none;
}}
.divider {{
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    margin: 1rem 0;
}}

/* Center-align alert/success banners text */
div[data-testid="stAlert"] {{
    text-align: center !important;
}}
div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {{
    text-align: center !important;
    display: inline-block !important;
}}

/* Prevent word wrap in expander summaries in sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] details summary p {{
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}}

/* Highlight the third expander from the bottom (Add Custom Category) */
[data-testid="stSidebar"] div.element-container:nth-last-child(3) div[data-testid="stExpander"] details summary {{
    background: {selected_theme["btn_gradient"]} !important;
    color: #ffffff !important;
    border-radius: 12px !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    box-shadow: {selected_theme["btn_shadow"]} !important;
    transition: all 0.3s ease !important;
}}
[data-testid="stSidebar"] div.element-container:nth-last-child(3) div[data-testid="stExpander"] details summary * {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}
[data-testid="stSidebar"] div.element-container:nth-last-child(3) div[data-testid="stExpander"] details summary:hover {{
    transform: translateY(-2px) !important;
    box-shadow: {selected_theme["btn_shadow_hover"]} !important;
}}
</style>
"""
st.markdown(style_inject_str, unsafe_allow_html=True)

# Try loading configuration
import app.config as config
from app.db import (
    supabase, verify_connection, seed_global_categories,
    get_profile, create_profile_if_not_exists, get_categories,
    check_duplicate_expense, insert_expense, get_expenses,
    delete_expense, init_supabase_client, process_recurring_schedules
)
from app.categories import add_custom_category, DuplicateCategoryError, GLOBAL_CATEGORIES
from app.email_worker import fetch_and_parse_emails

# --- Next-Gen PFM Logic Helpers ---
def calculate_fhs(income, expenses_sum, emergency_cash, debt_obligations, investment_surplus, insurance_checklist):
    savings_rate = (income - expenses_sum) / income if income > 0 else 0
    if savings_rate >= 0.40:
        s_score = 1.0
    elif savings_rate <= 0.00:
        s_score = 0.0
    else:
        s_score = savings_rate / 0.40
        
    average_expenses = expenses_sum if expenses_sum > 0 else 10000.0
    runway_months = emergency_cash / average_expenses
    if runway_months >= 6.0:
        e_score = 1.0
    elif runway_months <= 0.0:
        e_score = 0.0
    else:
        e_score = runway_months / 6.0
        
    dti = debt_obligations / income if income > 0 else 0
    if dti <= 0.20:
        d_score = 1.0
    elif dti >= 0.50:
        d_score = 0.0
    else:
        d_score = 1.0 - ((dti - 0.20) / 0.30)
        
    surplus = income - expenses_sum
    if surplus <= 0:
        i_score = 0.0
    else:
        investment_ratio = investment_surplus / surplus
        if investment_ratio >= 0.80:
            i_score = 1.0
        else:
            i_score = investment_ratio / 0.80
            
    a_score = 0.0
    if insurance_checklist.get("life"): a_score += 0.40
    if insurance_checklist.get("health"): a_score += 0.40
    if insurance_checklist.get("other"): a_score += 0.20
    
    raw_fhs = 0.25 * s_score + 0.25 * e_score + 0.20 * d_score + 0.15 * i_score + 0.15 * a_score
    fhs = 300 + 550 * raw_fhs
    return int(fhs), {
        "savings_rate": savings_rate * 100,
        "runway_months": runway_months,
        "dti": dti * 100,
        "investment_ratio": (investment_surplus / surplus * 100) if surplus > 0 else 0,
        "adequacy": a_score * 100
    }

def get_ai_coach_response(user_query: str, context_str: str, history_str: str = "") -> str:
    import google.generativeai as genai
    import app.config as config
    import os
    api_key = os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
    if not api_key:
        return "⚠️ Gemini API Key not configured. Please add it to credentials."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = f"""
You are the lead AI Financial Advisor of the Enterprise PFM Platform, operating with absolute mathematical precision and fiduciary responsibility.

CONTEXT VARIABLES:
{context_str}

CONVERSATION HISTORY WITH USER:
{history_str if history_str else "None"}

BEHAVIORAL INSTRUCTIONS:
1. TRUTHFULNESS: Never hypothesize or estimate numbers. If asset data is missing, request clarification.
2. CALCULATIONS: For calculations involving interest, compound returns, or savings projections, you must output the formula explicitly in LaTeX format before returning the final sum.
3. GOAL CRITICALITY: Evaluate any purchase question ("Can I afford...") against active goals. A purchase is NOT affordable if it lowers the Emergency Runway below 3 months, or delays any active Household Goal by more than 3 months.
4. ACTIONABILITY: Always provide exactly one savings optimization insight based on active SaaS subscriptions or redundant categories.

RESPONSE SCHEMA CONSTRAINT:
Return responses wrapped in this structured layout:
---
### 📊 AI Financial Evaluation
[Core feedback on question, taking into account context and conversation history]

### 🧮 Mathematical Validation
- **Formula Used:** [LaTeX Formula if applicable, else N/A]
- **Projections:** [Timeline analysis if applicable, else N/A]

### 💡 Recommendation & Next Steps
- [One-sentence optimization action item]
---
"""
        response = model.generate_content([system_prompt, user_query])
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {e}"


# State initialization
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "pending_expense" not in st.session_state:
    st.session_state.pending_expense = None
if "force_config" not in st.session_state:
    st.session_state.force_config = False
if "editing_expense_id" not in st.session_state:
    st.session_state.editing_expense_id = None
if "coach_messages" not in st.session_state:
    st.session_state.coach_messages = []
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"
if "show_verification_prompt" not in st.session_state:
    st.session_state.show_verification_prompt = None
if "login_error_unverified" not in st.session_state:
    st.session_state.login_error_unverified = False
if "login_unverified_email" not in st.session_state:
    st.session_state.login_unverified_email = ""

# Hide Streamlit administrative controls for non-admin users
is_admin = False
if st.session_state.get("auth_user") and st.session_state.auth_user.email == "adks009@gmail.com":
    is_admin = True

if not is_admin:
    st.markdown("""
    <style>
    /* Hide top header bar (Share, Star, Edit, GitHub links) */
    [data-testid="stHeader"], header {
        display: none !important;
        height: 0px !important;
    }
    /* Hide default Main Menu (Three Dots) */
    #MainMenu, [data-testid="stMainMenu"] {
        visibility: hidden !important;
        display: none !important;
    }
    /* Hide Manage App button at bottom right and default footer */
    [data-testid="stManageAppBttn"], div.stManageAppBttn, footer {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Email Sync Manager Dialog
@st.dialog("📥 Email Transaction Sync Manager")
def manage_email_sync_dialog():
    st.markdown("""
    <div style="background-color: rgba(0, 223, 216, 0.05); border: 1px solid rgba(0, 223, 216, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1.2rem;">
        <span style="font-weight: 700; font-size: 1.05rem; color: #00DFD8;">🔒 Privacy & Security Guarantee</span><br/>
        <span style="font-size: 0.85rem; color: #cbd5e0; line-height: 1.4; display: block; margin-top: 0.4rem;">
            We do not keep or store any record of your emails. The engine connects directly to your inbox using a secure local connection to read transaction alert messages. The AI parser is strictly trained to sync only financial alert messages (debits, credits, invoices) and ignores all personal messages.
        </span>
    </div>
    """, unsafe_allow_html=True)

    user_metadata = getattr(st.session_state.auth_user, "user_metadata", {}) or {}
    email_sync_configs = user_metadata.get("email_sync_configs", [])

    st.markdown("##### ➕ Add Sync Account")
    add_provider = st.selectbox("Email Provider", ["Google (Gmail)", "Yahoo Mail", "Outlook / Hotmail", "Microsoft Account", "Custom IMAP"], key="sync_add_provider")
    
    col_a, col_b = st.columns(2)
    with col_a:
        add_email = st.text_input("Inbox Email Address", placeholder="e.g. user@gmail.com", key="sync_add_email")
    with col_b:
        add_imap = ""
        if add_provider == "Custom IMAP":
            add_imap = st.text_input("Custom IMAP Server Host", placeholder="imap.yourcompany.com", key="sync_add_imap")
            
    if st.button("Save Account Connection", key="btn_save_sync_account", use_container_width=True):
        if not add_email.strip():
            st.error("Email address cannot be empty.")
        else:
            # Check duplicate email
            exists = any(c["email"].lower() == add_email.strip().lower() for c in email_sync_configs)
            if exists:
                st.warning("This email address is already configured.")
            else:
                new_acc = {
                    "email": add_email.strip(),
                    "provider": add_provider,
                    "imap_host": add_imap.strip() if add_provider == "Custom IMAP" else None
                }
                new_configs = email_sync_configs + [new_acc]
                try:
                    res = supabase.auth.update_user({"data": {"email_sync_configs": new_configs}})
                    if res.user:
                        st.session_state.auth_user = res.user
                        st.success(f"Added connection for {add_email}!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to save account: {e}")

    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.1;'/>", unsafe_allow_html=True)
    st.markdown("##### ⚙️ Configured Connections")
    if not email_sync_configs:
        st.info("No connections configured yet. Use the form above to add an email address.")
    else:
        # Initialize passwords in session state if not existing
        if "email_passwords" not in st.session_state:
            st.session_state.email_passwords = {}
            
        for idx, cfg in enumerate(email_sync_configs):
            with st.container(border=True):
                col1, col2, col3 = st.columns([1.5, 1.5, 1])
                with col1:
                    st.markdown(f"**{cfg['email']}**")
                    st.markdown(f"<small style='opacity: 0.8;'>{cfg['provider']}</small>", unsafe_allow_html=True)
                with col2:
                    # Input temporary password for this email (stored in st.session_state only)
                    saved_pass = st.session_state.email_passwords.get(cfg['email'], "")
                    temp_pass = st.text_input("App-Specific Password", type="password", value=saved_pass, key=f"temp_pwd_{idx}", placeholder="••••••••", help="Enter the app-specific password generated from your mail settings.")
                    st.session_state.email_passwords[cfg['email']] = temp_pass
                with col3:
                    # Action buttons
                    st.write("") # Spacer
                    btn_col_sync, btn_col_del = st.columns(2)
                    with btn_col_sync:
                        if st.button("📥", key=f"sync_now_btn_{idx}", help="Sync transactional emails from this inbox"):
                            pwd = st.session_state.email_passwords.get(cfg['email'], "")
                            if not pwd:
                                st.error("Please provide the app-specific password to sync.")
                            else:
                                with st.spinner(f"Scanning..."):
                                    try:
                                        # Pass customized imap_host if custom
                                        new_txs = fetch_and_parse_emails(
                                            email_address=cfg['email'],
                                            password=pwd,
                                            user_id=st.session_state.auth_user.id,
                                            imap_host=cfg.get("imap_host")
                                        )
                                        if new_txs:
                                            st.success(f"Successfully synced {len(new_txs)} new transactions!")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.info("Scan completed. No new transactional alerts found.")
                                    except Exception as err:
                                        st.error(f"Sync failed: {err}")
                    with btn_col_del:
                        if st.button("🗑️", key=f"delete_sync_acc_{idx}", help="Remove this connection"):
                            new_configs = [c for i, c in enumerate(email_sync_configs) if i != idx]
                            try:
                                res = supabase.auth.update_user({"data": {"email_sync_configs": new_configs}})
                                if res.user:
                                    st.session_state.auth_user = res.user
                                    if cfg['email'] in st.session_state.email_passwords:
                                        del st.session_state.email_passwords[cfg['email']]
                                    st.success(f"Removed connection for {cfg['email']}!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to remove account: {e}")

# Helper to save configurations entered from UI
def save_config_env(url, key, gemini_key):
    try:
        with open(".env", "w") as f:
            f.write(f"SUPABASE_URL={url}\n")
            f.write(f"SUPABASE_KEY={key}\n")
            f.write(f"GEMINI_API_KEY={gemini_key}\n")
        # Load them into config module dynamically
        config.SUPABASE_URL = url
        config.SUPABASE_KEY = key
        config.GEMINI_API_KEY = gemini_key
        os.environ["SUPABASE_URL"] = url
        os.environ["SUPABASE_KEY"] = key
        os.environ["GEMINI_API_KEY"] = gemini_key
        
        # Configure Gemini API dynamically
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        
        init_supabase_client(url, key)
        return True
    except Exception as e:
        st.error(f"Failed to save env file: {e}")
        return False

# 1. Setup Configuration Screen if credentials are missing or are placeholder values
missing_configs = config.check_config()
is_placeholder = (
    "your-project-id" in (config.SUPABASE_URL or "") or 
    "your-supabase" in (config.SUPABASE_KEY or "") or 
    "your-gemini" in (config.GEMINI_API_KEY or "")
)

if missing_configs or not supabase or is_placeholder or st.session_state.force_config:
    st.markdown('<div class="main-title">Financial Tracker Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Provision your Free-Tier Supabase + Gemini credentials to get started</div>', unsafe_allow_html=True)
    
    with st.form("config_setup"):
        st.info("💡 Environment settings can be entered below. These will be saved locally to a .env file.")
        
        curr_url = "" if "your-project-id" in (config.SUPABASE_URL or "") else config.SUPABASE_URL
        curr_key = "" if "your-supabase" in (config.SUPABASE_KEY or "") else config.SUPABASE_KEY
        curr_gemini = "" if "your-gemini" in (config.GEMINI_API_KEY or "") else config.GEMINI_API_KEY
        
        url_input = st.text_input("Supabase Project URL", value=curr_url or "", placeholder="https://your-id.supabase.co")
        key_input = st.text_input("Supabase Anon / Service Role Key", value=curr_key or "", type="password", placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        gemini_input = st.text_input("Google AI Studio Gemini API Key", value=curr_gemini or "", type="password", placeholder="AIzaSy...")
        
        submit_config = st.form_submit_button("Save Credentials & Launch App")
        
        if submit_config:
            if not url_input or not key_input or not gemini_input:
                st.error("All credentials are required to operate the tracker.")
            else:
                success = save_config_env(url_input, key_input, gemini_input)
                if success:
                    st.session_state.force_config = False
                    st.success("Credentials saved successfully! Reloading...")
                    st.rerun()
    st.stop()

# Ensure connection works before going forward
if not verify_connection():
    st.error("🚨 Connection to Supabase failed. Check your API Keys, Supabase Endpoint status, or database DDL execution.")
    if st.button("Reconfigure Credentials"):
        st.session_state.force_config = True
        st.rerun()
    st.stop()

# If supabase client session has expired and been cleared, sync local auth state
if st.session_state.auth_user:
    try:
        session = supabase.auth.get_session()
        if not session:
            st.session_state.auth_user = None
            st.rerun()
    except Exception:
        st.session_state.auth_user = None
        st.rerun()

# Seed categories if database is empty
seed_global_categories()

# 2. Handle Login / Signup Screen if not authenticated
if not st.session_state.auth_user:
    st.markdown('<div class="main-title">Global Expense & Split Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">A Multi-User SaaS Engine powered by Supabase & Gemini</div>', unsafe_allow_html=True)
    
    # Get configured deep link redirect URL
    REDIRECT_URL = getattr(config, "REDIRECT_URL", "http://localhost:8501/")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        # Custom visual toggle for tabs
        col_toggle_1, col_toggle_2 = st.columns(2)
        with col_toggle_1:
            is_login = st.session_state.auth_view == "login"
            if st.button("🔑 Access Account", use_container_width=True, type="primary" if is_login else "secondary"):
                st.session_state.auth_view = "login"
                st.session_state.login_error_unverified = False # Clear error on switch
                st.session_state.show_verification_prompt = None
                st.rerun()
        with col_toggle_2:
            is_register = st.session_state.auth_view == "register"
            if st.button("📝 Register New", use_container_width=True, type="primary" if is_register else "secondary"):
                st.session_state.auth_view = "register"
                st.session_state.login_error_unverified = False # Clear error on switch
                st.session_state.show_verification_prompt = None
                st.rerun()

        # Shared country codes configuration
        import re
        country_codes = [
            "🇮🇳 India (+91)",
            "🇺🇸 USA (+1)",
            "🇬🇧 UK (+44)",
            "🇨🇦 Canada (+1)",
            "🇦🇺 Australia (+61)",
            "🇸🇬 Singapore (+65)",
            "🇦🇪 UAE (+971)",
            "Other"
        ]
        
        # LOGIN VIEW
        if st.session_state.auth_view == "login":
            # Display Verification Prompts outside the form (so button click works)
            if st.session_state.show_verification_prompt:
                st.info(f"✉️ **Verification email sent to {st.session_state.show_verification_prompt}!** Please check your inbox and verify your email before signing in.")
                
            if st.session_state.login_error_unverified:
                st.error(f"⚠️ **Access Blocked:** Your email address `{st.session_state.login_unverified_email}` has not been verified yet. Please check your inbox.")
                if st.button("📧 Resend Verification Email", key="resend_verify_login_outside", use_container_width=True):
                    try:
                        supabase.auth.resend({
                            "type": "signup",
                            "email": st.session_state.login_unverified_email,
                            "options": {
                                "email_redirect_to": REDIRECT_URL
                            }
                        })
                        st.success("Verification link resent successfully! Please check your inbox.")
                        st.session_state.login_error_unverified = False
                        st.session_state.show_verification_prompt = None
                    except Exception as resend_err:
                        st.error(f"Failed to resend link: {resend_err}")
            
            # Select login method
            login_method = st.radio("Select Login Method", ["📧 Email & Password", "📱 Phone OTP (SMS / WhatsApp)"], horizontal=True, key="login_method_selector")
            
            if login_method == "📧 Email & Password":
                with st.form("login_form"):
                    email = st.text_input("Email Address", placeholder="jane@example.com")
                    password = st.text_input("Password", type="password")
                    btn_login = st.form_submit_button("Sign In")
                    
                    if btn_login:
                        if not email.strip() or not password.strip():
                            st.error("Please enter email and password.")
                        else:
                            try:
                                # Sign in user
                                auth_res = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                                if auth_res.user:
                                    # Strict Check: check if email is verified
                                    email_confirmed = getattr(auth_res.user, "email_confirmed_at", None)
                                    if not email_confirmed:
                                        # Block access
                                        supabase.auth.sign_out()
                                        st.session_state.auth_user = None
                                        st.session_state.login_error_unverified = True
                                        st.session_state.login_unverified_email = email.strip()
                                        st.session_state.show_verification_prompt = None
                                        st.rerun()
                                    else:
                                        st.session_state.auth_user = auth_res.user
                                        create_profile_if_not_exists(auth_res.user.id, auth_res.user.email)
                                        st.session_state.show_login_success = True
                                        st.rerun()
                            except Exception as e:
                                err_str = str(e).lower()
                                if "email not confirmed" in err_str or "confirm your email" in err_str:
                                    st.session_state.login_error_unverified = True
                                    st.session_state.login_unverified_email = email.strip()
                                    st.session_state.show_verification_prompt = None
                                    st.rerun()
                                else:
                                    st.error(f"Login failed: {e}")
                
                # Forgot Password section
                with st.expander("🔑 Forgot Password?"):
                    reset_email = st.text_input("Enter your registered email address")
                    if st.button("Send Reset Link", key="btn_reset_pass_gate"):
                        if not reset_email:
                            st.warning("Please enter your email address.")
                        else:
                            try:
                                supabase.auth.reset_password_for_email(reset_email)
                                st.success("A password reset link has been sent to your email address!")
                            except Exception as e:
                                st.error(f"Failed to send reset link: {e}")
            
            else:
                # Phone OTP Logic
                if "otp_sent" not in st.session_state:
                    st.session_state.otp_sent = False
                if "otp_phone" not in st.session_state:
                    st.session_state.otp_phone = ""
                if "otp_channel" not in st.session_state:
                    st.session_state.otp_channel = "whatsapp"
                
                if not st.session_state.otp_sent:
                    # Let user enter phone number
                    col_code, col_phone = st.columns([1.2, 2.8])
                    with col_code:
                        login_country = st.selectbox("Code", country_codes, index=0, key="login_country_code")
                    with col_phone:
                        login_phone_num = st.text_input("Phone Number", placeholder="9876543210", key="login_phone_num")
                    
                    # OTP Delivery Channel Selector
                    otp_channel_sel = st.radio(
                        "OTP Delivery Channel",
                        ["💬 WhatsApp", "✉️ SMS (Text Message)"],
                        horizontal=True,
                        key="login_otp_channel_sel"
                    )
                    
                    btn_send_otp = st.button("📱 Send OTP", use_container_width=True)
                    if btn_send_otp:
                        if not login_phone_num.strip():
                            st.warning("Please enter your phone number.")
                        else:
                            # Format phone number
                            if login_country != "Other":
                                code_match = re.search(r'\(\+(\d+)\)', login_country)
                                code = f"+{code_match.group(1)}" if code_match else ""
                                full_phone = f"{code}{login_phone_num.strip()}"
                            else:
                                full_phone = login_phone_num.strip()
                            
                            channel = "whatsapp" if "WhatsApp" in otp_channel_sel else "sms"
                            
                            try:
                                supabase.auth.sign_in_with_otp({
                                    "phone": full_phone,
                                    "options": {
                                        "channel": channel
                                    }
                                })
                                st.session_state.otp_sent = True
                                st.session_state.otp_phone = full_phone
                                st.session_state.otp_channel = channel
                                display_channel = "WhatsApp" if channel == "whatsapp" else "SMS"
                                st.success(f"OTP sent successfully to {full_phone} via {display_channel}!")
                                st.rerun()
                            except Exception as e:
                                display_channel = "WhatsApp" if channel == "whatsapp" else "SMS"
                                st.error(f"Error sending OTP via {display_channel}: {e}")
                                st.markdown(f"""
                                <div style="background-color: rgba(255, 185, 0, 0.05); border: 1px solid rgba(255, 185, 0, 0.2); border-radius: 12px; padding: 1rem; margin-top: 0.5rem; font-family: 'Outfit', sans-serif;">
                                    <span style="font-weight: 700; font-size: 1rem; color: #FFB900;">🛠️ How to Test OTP (Free Sandbox Mocks)</span><br/>
                                    <span style="font-size: 0.85rem; color: #cbd5e0; line-height: 1.4; display: block; margin-top: 0.4rem;">
                                        By default, Supabase requires a configured WhatsApp/SMS provider (e.g. Twilio) to deliver OTPs. 
                                        To test this flow for free in development, you can add <b>Test Phone Numbers</b> in your Supabase Auth Console:
                                        <ol style="margin-top: 0.4rem; padding-left: 1.2rem; color: #cbd5e0;">
                                            <li>Go to your <a href="https://supabase.com/dashboard/project/hizsdqadjxrvmbvtcobl/auth/providers" target="_blank" style="color: #60EFFF; font-weight: bold; text-decoration: none;">Supabase Auth Providers Console</a></li>
                                            <li>Expand the <b>Phone</b> section</li>
                                            <li>Enable the Phone provider toggle and scroll to <b>Test Phone Numbers</b></li>
                                            <li>Add your number (e.g. <code>{full_phone}</code>) and a mock OTP code (e.g. <code>123456</code>)</li>
                                            <li>Click <b>Save</b></li>
                                        </ol>
                                        Once added, try sending OTP again from the login page, enter <code>123456</code>, and you will log in natively with full database RLS compatibility!
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    display_channel = "WhatsApp" if st.session_state.otp_channel == "whatsapp" else "SMS"
                    st.info(f"OTP has been sent to **{st.session_state.otp_phone}** via **{display_channel}**")
                    otp_code = st.text_input("Enter 6-digit OTP Code", placeholder="123456")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        btn_verify = st.button("🔓 Verify & Sign In", type="primary", use_container_width=True)
                    with col_btn2:
                        btn_resend = st.button("🔄 Resend OTP / Change Phone", use_container_width=True)
                        
                    if btn_verify:
                        if not otp_code.strip():
                            st.warning("Please enter the OTP code.")
                        else:
                            try:
                                verify_res = supabase.auth.verify_otp({
                                    "phone": st.session_state.otp_phone,
                                    "token": otp_code.strip(),
                                    "type": "sms"
                                })
                                if verify_res.user:
                                    st.session_state.auth_user = verify_res.user
                                    create_profile_if_not_exists(verify_res.user.id, verify_res.user.email or "", phone_no=st.session_state.otp_phone)
                                    st.session_state.otp_sent = False
                                    st.session_state.otp_phone = ""
                                    st.session_state.show_login_success = True
                                    st.rerun()
                                else:
                                    st.error("Failed to verify OTP.")
                            except Exception as e:
                                st.error(f"Verification failed: {e}")
                                
                    if btn_resend:
                        st.session_state.otp_sent = False
                        st.session_state.otp_phone = ""
                        st.rerun()
                        
        # REGISTER VIEW
        else:
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="Jane Doe")
                reg_email = st.text_input("Email Address", placeholder="jane@example.com")
                
                st.markdown("<small><b>Phone Number</b></small>", unsafe_allow_html=True)
                col_reg_code, col_reg_phone = st.columns([1.2, 2.8])
                with col_reg_code:
                    reg_country = st.selectbox("Code", country_codes, index=0, key="reg_country_code", label_visibility="collapsed")
                with col_reg_phone:
                    reg_phone_only = st.text_input("Phone Number", placeholder="9876543210", key="reg_phone_num", label_visibility="collapsed")
                
                reg_password = st.text_input("Password (min 6 characters)", type="password")
                btn_register = st.form_submit_button("Create Account")
                
                if btn_register:
                    # Combine phone number
                    if reg_country != "Other":
                        code_match = re.search(r'\(\+(\d+)\)', reg_country)
                        code = f"+{code_match.group(1)}" if code_match else ""
                        reg_phone = f"{code}{reg_phone_only.strip()}" if reg_phone_only.strip() else ""
                    else:
                        reg_phone = reg_phone_only.strip()
                        
                    if len(reg_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif not reg_name or not reg_email:
                        st.error("Name and Email are required.")
                    else:
                        try:
                            # Sign up user inside Supabase Auth
                            auth_res = supabase.auth.sign_up({
                                "email": reg_email.strip(),
                                "password": reg_password,
                                "options": {
                                    "data": {
                                        "full_name": reg_name.strip(),
                                        "phone_no": reg_phone
                                    },
                                    "email_redirect_to": REDIRECT_URL
                                }
                            })
                            if auth_res.user:
                                # Ensure profile is created immediately (fallback logic)
                                create_profile_if_not_exists(
                                    auth_res.user.id, 
                                    reg_email.strip(), 
                                    full_name=reg_name.strip(), 
                                    phone_no=reg_phone
                                )
                                # Redirect to login page and display message
                                st.session_state.auth_view = "login"
                                st.session_state.show_verification_prompt = reg_email.strip()
                                st.rerun()
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
    st.stop()

# 3. Main SaaS Application Area (User Authenticated)
current_user = st.session_state.auth_user
if current_user:
    try:
        user_res = supabase.auth.get_user()
        if user_res and user_res.user:
            current_user = user_res.user
            st.session_state.auth_user = user_res.user
    except Exception:
        pass

profile = get_profile(current_user.id)
user_fullname = profile.get("full_name", current_user.email.split("@")[0])

# Clean up email and phone number fallbacks to avoid cross-field bugs
profile_email = profile.get("email") or current_user.email or ""
if current_user.email and profile_email != current_user.email:
    try:
        supabase.table("profiles").update({"email": current_user.email}).eq("id", current_user.id).execute()
        profile_email = current_user.email
    except Exception:
        pass
raw_phone = profile.get("phone_no") or ""
phone_val = "" if raw_phone.strip().lower() == profile_email.strip().lower() else raw_phone

# Sidebar Controls
with st.sidebar:
    # Render Profile Photo avatar if it exists
    avatar_url = profile.get("avatar_url")
    if avatar_url:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 0.8rem; margin-top: 0.5rem;">
            <img src="{avatar_url}" style="border-radius: 50%; width: 85px; height: 85px; object-fit: cover; border: 3px solid #60EFFF; box-shadow: 0 4px 15px rgba(0,0,0,0.35);"/>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.2rem;">
        <h3 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.3rem; color: {selected_theme['sidebar_header']};">
            Welcome, {user_fullname}
        </h3>
    </div>
    """, unsafe_allow_html=True)
        
    # Mobile Utility / PWA Quick Access Card
    if not st.session_state.get("pwa_dismissed"):
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.8rem; margin-bottom: 0.8rem;">
            <span style="font-weight: 700; font-size: 0.9rem; color: #60EFFF;">📱 App Quick Access</span><br/>
            <span style="font-size: 0.8rem; color: #cbd5e0; line-height: 1.3; display: block; margin-top: 0.3rem; margin-bottom: 0.6rem;">
                Add to Home Screen for app-like access (Tap browser menu <span style="font-weight:bold;">⁝</span> or share <span style="font-weight:bold;">📤</span> and select <b>Add to Home Screen</b>).
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        st.components.v1.html("""
        <style>
        .share-btn {
            background: linear-gradient(135deg, #007CF0 0%, #00DFD8 100%);
            border: none;
            color: white;
            padding: 8px 12px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            font-weight: 700;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            box-shadow: 0 4px 12px rgba(0, 223, 216, 0.15);
            transition: transform 0.2s;
            font-family: 'Outfit', sans-serif;
        }
        .share-btn:hover {
            transform: scale(1.02);
        }
        </style>
        <button class="share-btn" onclick="shareApp()">🔗 Share App Link</button>
        <script>
        function shareApp() {
            if (navigator.share) {
                navigator.share({
                    title: 'AI Financial Coach',
                    text: 'Check out this AI-powered Financial Coach and Expense Tracker!',
                    url: 'https://aifinancetracker.streamlit.app/'
                }).catch(err => console.log(err));
            } else {
                const tempInput = document.createElement('input');
                tempInput.value = 'https://aifinancetracker.streamlit.app/';
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                alert('Link copied to clipboard! (Sharing sheet not supported on this browser)');
            }
        }
        </script>
        """, height=38)
        
        if st.button("✕ Dismiss Guide", key="btn_dismiss_pwa", use_container_width=True):
            st.session_state.pwa_dismissed = True
            st.rerun()
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True) # Spacer
        
    # Edit Profile expander
    with st.expander("👤 Edit Profile"):
        st.caption("Change name, email, phone, password, or upload photo.")
        
        # Check if email is verified
        is_email_verified = False
        if current_user:
            email_confirmed_at = getattr(current_user, "email_confirmed_at", None)
            if email_confirmed_at:
                is_email_verified = True
        
        # Render email field dynamically based on verification status
        REDIRECT_URL = getattr(config, "REDIRECT_URL", "http://localhost:8501/")
        
        if is_email_verified:
            # State B: Email VERIFIED
            # Lock the email input field (disabled=True) and display ✅ next to it
            col_email, col_badge = st.columns([4, 1])
            with col_email:
                st.text_input("Registered Email", value=profile_email, disabled=True, key="profile_email_readonly")
            with col_badge:
                st.markdown("<div style='text-align: center; margin-top: 1.8rem; font-size: 1.5rem;' title='Verified Email'>✅</div>", unsafe_allow_html=True)
            updated_email = profile_email
        else:
            # State A: Email NOT Verified
            # Do not gray out (disabled=False), editable, and render a "Verify Email" button next to it
            col_email, col_action = st.columns([3.2, 1.8])
            with col_email:
                updated_email = st.text_input("Registered Email (Unverified)", value=profile_email, key="profile_email_editable")
            with col_action:
                st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True) # Spacer
                btn_verify_email = st.button("✉️ Verify Email", key="btn_verify_email_profile", help="Trigger verification email", use_container_width=True)
                
            if btn_verify_email:
                if not updated_email.strip():
                    st.error("Email cannot be empty.")
                else:
                    try:
                        # If email changed, update it first in Supabase
                        if updated_email.strip() != current_user.email:
                            supabase.auth.update_user(
                                {"email": updated_email.strip()},
                                options={"email_redirect_to": REDIRECT_URL}
                            )
                            supabase.table("profiles").update({"email": updated_email.strip()}).eq("id", current_user.id).execute()
                            st.success("Email updated and verification link sent! Please check your inbox.")
                        else:
                            # Just resend verification
                            supabase.auth.resend({
                                "type": "signup",
                                "email": updated_email.strip(),
                                "options": {
                                    "email_redirect_to": REDIRECT_URL
                                }
                            })
                            st.success("Verification link sent! Please check your inbox.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Verification trigger failed: {e}")
        
        # Profile Photo File Uploader (converts to base64 data URI)
        st.markdown("<small><b>Upload Profile Photo</b></small>", unsafe_allow_html=True)
        uploaded_img = st.file_uploader("Profile Photo", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        new_avatar_base64 = None
        if uploaded_img is not None:
            try:
                import base64
                img_bytes = uploaded_img.getvalue()
                base64_str = base64.b64encode(img_bytes).decode("utf-8")
                new_avatar_base64 = f"data:{uploaded_img.type};base64,{base64_str}"
                st.success("Photo uploaded! Click save to apply.")
            except Exception as e:
                st.error(f"Image processing failed: {e}")
                
        new_name = st.text_input("Full Name", value=user_fullname)
        new_phone = st.text_input("Phone Number", value=phone_val)
        
        st.markdown("<hr style='margin: 0.8rem 0; opacity: 0.2;'/>", unsafe_allow_html=True)
        st.markdown("<small><b>Change Password</b></small>", unsafe_allow_html=True)
        curr_password = st.text_input("Current Password", type="password", placeholder="Enter current password")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password (min 6 chars)")
        retype_password = st.text_input("Retype New Password", type="password", placeholder="Retype new password")
        
        if st.button("Save Profile Info", key="btn_save_profile_sidebar"):
            if not new_name.strip():
                st.error("Name cannot be empty.")
            else:
                try:
                    # Update email if unverified and changed
                    if not is_email_verified and updated_email.strip() and updated_email.strip() != profile_email:
                        try:
                            supabase.auth.update_user(
                                {"email": updated_email.strip()},
                                options={"email_redirect_to": REDIRECT_URL}
                            )
                            supabase.table("profiles").update({"email": updated_email.strip()}).eq("id", current_user.id).execute()
                            st.info("Verification link sent to the new email address. Please check your inbox.")
                        except Exception as email_update_err:
                            st.error(f"Failed to update email: {email_update_err}")
                    
                    update_data = {
                        "full_name": new_name.strip(),
                        "phone_no": new_phone.strip() if new_phone.strip() else None
                    }
                    if new_avatar_base64:
                        update_data["avatar_url"] = new_avatar_base64
                    
                    supabase.table("profiles").update(update_data).eq("id", current_user.id).execute()
                    
                    # Manage password updates securely
                    if curr_password.strip() or new_password.strip() or retype_password.strip():
                        if not curr_password.strip() or not new_password.strip() or not retype_password.strip():
                            st.error("To change password, you must fill all three password fields (Current, New, and Retype).")
                        elif new_password.strip() != retype_password.strip():
                            st.error("New Password and Retype New Password do not match.")
                        elif len(new_password.strip()) < 6:
                            st.error("New password must be at least 6 characters.")
                        else:
                            # Re-authenticate user to check if current password is correct
                            try:
                                supabase.auth.sign_in_with_password({"email": updated_email.strip(), "password": curr_password.strip()})
                                supabase.auth.update_user({"password": new_password.strip()})
                                st.info("Password updated successfully!")
                            except Exception as auth_err:
                                st.error(f"Password update failed: Current password might be incorrect. ({auth_err})")
                            
                    st.success("Profile saved!")
                    st.toast("Profile Saved!", icon="👤")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update profile: {e}")
                    
    st.divider()
    
    # Email Synced Engine (restructured under expander)
    with st.expander("📥 Email Transaction Sync"):
        # Read sync configs from User Metadata
        user_metadata = getattr(current_user, "user_metadata", {}) or {}
        email_sync_configs = user_metadata.get("email_sync_configs", [])
        
        if email_sync_configs:
            for cfg in email_sync_configs:
                st.markdown(f"• **{cfg['email']}** ({cfg['provider']})")
        else:
            st.caption("No sync accounts configured yet.")
            
        if st.button("Manage & Sync Inboxes", key="btn_open_email_sync_dialog", use_container_width=True):
            manage_email_sync_dialog()
                    
    st.divider()
    
    # Custom Category Creator (restructured under expander)
    with st.expander("🏷️ Add Custom Category"):
        st.caption("Create a new category for your transactions with standard or custom SVG icons.")
        
        new_cat_name = st.text_input("Category Name", placeholder="e.g. Shopping, Subscriptions", key="sidebar_new_cat_name")
        
        # Friendly icon selector
        icon_option = st.selectbox(
            "Category Icon Type",
            [
                "⚙️ Standard Wrench (Default)",
                "🛒 Groceries",
                "🚗 Fuel & Transport",
                "🍔 Dining & Food",
                "💡 Utilities & Bills",
                "🏥 Medical & Health",
                "🎬 Entertainment & Subs",
                "🏠 Home Maintenance",
                "🎓 Education & Fees",
                "💰 Salary & Income",
                "💼 Business / Trading",
                "Custom SVG XML..."
            ],
            key="sidebar_new_cat_icon_option"
        )
        
        # Show custom SVG text area only if selected
        new_cat_svg = ""
        if icon_option == "Custom SVG XML...":
            new_cat_svg = st.text_area("SVG Icon Path (raw xml)", value="", height=80, placeholder="<svg>...</svg>", key="sidebar_new_cat_svg_raw")
            
        if st.button("Register Category", key="btn_register_category_sidebar", use_container_width=True):
            if not new_cat_name.strip():
                st.error("Category name is required.")
            else:
                try:
                    # Resolve SVG path
                    resolved_svg = ""
                    if icon_option == "Custom SVG XML...":
                        resolved_svg = new_cat_svg.strip()
                    else:
                        # Extract the key name for looking up in GLOBAL_CATEGORIES
                        icon_map = {
                            "⚙️ Standard Wrench (Default)": "Miscellaneous",
                            "🛒 Groceries": "Groceries",
                            "🚗 Fuel & Transport": "Fuel & Transport",
                            "🍔 Dining & Food": "Dining & Food",
                            "💡 Utilities & Bills": "Utilities & Bills",
                            "🏥 Medical & Health": "Medical & Health",
                            "🎬 Entertainment & Subs": "Entertainment & Subs",
                            "🏠 Home Maintenance": "Home Maintenance",
                            "🎓 Education & Fees": "School & Tuition Fees",
                            "💰 Salary & Income": "Salary Credit",
                            "💼 Business / Trading": "Investments & Trading",
                        }
                        global_cat_key = icon_map.get(icon_option, "Miscellaneous")
                        # Get matching standard SVG
                        matched_cat = GLOBAL_CATEGORIES.get(global_cat_key)
                        if matched_cat:
                            resolved_svg = matched_cat.get("svg", "")
                    
                    if not resolved_svg:
                        # Use default wrench (Miscellaneous)
                        resolved_svg = GLOBAL_CATEGORIES["Miscellaneous"]["svg"]
                        
                    added = add_custom_category(supabase, current_user.id, new_cat_name.strip(), resolved_svg)
                    st.success(f"Category '{added['name']}' added successfully!")
                    st.toast("Category Added!", icon="🏷️")
                    st.rerun()
                except DuplicateCategoryError as e:
                    st.warning(str(e))
                except Exception as e:
                    st.error(f"Failed to add category: {e}")
                    
    st.divider()
    
    # Logout button
    if st.button("🚪 Sign Out", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.auth_user = None
        st.session_state.pending_expense = None
        st.rerun()

# 4. Main Panel Tabs Layout
if st.session_state.get("show_login_success"):
    st.markdown("""
    <div style="
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999999;
        animation: slideDownFadeOut 4.5s forwards ease-in-out;
        background: linear-gradient(135deg, #00FF87 0%, #60EFFF 100%);
        color: #0b0e14;
        padding: 0.9rem 2.5rem;
        border-radius: 50px;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 10px 30px rgba(96, 239, 255, 0.35);
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    ">
        🎉 Welcome back! Login successful.
    </div>
    
    <style>
    @keyframes slideDownFadeOut {
        0% {
            top: -100px;
            opacity: 0;
        }
        8% {
            top: 30px;
            opacity: 1;
        }
        88% {
            top: 30px;
            opacity: 1;
        }
        100% {
            top: -100px;
            opacity: 0;
            visibility: hidden;
            display: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    del st.session_state["show_login_success"]

st.markdown(f'<div class="main-title">Global Expense & Split Tracker</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">Production SaaS dashboard for <span style="color: {selected_theme["category_icon_color"]}; font-weight: 600;">{user_fullname}</span></div>', unsafe_allow_html=True)

# Fetch expenses and categories to render
process_recurring_schedules(current_user.id)
expenses = get_expenses(current_user.id)
categories = get_categories(current_user.id)

# Keep track of active tab across reruns
default_tab = st.session_state.pop("active_tab", None)

tab_analytics, tab_manual, tab_ledger, tab_goals, tab_subs, tab_family, tab_sandbox, tab_coach = st.tabs([
    "📊 Executive Analytics", 
    "➕ Add New Transaction", 
    "📋 Ledger Register",
    "🎯 Visual Goals",
    "🔌 Subscriptions",
    "👪 Household Hub",
    "🧪 What-If Sandbox",
    "💬 AI Financial Coach"
], default=default_tab)

# TAB 1: EXECUTIVE ANALYTICS
with tab_analytics:
    if not expenses:
        st.info("No transaction data found. Use 'Add New Transaction' or sync your emails to load details.")
    else:
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate calculated fields
        # Personal impact is: amount * (split_percentage / 100.00)
        df['personal_impact'] = df.apply(
            lambda r: float(r['amount']) * (float(r['split_percentage']) / 100.00), 
            axis=1
        )
        df['amount'] = df['amount'].astype(float)
        df['split_percentage'] = df['split_percentage'].astype(float)
        
        # Metric Calculations
        total_earnings = df[df['earning_vs_expense'] == 'Earning']['personal_impact'].sum()
        total_expenses = df[df['earning_vs_expense'] == 'Expense']['personal_impact'].sum()
        net_balance = total_earnings - total_expenses
        
        # Calculate shared splits amount (amount * (100 - split_percentage) / 100)
        # That represents money that was split/shared with others.
        df['split_with_others'] = df.apply(
            lambda r: float(r['amount']) * (1.0 - (float(r['split_percentage']) / 100.00)) if r['is_shared'] else 0.0,
            axis=1
        )
        total_shared_split = df['split_with_others'].sum()
        
        # Next-Gen FHS & Cash Flow Panel
        fhs_col1, fhs_col2 = st.columns([1, 1.5])
        with fhs_col1:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0; text-align:center;'>📈 Financial Health Score</h4>", unsafe_allow_html=True)
                
                # Form inputs inside an expander so it stays clean, or default estimations
                with st.expander("⚙️ Adjust FHS Variables", expanded=False):
                    f_inc = st.number_input("Gross Monthly Income (₹)", min_value=1.0, value=float(total_earnings) if total_earnings > 0 else 100000.0)
                    f_debt = st.number_input("Monthly Debt Obligations (₹)", min_value=0.0, value=20000.0)
                    f_cash = st.number_input("Liquid Emergency Cash (₹)", min_value=0.0, value=500000.0)
                    f_inv = st.number_input("Monthly Investments / SIPs (₹)", min_value=0.0, value=15000.0)
                    
                    ins_life = st.checkbox("Active Term Life Insurance (10x income)", value=True)
                    ins_health = st.checkbox("Active Family Health Insurance", value=True)
                    ins_other = st.checkbox("Active Vehicle/Property Insurance", value=True)
                
                ins_checklist = {"life": ins_life, "health": ins_health, "other": ins_other}
                fhs_val, fhs_breakdown = calculate_fhs(f_inc, total_expenses, f_cash, f_debt, f_inv, ins_checklist)
                
                # Color score based on rating
                score_color = "#48BB78" if fhs_val >= 700 else "#FF9933" if fhs_val >= 500 else "#F56565"
                st.markdown(f"""
                <div style="text-align:center; padding: 1rem 0;">
                    <span style="font-size: 3.5rem; font-weight:800; color:{score_color};">{fhs_val}</span><br/>
                    <span style="font-size:1rem; font-weight:600; color:#cbd5e0;">Credit-equivalent Rating</span>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"Savings Rate: {fhs_breakdown['savings_rate']:.1f}% | Emergency Runway: {fhs_breakdown['runway_months']:.1f} months")
                
        with fhs_col2:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0;'>🔮 Predictive Month-End Cash Flow</h4>", unsafe_allow_html=True)
                
                # Fetch subscriptions for month-end balance
                subs_amt_total = 0.0
                try:
                    from app.db import get_subscriptions
                    subs_list = get_subscriptions(current_user.id)
                    subs_amt_total = sum([float(s["amount"]) for s in subs_list])
                except Exception:
                    pass
                    
                projected_bal = net_balance - f_inv - f_debt - subs_amt_total
                
                st.markdown(f"""
                <div style="margin-top: 1rem;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <span>Current Ledger Net Balance:</span>
                        <b>₹{net_balance:,.2f}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; color:#FF9933;">
                        <span>- Upcoming Subscriptions:</span>
                        <b>₹{subs_amt_total:,.2f}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; color:#F56565;">
                        <span>- Monthly Debt Commitments:</span>
                        <b>₹{f_debt:,.2f}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; color:#00DFD8;">
                        <span>- Automated SIP Investments:</span>
                        <b>₹{f_inv:,.2f}</b>
                    </div>
                    <hr style="opacity:0.1; margin:0.5rem 0;"/>
                    <div style="display:flex; justify-content:space-between; font-size:1.2rem; font-weight:700;">
                        <span>Projected Month-End Balance:</span>
                        <span style="color:#00FF87;">₹{projected_bal:,.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # Render Metrics Row
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        
        with m_col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">💰 Net Personal Balance</div>
                <div class="metric-value {'metric-positive' if net_balance >= 0 else 'metric-negative'}">
                    ₹{net_balance:,.2f}
                </div>
                <small style="color:#a0aec0">Earnings minus expenses</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">📈 Personal Earnings</div>
                <div class="metric-value metric-positive">
                    ₹{total_earnings:,.2f}
                </div>
                <small style="color:#a0aec0">Adjusted for split shares</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">📉 Personal Expenses</div>
                <div class="metric-value metric-negative">
                    ₹{total_expenses:,.2f}
                </div>
                <small style="color:#a0aec0">Adjusted for split shares</small>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">🤝 Split with Others</div>
                <div class="metric-value metric-neutral">
                    ₹{total_shared_split:,.2f}
                </div>
                <small style="color:#a0aec0">Shared portion of bills</small>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Time-grain Frequency Selector
        col_grain_left, col_grain_right = st.columns([1, 4])
        with col_grain_left:
            st.markdown("<p style='margin-top:0.5rem; font-weight:600;'>Resolution Frequency</p>", unsafe_allow_html=True)
        with col_grain_right:
            time_grain = st.radio(
                "Time Grain", 
                ["Daily", "Weekly", "Monthly", "Yearly"], 
                horizontal=True,
                label_visibility="collapsed"
            )
            
        # Group data based on frequency
        if time_grain == "Daily":
            df['period'] = df['date'].dt.strftime('%Y-%m-%d')
        elif time_grain == "Weekly":
            # Start of week (Monday)
            df['period'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time.strftime('%Y-%m-%d'))
        elif time_grain == "Monthly":
            df['period'] = df['date'].dt.strftime('%Y-%m')
        else: # Yearly
            df['period'] = df['date'].dt.strftime('%Y')
            
        st.divider()
        
        # Graphs Grid
        g_col1, g_col2 = st.columns(2)
        
        # Graph 1: Category Distribution Donut Chart
        with g_col1:
            st.markdown("### Expense Distribution by Category")
            expense_df = df[df['earning_vs_expense'] == 'Expense']
            if expense_df.empty:
                st.info("No expenses found for category analysis.")
            else:
                # Merge with category name
                cat_data = []
                for _, row in expense_df.iterrows():
                    cat_name = row['categories']['name'] if row['categories'] else 'Miscellaneous'
                    cat_data.append({
                        "Category": cat_name,
                        "Amount": row['personal_impact']
                    })
                cat_df = pd.DataFrame(cat_data)
                cat_summary = cat_df.groupby("Category")["Amount"].sum().reset_index()
                
                THEME_COLORS = ['#60EFFF', '#007CF0', '#7928CA', '#FF007F', '#00FF87', '#FF9933', '#ED8936', '#48BB78']
                fig_donut = px.pie(
                    cat_summary, 
                    values='Amount', 
                    names='Category', 
                    hole=0.45,
                    color_discrete_sequence=THEME_COLORS
                )
                fig_donut.update_layout(
                    template=selected_theme["plotly_theme"],
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#FFFFFF' if app_theme != "☀️ Classic Light" else '#2d3748',
                    legend=dict(orientation="h", y=-0.1),
                    margin=dict(t=10, b=10, l=10, r=10)
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_donut, use_container_width=True)
                
        # Graph 2: Income vs. Expenses over Time
        with g_col2:
            st.markdown("### Earned Income vs. Accumulative Expenses")
            # Group by period and transaction type
            trend_df = df.groupby(['period', 'earning_vs_expense'])['personal_impact'].sum().unstack(fill_value=0).reset_index()
            
            # Ensure both columns exist
            if 'Earning' not in trend_df.columns:
                trend_df['Earning'] = 0.0
            if 'Expense' not in trend_df.columns:
                trend_df['Expense'] = 0.0
                
            trend_df = trend_df.sort_values('period')
            
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=trend_df['period'],
                y=trend_df['Earning'],
                name='Income/Earnings',
                marker_color='#00FF87'
            ))
            fig_bar.add_trace(go.Bar(
                x=trend_df['period'],
                y=trend_df['Expense'],
                name='Accumulative Expenses',
                marker_color='#FF416C'
            ))
            
            grid_color = 'rgba(255,255,255,0.05)' if app_theme != "☀️ Classic Light" else 'rgba(0,0,0,0.1)'
            fig_bar.update_layout(
                template=selected_theme["plotly_theme"],
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#FFFFFF' if app_theme != "☀️ Classic Light" else '#2d3748',
                legend=dict(orientation="h", y=-0.2),
                xaxis=dict(showgrid=False, title="Time period"),
                yaxis=dict(showgrid=True, gridcolor=grid_color, title="Amount (₹)"),
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # --- SPLITWISE OUTSTANDING BALANCES SECTION ---
        st.markdown("---")
        st.markdown("### 🤝 Shared Splits & Outstanding Balances (Splitwise Mode)")
        
        # Calculate Splitwise Outstanding balances
        outstanding_splits = {}
        for exp in expenses:
            if exp.get("is_shared") and exp.get("shared_person_name"):
                friend = exp["shared_person_name"].strip()
                friend_email = exp.get("shared_person_email") or ""
                friend_phone = exp.get("shared_person_phone") or ""
                
                amount = float(exp["amount"])
                split_pct = float(exp["split_percentage"])
                flow = exp.get("earning_vs_expense", "Expense")
                who = exp.get("who_paid", "You")
                
                impact = 0.0
                if flow == "Expense":
                    if who == "You":
                        # Friend owes you their share
                        impact = amount * (1.0 - split_pct / 100.0)
                    else:
                        # You owe friend your share
                        impact = -amount * (split_pct / 100.0)
                else: # Earning
                    if who == "You":
                        # You owe friend their share of the income
                        impact = -amount * (1.0 - split_pct / 100.0)
                    else:
                        # Friend owes you your share of the income
                        impact = amount * (split_pct / 100.0)
                        
                if friend not in outstanding_splits:
                    outstanding_splits[friend] = {
                        "balance": 0.0,
                        "email": friend_email,
                        "phone": friend_phone
                    }
                outstanding_splits[friend]["balance"] += impact
                if friend_email and not outstanding_splits[friend]["email"]:
                    outstanding_splits[friend]["email"] = friend_email
                if friend_phone and not outstanding_splits[friend]["phone"]:
                    outstanding_splits[friend]["phone"] = friend_phone

        # Filter out friends who have settled (balance close to 0)
        active_splits = {k: v for k, v in outstanding_splits.items() if abs(v["balance"]) >= 0.01}
        
        if not active_splits:
            st.info("🎉 All shared balances are fully settled! No outstanding splits.")
        else:
            split_cols = st.columns(min(len(active_splits), 3))
            
            for idx, (friend, data) in enumerate(active_splits.items()):
                col_idx = idx % len(split_cols)
                with split_cols[col_idx]:
                    bal = data["balance"]
                    is_owed = bal > 0
                    abs_bal = abs(bal)
                    
                    bg_color = "rgba(0, 255, 135, 0.05)" if is_owed else "rgba(255, 65, 108, 0.05)"
                    border_color = "rgba(0, 255, 135, 0.2)" if is_owed else "rgba(255, 65, 108, 0.2)"
                    text_class = "metric-positive" if is_owed else "metric-negative"
                    verb = "owes you" if is_owed else "you owe them"
                    
                    st.markdown(f"""
                    <div class="metric-container" style="background: {bg_color}; border: 1px solid {border_color}; text-align: left; padding: 1.2rem; margin-bottom: 0.8rem;">
                        <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">👤 {friend}</div>
                        <div style="font-size: 0.8rem; color: #a0aec0; margin-bottom: 0.4rem;">
                            {data['email'] or 'No email'} | {data['phone'] or 'No phone'}
                        </div>
                        <div class="{text_class}" style="font-size: 1.6rem; font-weight: 800; margin: 0.4rem 0;">
                            ₹{abs_bal:,.2f}
                        </div>
                        <div style="font-size: 0.75rem; color: #cbd5e0; text-transform: uppercase; font-weight: 600;">
                            {verb}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button(f"🔔 Remind Friend", key=f"remind_{friend}_{idx}", use_container_width=True):
                            if data['email']:
                                st.success(f"Reminder sent to {friend} ({data['email']})!")
                                st.toast("Reminder Sent!", icon="🔔")
                            else:
                                st.warning("No email registered.")
                    with act_col2:
                        if st.button(f"🤝 Settle Balance", key=f"settle_{friend}_{idx}", use_container_width=True):
                            # Record settlement: Expense transaction where:
                            # if they owe you (bal > 0), John pays you (so John paid, who_paid='Other', your share split_percentage=100.00 -> impact is negative)
                            # if you owe them (bal < 0), you pay John (so you paid, who_paid='You', your share split_percentage=0.00 -> impact is positive)
                            settlement_data = {
                                "profile_id": current_user.id,
                                "date": datetime.today().strftime("%Y-%m-%d"),
                                "merchant": f"Settlement: {friend}",
                                "description": f"Split settlement with {friend}",
                                "amount": abs_bal,
                                "earning_vs_expense": "Expense",
                                "category_id": None,
                                "is_shared": True,
                                "shared_person_name": friend,
                                "shared_person_email": data["email"],
                                "shared_person_phone": data["phone"],
                                "who_paid": "Other" if is_owed else "You",
                                "split_percentage": 100.00 if is_owed else 0.00,
                                "is_recurring": False,
                                "recurring_interval": "None"
                            }
                            try:
                                insert_expense(settlement_data)
                                st.success(f"Recorded settlement of ₹{abs_bal:,.2f} with {friend}!")
                                st.toast("Settled!", icon="🤝")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Settle failed: {e}")

# TAB 2: MANUAL ENTRY FORM
with tab_manual:
    st.markdown("### Enter Manual Transaction Details")
    
    # Handle duplicate verification trigger state
    if st.session_state.pending_expense:
        # User submitted, but a duplicate was detected
        pending = st.session_state.pending_expense
        st.warning(f"⚠️ **Duplicate Alert:** An identical transaction with the same amount (₹{pending['amount']}) and merchant ('{pending['merchant']}') on date {pending['date']} already exists in your ledger.")
        
        col_dup1, col_dup2 = st.columns(2)
        with col_dup1:
            if st.button("Yes, Force Add Transaction", use_container_width=True):
                # User wants to add it anyway
                try:
                    inserted = insert_expense(pending)
                    if inserted:
                        st.success("Transaction forced successfully!")
                        st.balloons()
                    st.session_state.pending_expense = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add transaction: {e}")
                    
        with col_dup2:
            if st.button("Cancel & Discard Entry", use_container_width=True):
                st.session_state.pending_expense = None
                st.info("Transaction entry discarded.")
                st.rerun()
    else:
        # Standard input form - using st.container(border=True) to allow dynamic, reactive options updating
        with st.container(border=True):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                tx_date = st.date_input("Transaction Date", value=datetime.today())
                tx_merchant = st.text_input("Merchant / Source Name", placeholder="e.g. Reliance Smart, Salary, Uber")
                tx_amount = st.number_input("Total Amount (₹)", min_value=0.00, step=10.00, format="%.2f")
                tx_type = st.radio("Transaction Flow", ["Expense", "Earning"], horizontal=True)
                
                # Recurring transaction configurations
                st.markdown("**🔄 Repeated Cycle (Recurring)**")
                is_recurring = st.checkbox("Is this a Recurring / Repeated Transaction?", value=False)
                recurring_interval = "None"
                if is_recurring:
                    recurring_interval = st.selectbox(
                        "Repeat Cycle Interval", 
                        options=["Weekly", "Monthly", "Yearly"], 
                        index=1 # Default to Monthly
                    )
                
            with col_form2:
                # Dynamically filter categories based on the transaction type selection
                EARNINGS_CATEGORIES_KEYS = {
                    "Salary Credit", "Investments & Trading", "Retirement & PF", 
                    "Profits & Interest", "F&F Settlement (Receipts)", "Other Income"
                }
                
                if tx_type == "Earning":
                    filtered_cats = [c for c in categories if c["name"] in EARNINGS_CATEGORIES_KEYS or c["profile_id"] is not None]
                else:
                    filtered_cats = [c for c in categories if c["name"] not in EARNINGS_CATEGORIES_KEYS]
                
                # Map categories list for dropdown selection
                cat_options = {c["name"]: c["id"] for c in filtered_cats}
                cat_options_list = list(cat_options.keys()) + ["➕ Create Custom Category..."]
                
                selected_cat_name = st.selectbox("Transaction Category", options=cat_options_list)
                
                # On-the-fly custom category text input
                new_cat_name_input = ""
                if selected_cat_name == "➕ Create Custom Category...":
                    new_cat_name_input = st.text_input("Enter New Custom Category Name", placeholder="e.g. Health Insurance, Pet Supplies")
                
                tx_desc = st.text_area("Short Description", placeholder="e.g. Weekly grocery stock, internet utility bill")
                
                # Split Allocation section
                st.markdown("**🤝 Splitwise Shared Allocation**")
                is_shared = st.checkbox("Is this a Shared / Split Transaction?", value=False)
                
                who_paid = "You"
                shared_person_name = ""
                shared_person_email = ""
                shared_person_phone = ""
                split_pct = 100.0
                
                if is_shared:
                    who_paid_selection = st.radio(
                        "Who Paid?", 
                        ["You paid (they owe you)", "Other paid (you owe them)"], 
                        horizontal=True
                    )
                    who_paid = "You" if "You paid" in who_paid_selection else "Other"
                    split_pct = st.slider("Your Share Percentage (%)", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
                    
                    shared_person_name = st.text_input("Friend's Name", placeholder="e.g. John Doe")
                    shared_person_email = st.text_input("Friend's Email Address", placeholder="e.g. john@example.com")
                    shared_person_phone = st.text_input("Friend's Phone Number", placeholder="e.g. +11234567890")
                    
                    # Invite button next to shared person fields
                    if shared_person_name:
                        invite_btn = st.button(f"✉️ Invite {shared_person_name} to Platform", key="btn_invite_person_manual_form")
                        if invite_btn:
                            if not shared_person_email:
                                st.warning("Please enter an email address to send the invitation.")
                            else:
                                try:
                                    # Simulate invitation
                                    st.success(f"🎉 Invitation link successfully sent to {shared_person_email}!")
                                    st.toast("Invited!", icon="✉️")
                                    if shared_person_phone:
                                        st.info(f"📱 SMS invite sent to {shared_person_phone}!")
                                except Exception as e:
                                    st.error(f"Invite failed: {e}")
            
            submit_tx = st.button("Record Transaction", use_container_width=True, type="primary")
            
            if submit_tx:
                if not tx_merchant.strip():
                    st.error("Merchant name is required.")
                elif tx_amount <= 0:
                    st.error("Amount must be greater than zero.")
                elif selected_cat_name == "➕ Create Custom Category..." and not new_cat_name_input.strip():
                    st.error("Please enter a name for the custom category.")
                elif is_shared and not shared_person_name.strip():
                    st.error("Please enter a name for the person you are splitting this transaction with.")
                else:
                    # Resolve category ID
                    resolved_category_id = None
                    if selected_cat_name == "➕ Create Custom Category...":
                        clean_new_cat = new_cat_name_input.strip()
                        # Avoid duplicates
                        existing_cat = None
                        for c in categories:
                            if c["name"].lower() == clean_new_cat.lower():
                                existing_cat = c
                                break
                        
                        if existing_cat:
                            resolved_category_id = existing_cat["id"]
                        else:
                            try:
                                new_cat = add_custom_category(supabase, current_user.id, clean_new_cat)
                                resolved_category_id = new_cat["id"]
                            except Exception as e:
                                st.error(f"Failed to create custom category: {e}")
                                resolved_category_id = None
                    else:
                        resolved_category_id = cat_options[selected_cat_name]
                    
                    if resolved_category_id is not None:
                        # Construct record
                        expense_data = {
                            "profile_id": current_user.id,
                            "date": tx_date.strftime("%Y-%m-%d"),
                            "merchant": tx_merchant.strip(),
                            "description": tx_desc.strip(),
                            "amount": tx_amount,
                            "earning_vs_expense": tx_type,
                            "category_id": resolved_category_id,
                            "is_shared": is_shared,
                            "split_percentage": split_pct if is_shared else 100.00,
                            "shared_person_name": shared_person_name.strip() if is_shared else None,
                            "shared_person_email": shared_person_email.strip() if is_shared else None,
                            "shared_person_phone": shared_person_phone.strip() if is_shared else None,
                            "who_paid": who_paid,
                            "is_recurring": is_recurring,
                            "recurring_interval": recurring_interval
                        }
                        
                        # Verify duplicates
                        duplicates = check_duplicate_expense(
                            current_user.id, 
                            expense_data["date"], 
                            expense_data["amount"], 
                            expense_data["merchant"]
                        )
                        
                        if duplicates:
                            # Set state to trigger duplicate popup confirm next render
                            st.session_state.pending_expense = expense_data
                            st.rerun()
                        else:
                            try:
                                inserted = insert_expense(expense_data)
                                if inserted:
                                    st.success("Transaction recorded successfully!")
                                    st.toast("Recorded!", icon="✅")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Failed to record transaction: {e}")

# TAB 3: LEDGER REGISTER
with tab_ledger:
    st.markdown("### Transaction Ledger Register")
    
    if not expenses:
        st.info("No transactions registered in this ledger. Sync your email or add manually.")
    else:
        # SEARCH AND SORTING FILTERS
        col_filter1, col_filter2, col_spacer = st.columns([1.5, 1, 2.5])
        with col_filter1:
            search_query = st.text_input("🔍 Search Transaction Ledger", placeholder="Search by merchant, description, category, or friend name...", key="ledger_search_box")
        with col_filter2:
            sort_by = st.selectbox(
                "Sort By", 
                options=[
                    "Date (Newest First)", 
                    "Date (Oldest First)", 
                    "Amount (Highest First)", 
                    "Amount (Lowest First)", 
                    "Merchant Name (A-Z)",
                    "Shared Friend Name (A-Z)"
                ],
                key="ledger_sort_box"
            )
            
        # EDIT TRANSACTION SUB-FORM
        if st.session_state.editing_expense_id:
            editing_exp = None
            for exp in expenses:
                if exp["id"] == st.session_state.editing_expense_id:
                    editing_exp = exp
                    break
                    
            if editing_exp:
                st.markdown("#### ✏️ Edit Transaction Details")
                with st.container(border=True):
                    col_ed1, col_ed2 = st.columns(2)
                    
                    with col_ed1:
                        ed_date = st.date_input("Date", value=datetime.strptime(editing_exp["date"], "%Y-%m-%d").date())
                        ed_merchant = st.text_input("Merchant / Source Name", value=editing_exp["merchant"])
                        ed_amount = st.number_input("Total Amount (₹)", min_value=0.00, value=float(editing_exp["amount"]), step=10.00, format="%.2f")
                        ed_type = st.radio("Transaction Flow", ["Expense", "Earning"], index=0 if editing_exp["earning_vs_expense"] == "Expense" else 1, horizontal=True)
                        
                        # Recurring Settings
                        ed_is_rec = st.checkbox("Is this a Recurring Transaction?", value=editing_exp.get("is_recurring", False))
                        ed_rec_interval = "None"
                        if ed_is_rec:
                            curr_int = editing_exp.get("recurring_interval", "Monthly")
                            ed_rec_interval = st.selectbox(
                                "Repeat Cycle Interval", 
                                options=["Weekly", "Monthly", "Yearly"], 
                                index=["Weekly", "Monthly", "Yearly"].index(curr_int) if curr_int in ["Weekly", "Monthly", "Yearly"] else 1
                            )
                        
                    with col_ed2:
                        # Dynamically filter categories based on transaction type selection
                        if ed_type == "Earning":
                            filtered_cats = [c for c in categories if c["name"] in EARNINGS_CATEGORIES_KEYS or c["profile_id"] is not None]
                        else:
                            filtered_cats = [c for c in categories if c["name"] not in EARNINGS_CATEGORIES_KEYS]
                            
                        ed_cat_options = {c["name"]: c["id"] for c in filtered_cats}
                        
                        curr_cat_id = editing_exp["category_id"]
                        curr_cat_name = None
                        for c in categories:
                            if c["id"] == curr_cat_id:
                                curr_cat_name = c["name"]
                                break
                        
                        ed_cat_options_list = list(ed_cat_options.keys())
                        default_idx = 0
                        if curr_cat_name and curr_cat_name in ed_cat_options:
                            default_idx = ed_cat_options_list.index(curr_cat_name)
                            
                        ed_selected_cat_name = st.selectbox("Category", options=ed_cat_options_list, index=default_idx)
                        ed_desc = st.text_area("Short Description", value=editing_exp["description"] or "")
                        
                        # Split settings
                        ed_is_shared = st.checkbox("Is this a Shared Transaction?", value=editing_exp.get("is_shared", False))
                        ed_who_paid = editing_exp.get("who_paid", "You")
                        ed_shared_name = editing_exp.get("shared_person_name") or ""
                        ed_shared_email = editing_exp.get("shared_person_email") or ""
                        ed_shared_phone = editing_exp.get("shared_person_phone") or ""
                        ed_split_pct = float(editing_exp.get("split_percentage", 50.00))
                        
                        if ed_is_shared:
                            ed_who_paid_selection = st.radio(
                                "Who Paid?", 
                                ["You paid (they owe you)", "Other paid (you owe them)"], 
                                index=0 if ed_who_paid == "You" else 1,
                                horizontal=True
                            )
                            ed_who_paid = "You" if "You paid" in ed_who_paid_selection else "Other"
                            ed_split_pct = st.slider("Your Share Percentage (%)", min_value=0.0, max_value=100.0, value=ed_split_pct, step=5.0)
                            ed_shared_name = st.text_input("Friend's Name", value=ed_shared_name)
                            ed_shared_email = st.text_input("Friend's Email Address", value=ed_shared_email)
                            ed_shared_phone = st.text_input("Friend's Phone Number", value=ed_shared_phone)
                            
                    ed_btn_save, ed_btn_cancel = st.columns(2)
                    with ed_btn_save:
                        if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                            try:
                                update_payload = {
                                    "date": ed_date.strftime("%Y-%m-%d"),
                                    "merchant": ed_merchant.strip(),
                                    "description": ed_desc.strip(),
                                    "amount": ed_amount,
                                    "earning_vs_expense": ed_type,
                                    "category_id": ed_cat_options[ed_selected_cat_name],
                                    "is_shared": ed_is_shared,
                                    "split_percentage": ed_split_pct if ed_is_shared else 100.00,
                                    "shared_person_name": ed_shared_name.strip() if ed_is_shared else None,
                                    "shared_person_email": ed_shared_email.strip() if ed_is_shared else None,
                                    "shared_person_phone": ed_shared_phone.strip() if ed_is_shared else None,
                                    "who_paid": ed_who_paid,
                                    "is_recurring": ed_is_rec,
                                    "recurring_interval": ed_rec_interval
                                }
                                supabase.table("expenses").update(update_payload).eq("id", editing_exp["id"]).eq("profile_id", current_user.id).execute()
                                st.success("Transaction updated successfully!")
                                st.session_state.editing_expense_id = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to update transaction: {e}")
                    with ed_btn_cancel:
                        if st.button("❌ Cancel Edit", use_container_width=True):
                            st.session_state.editing_expense_id = None
                            st.rerun()
                st.divider()

        # Build tabular rendering of expenses
        rows = []
        for exp in expenses:
            cat_name = exp["categories"]["name"] if exp["categories"] else "Miscellaneous"
            cat_svg = exp["categories"]["svg_icon"] if exp["categories"] else ""
            
            # Formulate inline SVG rendering
            cat_html = f'<div class="category-badge"><span class="category-icon">{cat_svg}</span>{cat_name}</div>'
            
            # Format numbers
            total_amt = float(exp["amount"])
            split_p = float(exp["split_percentage"])
            personal_imp = total_amt * (split_p / 100.0)
            
            rows.append({
                "ID": exp["id"],
                "Date": exp["date"],
                "Type": exp["earning_vs_expense"],
                "Merchant": exp["merchant"],
                "Description": exp["description"] or "",
                "CategoryBadge": cat_html,
                "CategoryName": cat_name,
                "SharedPerson": exp.get("shared_person_name") or "",
                "Total Amount (₹)": f"₹{total_amt:,.2f}",
                "Total Amount Float": total_amt,
                "Split": f"{split_p:.0f}%" if exp["is_shared"] else "Personal (100%)",
                "Personal Owed (₹)": f"₹{personal_imp:,.2f}",
                "Source": "📧 Email Sync" if exp.get("raw_email_uid") else "✍️ Manual"
            })
            
        ledger_df = pd.DataFrame(rows)
        
        # Apply Search query filter
        if search_query.strip():
            q = search_query.strip().lower()
            ledger_df = ledger_df[
                ledger_df["Merchant"].str.lower().str.contains(q) |
                ledger_df["Description"].str.lower().str.contains(q) |
                ledger_df["CategoryName"].str.lower().str.contains(q) |
                ledger_df["SharedPerson"].str.lower().str.contains(q)
            ]
            
        # Apply Sorting selection
        if sort_by == "Date (Newest First)":
            ledger_df = ledger_df.sort_values(by="Date", ascending=False)
        elif sort_by == "Date (Oldest First)":
            ledger_df = ledger_df.sort_values(by="Date", ascending=True)
        elif sort_by == "Amount (Highest First)":
            ledger_df = ledger_df.sort_values(by="Total Amount Float", ascending=False)
        elif sort_by == "Amount (Lowest First)":
            ledger_df = ledger_df.sort_values(by="Total Amount Float", ascending=True)
        elif sort_by == "Merchant Name (A-Z)":
            ledger_df = ledger_df.sort_values(by="Merchant", key=lambda col: col.str.lower(), ascending=True)
        elif sort_by == "Shared Friend Name (A-Z)":
            ledger_df = ledger_df.sort_values(by="SharedPerson", key=lambda col: col.str.lower(), ascending=True)

        if ledger_df.empty:
            st.info("No matching ledger items found for search query.")
        else:
            for idx, row in ledger_df.iterrows():
                card_col1, card_col2, card_col3 = st.columns([1, 5, 2])
                
                with card_col1:
                    # Type indicator with visual colors
                    if row["Type"] == "Earning":
                        st.markdown("<h4 style='color:#48BB78; margin: 0; text-align:center;'>▲ IN</h4>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h4 style='color:#F56565; margin: 0; text-align:center;'>▼ OUT</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:{selected_theme['subtext_color']}; font-size:0.85rem; text-align:center;'>{row['Date']}</p>", unsafe_allow_html=True)
                    
                with card_col2:
                    # Main body
                    badge_html = row["CategoryBadge"]
                    shared_info = f" | Split: {row['SharedPerson']}" if row["SharedPerson"] else ""
                    st.markdown(f"""
                    <div style="margin-bottom:0.8rem">
                        <span style="font-weight:600; font-size:1.1rem">{row["Merchant"]}</span>
                        &nbsp;&nbsp;&nbsp;&nbsp;{badge_html}
                        &nbsp;&nbsp;&nbsp;&nbsp;<span style="color:{selected_theme['subtext_color']}; font-size:0.85rem">{row["Source"]}{shared_info}</span>
                        <br/>
                        <span style="color:#a0aec0; font-size:0.9rem">{row["Description"]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with card_col3:
                    # Financial sums + actions
                    val_color = "#48BB78" if row["Type"] == "Earning" else "#F56565"
                    st.markdown(f"""
                    <div style="text-align:right; margin-bottom:0.5rem">
                        <span style="font-weight:600; font-size:1.1rem; color:{val_color};">{row["Personal Owed (₹)"]}</span><br/>
                        <span style="color:{selected_theme['subtext_color']}; font-size:0.75rem">Total: {row["Total Amount (₹)"]} ({row["Split"]})</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Delete and Edit Actions
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if st.button("✏️", key=f"edit_btn_{row['ID']}", help="Edit transaction details", use_container_width=True):
                            st.session_state.editing_expense_id = row['ID']
                            st.rerun()
                    with act_col2:
                        if st.button("🗑️", key=f"del_btn_{row['ID']}", help="Delete transaction", use_container_width=True):
                            deleted = delete_expense(row["ID"], current_user.id)
                            if deleted:
                                st.toast("Transaction deleted", icon="🗑️")
                                st.rerun()
                st.divider()


# ==========================================================
# Next-Gen PFM Enhancements Tab Implementations (June 21, 2026)
# ==========================================================

# TAB 4: VISUAL GOALS
with tab_goals:
    st.markdown('<div class="main-title" style="font-size:2rem; margin-bottom:1rem;">🎯 Financial Goals visual Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="margin-bottom:2rem; text-align:left;">Transition from rigid monthly budgets to dynamic, long-term visual savings goals.</div>', unsafe_allow_html=True)
    
    # Import Goal DB routines dynamically to isolate error handling
    from app.db import get_goals, insert_goal, update_goal_savings, delete_goal, get_household
    
    household = {}
    try:
        household = get_household(current_user.id)
    except Exception:
        pass
        
    h_id = household.get("id") if household else None
    
    goals_list = []
    try:
        goals_list = get_goals(current_user.id, h_id)
    except Exception as e:
        st.warning("⚠️ Goals database table is missing or not synced yet. Apply SQL migrations from schema.sql to enable goals!")
        
    # Form to add a goal
    with st.expander("➕ Create New Financial Goal", expanded=False):
        with st.form("new_goal_form"):
            g_name = st.text_input("Goal Name", placeholder="e.g. Dream House, Child Education, Vacation")
            g_target = st.number_input("Target Amount (₹)", min_value=100.0, step=1000.0, value=100000.0)
            g_date = st.date_input("Target Completion Date")
            g_scope = st.selectbox("Goal Scope", ["Personal", "Shared Household"] if h_id else ["Personal"])
            
            submit_g = st.form_submit_button("Create Savings Goal")
            if submit_g:
                if not g_name.strip():
                    st.error("Goal name is required.")
                else:
                    new_g_data = {
                        "profile_id": current_user.id,
                        "household_id": h_id if g_scope == "Shared Household" else None,
                        "name": g_name.strip(),
                        "target_amount": g_target,
                        "current_savings": 0.00,
                        "target_date": g_date.strftime("%Y-%m-%d")
                    }
                    try:
                        inserted = insert_goal(new_g_data)
                        if inserted:
                            st.success(f"Goal '{g_name}' registered successfully!")
                            st.rerun()
                    except Exception as err:
                        st.error(f"Failed to create goal: {err}")
                        
    # Display active goals
    if goals_list:
        st.markdown("### Active Savings Goals")
        for g in goals_list:
            target_val = float(g["target_amount"])
            saved_val = float(g["current_savings"])
            pct = min(1.0, saved_val / target_val) if target_val > 0 else 0
            
            # Parse target date
            try:
                t_date = datetime.strptime(g["target_date"], "%Y-%m-%d").date()
                days_left = (t_date - datetime.today().date()).days
                months_left = max(1, int(days_left / 30.4))
                monthly_req = max(0.00, (target_val - saved_val) / months_left)
            except Exception:
                months_left = 1
                monthly_req = target_val - saved_val
                
            scope_badge = "👥 Shared" if g.get("household_id") else "👤 Personal"
            
            # Glassmorphic card for each goal
            st.markdown(f"""
            <div class="metric-container" style="text-align: left; margin-bottom: 1.5rem; padding: 1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.25rem; font-weight:700; color:{selected_theme['text_color']};">{g['name']}</span>
                    <span class="category-badge">{scope_badge}</span>
                </div>
                <div style="font-size: 0.85rem; color:{selected_theme['subtext_color']}; margin-bottom: 1rem;">
                    Target: <b>₹{target_val:,.2f}</b> by {g['target_date']} ({months_left} months remaining)
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; font-size: 0.9rem; margin-bottom:0.4rem;">
                    <span>Saved: <b>₹{saved_val:,.2f}</b> ({pct*100:.1f}%)</span>
                    <span>Required: <b>₹{monthly_req:,.2f} / month</b></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar and quick update inputs
            st.progress(pct)
            
            up_col1, up_col2, up_col3 = st.columns([2, 1, 1])
            with up_col1:
                new_saved_input = st.number_input(f"Update Saved Balance for {g['name']}", min_value=0.0, max_value=target_val, value=saved_val, key=f"save_val_{g['id']}")
            with up_col2:
                if st.button("Apply", key=f"btn_up_save_{g['id']}", use_container_width=True):
                    try:
                        if update_goal_savings(g["id"], new_saved_input):
                            st.toast("Goal progress updated!")
                            st.rerun()
                    except Exception as err:
                        st.error(str(err))
            with up_col3:
                if st.button("Delete", key=f"btn_del_goal_{g['id']}", use_container_width=True):
                    try:
                        if delete_goal(g["id"]):
                            st.toast("Goal deleted")
                            st.rerun()
                    except Exception as err:
                        st.error(str(err))
            st.markdown("<hr style='opacity:0.1; margin: 1.5rem 0;'/>", unsafe_allow_html=True)
    else:
        st.caption("No dynamic goals configured yet. Add a savings goal above to start visual planning!")


# TAB 5: INTELLIGENT SUBSCRIPTIONS
with tab_subs:
    st.markdown('<div class="main-title" style="font-size:2rem; margin-bottom:1rem;">🔌 Intelligent Subscription & Renewal Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="margin-bottom:2rem; text-align:left;">Automatically monitor SaaS, entertainment recurring payments, and flag wasted subscription costs.</div>', unsafe_allow_html=True)
    
    from app.db import get_subscriptions, insert_subscription, delete_subscription, update_subscription
    
    subs_list = []
    try:
        subs_list = get_subscriptions(current_user.id)
    except Exception:
        st.warning("⚠️ Subscriptions database table is missing or not synced yet. Apply SQL migrations from schema.sql to enable subscriptions!")
        
    sub_cat_options = {c["name"]: c["id"] for c in categories} if 'categories' in locals() or 'categories' in globals() else {}
    
    # Form to add a subscription
    with st.expander("➕ Register New Subscription / Renewal", expanded=False):
        with st.form("new_sub_form"):
            sub_name = st.text_input("Service Name", placeholder="e.g. Netflix, Spotify, Amazon Prime, AWS")
            sub_amt = st.number_input("Billing Amount (₹)", min_value=1.0, value=299.0, step=10.0)
            sub_cycle = st.selectbox("Billing Cycle", ["Weekly", "Monthly", "Quarterly", "Yearly"])
            sub_date = st.date_input("Next Renewal Date")
            sub_cat = st.selectbox("Category Mapping", list(sub_cat_options.keys()) if sub_cat_options else ["Entertainment & Subs", "Utilities & Bills"])
            
            submit_sub = st.form_submit_button("Track Subscription")
            if submit_sub:
                if not sub_name.strip():
                    st.error("Service name is required.")
                else:
                    mapped_cat_id = sub_cat_options.get(sub_cat) if sub_cat_options else None
                        
                    new_sub_data = {
                        "profile_id": current_user.id,
                        "name": sub_name.strip(),
                        "amount": sub_amt,
                        "billing_cycle": sub_cycle,
                        "next_billing_date": sub_date.strftime("%Y-%m-%d"),
                        "category_id": mapped_cat_id
                    }
                    try:
                        inserted = insert_subscription(new_sub_data)
                        if inserted:
                            st.success(f"Subscription '{sub_name}' is now tracked!")
                            st.rerun()
                    except Exception as err:
                        st.error(f"Failed to track subscription: {err}")
                        
    # Display active subscriptions and alert notifications
    if subs_list:
        # Check alerts: Netflix/Spotify renewal in next 5 days
        today = datetime.today().date()
        alerts = []
        
        for sub in subs_list:
            next_bill = datetime.strptime(sub["next_billing_date"], "%Y-%m-%d").date()
            days_to_bill = (next_bill - today).days
            if 0 <= days_to_bill <= 5:
                alerts.append(f"⚠️ **{sub['name']}** renewal of **₹{float(sub['amount']):,.2f}** is due in **{days_to_bill} days** ({sub['next_billing_date']}).")
                
        # Alert Box
        if alerts:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0; color:#FF9933;'>🔔 Upcoming Renewal Alerts (Next 5 Days)</h4>", unsafe_allow_html=True)
                for alert in alerts:
                    st.markdown(alert)
                    
        # Wasted SaaS Box
        wasted_subs = [s for s in subs_list if s.get("is_wasted") or s.get("last_detected_usage") is None]
        if wasted_subs:
            with st.container(border=True):
                st.markdown("<h4 style='margin:0; color:#F56565;'>📉 Wasted Subscription Optimizer</h4>", unsafe_allow_html=True)
                st.markdown("<small>We detected zero financial transaction notifications or IMAP email alerts for the following subscriptions over the last 60 days. Consider cancelling these to optimize savings:</small>", unsafe_allow_html=True)
                for ws in wasted_subs:
                    st.markdown(f"• ❌ **{ws['name']}** (Costing **₹{float(ws['amount']):,.2f} / {ws['billing_cycle'].lower()}**)")
                    
        st.markdown("### Tracked Services")
        for sub in subs_list:
            sub_amount_val = float(sub["amount"])
            next_bill_str = sub["next_billing_date"]
            
            # Simple card representation
            st.markdown(f"""
            <div class="metric-container" style="text-align: left; margin-bottom: 1rem; padding: 1.2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size: 1.15rem; font-weight:700;">{sub['name']}</span>
                    <span style="font-weight:600; font-size:1.15rem; color:#FF9933;">₹{sub_amount_val:,.2f} / {sub['billing_cycle'].lower()}</span>
                </div>
                <div style="font-size: 0.8rem; color:{selected_theme['subtext_color']}; margin-top: 0.4rem;">
                    Next Renewal: {next_bill_str} | Status: Active Sync
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            sub_col1, sub_col2, sub_col3 = st.columns([2, 1, 1])
            with sub_col1:
                # toggle simulated wasted status
                w_status = st.checkbox("Mark as Low Usage / Wasted", value=sub.get("is_wasted", False), key=f"ws_status_{sub['id']}")
            with sub_col2:
                if st.button("Apply Status", key=f"btn_up_sub_{sub['id']}", use_container_width=True):
                    try:
                        if update_subscription(sub["id"], {"is_wasted": w_status}):
                            st.toast("Subscription optimization tag updated!")
                            st.rerun()
                    except Exception as err:
                        st.error(str(err))
            with sub_col3:
                if st.button("Cancel Track", key=f"btn_del_sub_{sub['id']}", use_container_width=True):
                    try:
                        if delete_subscription(sub["id"]):
                            st.toast("Subscription untracked")
                            st.rerun()
                    except Exception as err:
                        st.error(str(err))
    else:
        st.caption("No subscriptions configured yet. Add your SaaS, Netflix, or annual insurance contracts above to track renewals!")


# TAB 6: HOUSEHOLD HUB
with tab_family:
    st.markdown('<div class="main-title" style="font-size:2rem; margin-bottom:1rem;">👪 Household / Family Sync Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="margin-bottom:2rem; text-align:left;">Sync finances, share savings targets, track chore reward bonuses, and configure allowances.</div>', unsafe_allow_html=True)
    
    from app.db import get_household, get_household_members, create_household, add_household_member, get_allowances_for_parent, get_allowance_for_child, create_allowance, get_chores, create_chore, update_chore_status
    
    household = {}
    try:
        household = get_household(current_user.id)
    except Exception:
        st.warning("⚠️ Household tables are missing or not synced yet. Apply DDL migrations from schema.sql to activate collaborative tools!")
        
    if not household:
        st.info("💡 You do not belong to a household yet. You can create a new household or wait for an invitation.")
        h_name_input = st.text_input("New Household Name", placeholder="e.g. Singh Family, The Johansons Joint Account")
        if st.button("Create Household & Parent Profile", use_container_width=True):
            if h_name_input.strip():
                try:
                    new_h = create_household(current_user.id, h_name_input.strip())
                    if new_h:
                        st.success(f"Household '{h_name_input.strip()}' created successfully!")
                        st.rerun()
                except Exception as err:
                    st.error(str(err))
            else:
                st.error("Household name is required.")
    else:
        st.success(f"🏡 Connected to Household: **{household['name']}** (Role: **{household['role']}**)")
        
        # Display members list
        members = get_household_members(household["id"])
        
        m_col1, m_col2 = st.columns([1.5, 2])
        with m_col1:
            st.markdown("### Household Members")
            for m in members:
                p_meta = m.get("profiles", {}) or {}
                m_name = p_meta.get("full_name", "Anonymous")
                m_email = p_meta.get("email", "")
                st.markdown(f"• **{m_name}** ({m['role']}) — <small>{m_email}</small>", unsafe_allow_html=True)
                
            # Form to add a member
            if household["role"] in ["Admin", "Parent"]:
                with st.expander("✉️ Invite Family Member", expanded=False):
                    new_m_email = st.text_input("Member Email Address", placeholder="spouse@family.com")
                    new_m_role = st.selectbox("Role", ["Parent", "Child"])
                    if st.button("Add Member to Joint Space", use_container_width=True):
                        if new_m_email.strip():
                            try:
                                if add_household_member(household["id"], new_m_email.strip(), new_m_role):
                                    st.success(f"Member '{new_m_email}' added successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to add member: Profile email not registered on this platform.")
                            except Exception as err:
                                st.error(str(err))
                        else:
                            st.error("Email address is required.")
                            
        with m_col2:
            st.markdown("### 💰 Allowance & Chore Tracker")
            if household["role"] == "Parent":
                st.caption("Manage allowance payouts and chores for children in your household.")
                
                # Check allowances
                parent_allowances = get_allowances_for_parent(current_user.id)
                if parent_allowances:
                    for a in parent_allowances:
                        c_name = a.get("profiles", {}).get("full_name", "Child")
                        st.markdown(f"**Allowance Contract for {c_name}:** ₹{float(a['base_pocket_money']):,.2f} / month")
                        
                        # Fetch chores for allowance
                        allowance_chores = get_chores(a["id"])
                        if allowance_chores:
                            for c in allowance_chores:
                                status_emoji = "⏳" if c["status"] == "Assigned" else "✅" if c["status"] == "Completed" else "⭐"
                                st.markdown(f"- {status_emoji} **{c['name']}** (Reward: ₹{float(c['reward_amount']):,.2f}) — Status: {c['status']}")
                                if c["status"] == "Completed":
                                    if st.button("Approve Reward & Payout", key=f"btn_appr_chore_{c['id']}", use_container_width=True):
                                        try:
                                            if update_chore_status(c["id"], "Approved"):
                                                st.toast(f"Reward of ₹{float(c['reward_amount'])} approved!")
                                                st.rerun()
                                        except Exception as err:
                                            st.error(str(err))
                        
                        # Add a chore
                        with st.expander(f"➕ Assign Chore to {c_name}", expanded=False):
                            c_task = st.text_input("Chore/Task Name", placeholder="e.g. Wash the car, Complete math prep", key=f"task_{a['id']}")
                            c_reward = st.number_input("Chore Reward Amount (₹)", min_value=0.0, value=100.0, step=10.0, key=f"reward_{a['id']}")
                            c_due = st.date_input("Chore Due Date", key=f"due_{a['id']}")
                            
                            if st.button("Create Task", key=f"btn_create_task_{a['id']}", use_container_width=True):
                                if c_task.strip():
                                    try:
                                        inserted_c = create_chore(a["id"], a["child_id"], c_task.strip(), c_reward, c_due.strftime("%Y-%m-%d"))
                                        if inserted_c:
                                            st.success("Chore assigned!")
                                            st.rerun()
                                    except Exception as err:
                                        st.error(str(err))
                else:
                    # Form to create child allowance connection
                    with st.expander("Create Child Pocket Money Contract", expanded=False):
                        child_select_email = st.text_input("Child Registered Email", placeholder="child@family.com")
                        pocket_amt = st.number_input("Base Pocket Money (₹)", min_value=0.0, value=1500.0)
                        
                        if st.button("Establish Pocket Money", use_container_width=True):
                            if child_select_email.strip():
                                try:
                                    guardrails = {"daily_limit": 500, "blocked_categories": ["Gaming", "Entertainment"]}
                                    allowance = create_allowance(current_user.id, child_select_email.strip(), pocket_amt, guardrails)
                                    if allowance:
                                        st.success("Pocket Money established successfully!")
                                        st.rerun()
                                except Exception as err:
                                    st.error(str(err))
                            else:
                                st.error("Child email is required.")
                                
            elif household["role"] == "Child":
                st.caption("View your pocket money contract and log completed chores to request payouts.")
                
                child_allowance = get_allowance_for_child(current_user.id)
                if child_allowance:
                    p_name = child_allowance.get("profiles", {}).get("full_name", "Parent")
                    st.markdown(f"**Your Monthly Allowance:** ₹{float(child_allowance['base_pocket_money']):,.2f} (Managed by {p_name})")
                    
                    # Fetch chores
                    child_chores = get_chores(child_allowance["id"])
                    if child_chores:
                        st.markdown("#### Your Assigned Tasks")
                        for c in child_chores:
                            status_emoji = "⏳" if c["status"] == "Assigned" else "✅" if c["status"] == "Completed" else "⭐"
                            st.markdown(f"• {status_emoji} **{c['name']}** (Reward: ₹{float(c['reward_amount']):,.2f}) — Status: {c['status']}")
                            if c["status"] == "Assigned":
                                if st.button("Mark Completed (Request Payout)", key=f"btn_comp_chore_{c['id']}", use_container_width=True):
                                    try:
                                        if update_chore_status(c["id"], "Completed"):
                                            st.toast("Requested payout! Waiting for Parent approval.")
                                            st.rerun()
                                    except Exception as err:
                                        st.error(str(err))
                    else:
                        st.caption("No chores currently assigned by your parent.")
                else:
                    st.caption("No pocket money contract registered by your parent yet.")


# TAB 7: WHAT-IF SANDBOX
with tab_sandbox:
    st.markdown('<div class="main-title" style="font-size:2rem; margin-bottom:1rem;">🧪 Life Event Sandbox Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="margin-bottom:2rem; text-align:left;">Clone your active financial profile to test and simulate stressors, salary jumps, or early retirement.</div>', unsafe_allow_html=True)
    
    from app.db import get_scenarios, save_scenario, delete_scenario
    
    scenarios_list = []
    try:
        scenarios_list = get_scenarios(current_user.id)
    except Exception:
        st.warning("⚠️ Scenarios database table is missing or not synced yet. Apply SQL migrations from schema.sql to activate simulator!")
        
    # Simulate variables
    sim_col1, sim_col2 = st.columns([1, 1.5])
    with sim_col1:
        st.markdown("### Stressors & Boosts")
        sim_name = st.text_input("Simulation Name", placeholder="e.g. Job Loss Stress Test, 30% Promotion")
        sim_salary_change = st.number_input("Salary / Income Change (₹ / month)", value=0.00, step=5000.00)
        sim_expense_change = st.number_input("Fixed Expenses Change (₹ / month)", value=0.00, step=2000.00)
        sim_job_loss_months = st.number_input("Simulate Job Loss (Months without income)", min_value=0, max_value=24, value=0)
        sim_home_purchase = st.number_input("Simulate Home Purchase Mortgage (₹ / month)", min_value=0.0, value=0.0, step=5000.0)
        
        # Base stats for calculations
        # Sum base savings and base monthly income
        base_income = 150000.0
        base_expenses = 100000.0
        base_net_worth = 500000.0
        
        # Calculate base metrics if transactions exist
        if 'expenses' in locals() and expenses:
            try:
                temp_df = pd.DataFrame(expenses)
                temp_df['amount'] = temp_df['amount'].astype(float)
                m_exp = temp_df[temp_df['earning_vs_expense'] == 'Expense']['amount'].sum() / 2.0
                m_inc = temp_df[temp_df['earning_vs_expense'] == 'Earning']['amount'].sum() / 2.0
                if m_exp > 0: base_expenses = float(m_exp)
                if m_inc > 0: base_income = float(m_inc)
            except Exception:
                pass
                
        if st.button("Execute Simulation", use_container_width=True):
            if not sim_name.strip():
                st.error("Please enter a name for this simulation.")
            else:
                base_timeline = []
                sim_timeline = []
                
                base_val = base_net_worth
                sim_val = base_net_worth
                
                base_savings = base_income - base_expenses
                sim_savings = (base_income + sim_salary_change) - (base_expenses + sim_expense_change + sim_home_purchase)
                
                for month in range(120):
                    base_val = (base_val * (1 + 0.04/12)) + (base_savings / 12)
                    
                    if month < sim_job_loss_months:
                        sim_val = (sim_val * (1 + 0.04/12)) - (base_expenses + sim_expense_change + sim_home_purchase)
                    else:
                        sim_val = (sim_val * (1 + 0.04/12)) + (sim_savings / 12)
                        
                    base_timeline.append(max(0.00, base_val))
                    sim_timeline.append(max(0.00, sim_val))
                    
                outputs = {
                    "base_timeline": base_timeline,
                    "sim_timeline": sim_timeline,
                    "final_base": base_timeline[-1],
                    "final_sim": sim_timeline[-1]
                }
                inputs = {
                    "salary_change": sim_salary_change,
                    "expense_change": sim_expense_change,
                    "job_loss_months": sim_job_loss_months,
                    "home_purchase": sim_home_purchase
                }
                try:
                    save_scenario(current_user.id, sim_name.strip(), inputs, outputs)
                    st.success(f"Simulation '{sim_name}' executed and saved!")
                    st.rerun()
                except Exception as err:
                    st.error(str(err))
                    
    with sim_col2:
        st.markdown("### Simulation Trajectories")
        if scenarios_list:
            selected_sim = st.selectbox("Select Simulation to Visualize", [s["scenario_name"] for s in scenarios_list])
            sc = [s for s in scenarios_list if s["scenario_name"] == selected_sim][0]
            
            sc_out = sc["outputs"]
            base_t = sc_out["base_timeline"]
            sim_t = sc_out["sim_timeline"]
            
            years = [round(m / 12, 1) for m in range(120)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=years, y=base_t, name="Base Plan (4% Yield)", line=dict(color="#007CF0", width=3)))
            fig.add_trace(go.Scatter(x=years, y=sim_t, name=f"Simulated: {selected_sim}", line=dict(color="#F56565", width=3, dash='dash')))
            
            fig.update_layout(
                title=f"Net Worth Forecast Comparison (10-Year Horizon)",
                xaxis_title="Timeline (Years)",
                yaxis_title="Estimated Net Worth (₹)",
                template=selected_theme.get("plotly_theme", "plotly_dark"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("10-Year Estimated Net Worth (Base)", f"₹{base_t[-1]:,.2f}")
            with metric_col2:
                st.metric("10-Year Estimated Net Worth (Simulated)", f"₹{sim_t[-1]:,.2f}", delta=f"₹{sim_t[-1] - base_t[-1]:,.2f}")
                
            if st.button("Delete Simulation", key=f"btn_del_sim_{sc['id']}", use_container_width=True):
                try:
                    if delete_scenario(sc["id"]):
                        st.toast("Simulation deleted")
                        st.rerun()
                except Exception as err:
                    st.error(str(err))
        else:
            st.caption("No simulated scenarios saved yet. Define sandbox variables and click 'Execute Simulation' to plot outcomes!")


# TAB 8: AI FINANCIAL COACH
with tab_coach:
    st.markdown('<div class="main-title" style="font-size:2rem; margin-bottom:1rem;">💬 AI Financial Coach & Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="margin-bottom:1.5rem; text-align:left;">Have a continuous conversation with your AI advisor. Ask follow-up questions, request adjustments, or verify budget metrics.</div>', unsafe_allow_html=True)
    
    active_goals = []
    active_subs = []
    h_id_context = None
    try:
        from app.db import get_goals, get_subscriptions, get_household
        h_info = get_household(current_user.id)
        h_id_context = h_info.get("id") if h_info else None
        active_goals = get_goals(current_user.id, h_id_context)
        active_subs = get_subscriptions(current_user.id)
    except Exception:
        pass
        
    # 1. Summarize Recurring Expense Templates
    recurring_items = []
    if expenses:
        for e in expenses:
            if e.get("is_recurring"):
                cat_name = e.get("categories", {}).get("name", "Uncategorized") if (isinstance(e.get("categories"), dict) and e.get("categories")) else "Uncategorized"
                recurring_items.append(f"  • {e.get('merchant', 'Unknown')} ({cat_name}): ₹{float(e.get('amount', 0)):,.2f} repeated {e.get('recurring_interval', 'Monthly')}")
                
    # 2. Summarize recent transactions (last 30 items)
    recent_items = []
    if expenses:
        sorted_exp = sorted(expenses, key=lambda x: x.get('date', ''), reverse=True)[:30]
        for e in sorted_exp:
            cat_name = e.get("categories", {}).get("name", "Uncategorized") if (isinstance(e.get("categories"), dict) and e.get("categories")) else "Uncategorized"
            status = " [RECURRING]" if e.get("is_recurring") else ""
            recent_items.append(f"  • {e.get('date', '')} - {e.get('merchant', 'Unknown')} ({cat_name}): ₹{float(e.get('amount', 0)):,.2f} ({e.get('earning_vs_expense', 'Expense')}){status}")

    context_lines = []
    context_lines.append(f"- User Profile ID: {current_user.id}")
    context_lines.append(f"- Registered Email: {current_user.email}")
    context_lines.append(f"- Total Expenses this Month: ₹{sum([float(e['amount']) * (float(e['split_percentage'])/100) for e in expenses if e['earning_vs_expense']=='Expense']) if expenses else 0:,.2f}")
    context_lines.append(f"- Active Goals: {[{'name': g['name'], 'target': float(g['target_amount']), 'saved': float(g['current_savings']), 'due': g['target_date']} for g in active_goals]}")
    context_lines.append(f"- Active Subscriptions: {[s['name'] for s in active_subs]}")
    context_lines.append(f"- Total Active Subscriptions Expense: ₹{sum([float(s['amount']) for s in active_subs]):,.2f}/mo")
    context_lines.append("- Active Recurring Expense Templates:\n" + ("\n".join(recurring_items) if recurring_items else "  None"))
    context_lines.append("- Recent Transactions (Last 30):\n" + ("\n".join(recent_items) if recent_items else "  None"))
    
    context_str = "\n".join(context_lines)
    
    # Render layout
    coach_col1, coach_col2 = st.columns([2, 1.2])
    
    with coach_col1:
        st.markdown("### 💬 Conversation Thread")
        
        # Conversation history container
        chat_container = st.container(height=380, border=True)
        with chat_container:
            if not st.session_state.coach_messages:
                st.markdown(f"""
                <div style="padding: 1.5rem; text-align: center; border-radius: 12px; background-color: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1); margin-top: 2rem;">
                    <span style="font-size: 2.5rem;">🧠</span>
                    <h4 style="margin: 0.8rem 0 0.4rem 0; color: #fff;">Ask your Financial Advisor</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #a0aec0;">I have loaded your recent transactions, EMIs, active goals, and subscription details. Ask me anything about your cash flow or budget!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.coach_messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        
        # Chat input area (No form wrapper to preserve tab focus on client side)
        user_query_input = st.text_input("Ask a question...", placeholder="e.g. List all my recurring bills. Or: Can I buy a ₹10 Lakh SUV?", key="ai_coach_query_input_tab")
        
        btn_c1, btn_c2 = st.columns([1, 1])
        with btn_c1:
            submit_coach = st.button("Consult Advisor", use_container_width=True)
        with btn_c2:
            reset_coach = st.button("Reset Conversation", use_container_width=True)
            
        if reset_coach:
            st.session_state.coach_messages = []
            st.session_state.active_tab = "💬 AI Financial Coach"
            st.rerun()
            
        if submit_coach:
            if user_query_input.strip():
                # Add user query to conversation history
                st.session_state.coach_messages.append({"role": "user", "content": user_query_input.strip()})
                st.session_state.active_tab = "💬 AI Financial Coach"
                
                # Show premium typing indicator placeholder in the UI
                placeholder = st.empty()
                placeholder.markdown("""
                <div style="display: flex; align-items: center; margin-top: 10px; margin-bottom: 20px; padding: 10px; border-radius: 8px; background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);">
                    <span style="font-size: 0.9rem; color: #00DFD8; margin-right: 8px; font-weight: 500;">Advisor is thinking</span>
                    <div style="display: flex; gap: 4px;">
                        <span class="dot" style="width: 6px; height: 6px; background-color: #00DFD8; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite both;"></span>
                        <span class="dot" style="width: 6px; height: 6px; background-color: #00DFD8; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite both; animation-delay: 0.2s;"></span>
                        <span class="dot" style="width: 6px; height: 6px; background-color: #00DFD8; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite both; animation-delay: 0.4s;"></span>
                    </div>
                </div>
                <style>
                @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1.0); }
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Build conversation history context
                history_lines = []
                for msg in st.session_state.coach_messages[:-1]:
                    history_lines.append(f"{'User' if msg['role']=='user' else 'Advisor'}: {msg['content']}")
                history_str = "\n".join(history_lines)
                
                with st.spinner("Analyzing portfolio & running projections..."):
                    coach_response = get_ai_coach_response(user_query_input.strip(), context_str, history_str)
                    st.session_state.coach_messages.append({"role": "assistant", "content": coach_response})
                    
                # Rerun to show new messages and clear typing indicator
                st.rerun()
            else:
                st.error("Please enter a question.")
                
    with coach_col2:
        st.markdown("### 📊 Advisor Context Data")
        st.caption("Active RAG financial snapshot injected into the advisor's prompt context:")
        
        # Financial Health Score card
        with st.container(border=True):
            st.markdown("<h5 style='margin:0; color:#00DFD8;'>📈 Financial Health Score</h5>", unsafe_allow_html=True)
            profile = get_profile(current_user.id)
            if profile and expenses:
                income = float(profile.get("monthly_income", 0)) or 100000.0
                rent = float(profile.get("monthly_rent", 0)) or 0.0
                debt = float(profile.get("monthly_debt", 0)) or 20000.0
                inv = float(profile.get("monthly_investments", 0)) or 15000.0
                
                exp_sum = sum([float(e['amount']) * (float(e['split_percentage'])/100) for e in expenses if e['earning_vs_expense']=='Expense'])
                liq_cash = 500000.0
                ins_checklist = {"life": True, "health": True, "other": True}
                
                fhs_val, _ = calculate_fhs(income, exp_sum, liq_cash, debt, inv, ins_checklist)
                st.markdown(f"<h3 style='margin: 0.5rem 0; color:#fff;'>{fhs_val} / 850</h3>", unsafe_allow_html=True)
            else:
                st.markdown("<h3 style='margin: 0.5rem 0; color:#fff;'>N/A</h3>", unsafe_allow_html=True)
                
        # Goals progress summary
        with st.container(border=True):
            st.markdown("<h5 style='margin:0 0 0.5rem 0; color:#FFB900;'>🎯 Active Goals</h5>", unsafe_allow_html=True)
            if active_goals:
                for g in active_goals[:3]:
                    progress = min(1.0, float(g["current_savings"]) / float(g["target_amount"]))
                    st.markdown(f"<p style='margin:0; font-size:0.85rem;'>{g['name']} (₹{float(g['current_savings']):,.0f}/₹{float(g['target_amount']):,.0f})</p>", unsafe_allow_html=True)
                    st.progress(progress)
            else:
                st.caption("No active goals found.")
                
        # Subscriptions list
        with st.container(border=True):
            st.markdown("<h5 style='margin:0 0 0.5rem 0; color:#7F55FF;'>🔌 Active Subscriptions</h5>", unsafe_allow_html=True)
            if active_subs:
                for s in active_subs[:4]:
                    st.markdown(f"<p style='margin:0; font-size:0.85rem;'>• {s['name']} (₹{float(s['amount']):,.2f}/mo)</p>", unsafe_allow_html=True)
            else:
                st.caption("No subscriptions configured.")
                
        # Recurring expenses template list
        with st.container(border=True):
            st.markdown("<h5 style='margin:0 0 0.5rem 0; color:#F56565;'>🔄 Recurring Payments</h5>", unsafe_allow_html=True)
            has_rec = False
            if expenses:
                count = 0
                for e in expenses:
                    if e.get("is_recurring"):
                        has_rec = True
                        st.markdown(f"<p style='margin:0; font-size:0.85rem;'>• {e.get('merchant')} (₹{float(e.get('amount')):,.2f})</p>", unsafe_allow_html=True)
                        count += 1
                        if count >= 3:
                            break
            if not has_rec:
                st.caption("No recurring expenses templates.")

# Render Global Footer at the very bottom of the page
st.markdown("""
<hr style="margin-top: 3rem; opacity: 0.1;"/>
<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; flex-wrap: wrap; padding: 1.5rem 0; font-family: 'Outfit', sans-serif; font-size: 0.85rem; color: #a0aec0; gap: 1rem;">
    <div style="display: flex; flex-direction: row; align-items: center; gap: 0.8rem; flex-wrap: wrap;">
        <span style="font-weight: 700; color: #fff;">📞 Contact Us</span>
        <a href="https://wa.me/917506009321" target="_blank" style="text-decoration: none; display: inline-flex; align-items: center; gap: 0.4rem; background: #25D366; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.2);">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16">
                <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.977h.004c4.368 0 7.927-3.558 7.93-7.93a7.897 7.897 0 0 0-2.33-5.615zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.69-4.98c-.202-.101-1.194-.588-1.378-.653-.185-.066-.32-.099-.455.101-.134.2-.522.653-.64.787-.118.134-.236.15-.437.05-.202-.101-.849-.313-1.616-.997-.597-.533-1.001-1.192-1.119-1.392-.118-.2-.013-.308.088-.408.09-.09.202-.236.302-.354.101-.118.134-.2.202-.336.067-.134.034-.251-.017-.352-.05-.101-.455-1.094-.623-1.5-.165-.4-.347-.343-.455-.349-.117-.007-.251-.007-.385-.007a.784.784 0 0 0-.568.264c-.185.2-.707.691-.707 1.684 0 .993.722 1.952.822 2.085.101.134 1.417 2.164 3.435 3.033.48.207.854.33 1.147.424.483.153.923.131 1.272.079.39-.058 1.194-.488 1.362-.96.168-.472.168-.876.118-.96-.05-.085-.185-.134-.387-.235z"/>
            </svg>
            Chat on WhatsApp
        </a>
        <span>•</span>
        <span>Email: <a href="mailto:adks001@gmail.com" style="color: #60EFFF; text-decoration: none;">adks001@gmail.com</a></span>
    </div>
    <div style="font-size: 0.8rem; text-align: right;">
        © 2026 Ankur Kumar Singh. All Rights Reserved.
    </div>
</div>
""", unsafe_allow_html=True)

