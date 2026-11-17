import plotly.express as px

# Soft, pale, feel-good pastel color themes
THEMES = {
    "Lavender Dream": {
        "bg": "#F8F6FF", "sidebar": "#EEE9FF", "primary": "#7C66DC",
        "secondary": "#E4DEFA", "card": "#F3F0FF", "accent": "#B4A3EE"
    },
    "Ocean Breeze": {
        "bg": "#F4F9FD", "sidebar": "#E5F1F9", "primary": "#4A90E2",
        "secondary": "#D2E6F7", "card": "#EBF4FC", "accent": "#8AB8E6"
    },
    "Soft Rose": {
        "bg": "#FFF8F9", "sidebar": "#FCE9ED", "primary": "#D67B94",
        "secondary": "#F9D6DF", "card": "#FFF0F3", "accent": "#E8ACB9"
    },
    "Mint Glow": {
        "bg": "#F4FAF7", "sidebar": "#E4F4ED", "primary": "#529E7E",
        "secondary": "#CFEADB", "card": "#EAF6F0", "accent": "#9DCDB7"
    },
    "Warm Peach": {
        "bg": "#FFFAF5", "sidebar": "#FDF0E2", "primary": "#D68C51",
        "secondary": "#F7DEC3", "card": "#FFF3E8", "accent": "#E8BC96"
    }
}

MULTI_PALETTE = px.colors.qualitative.Pastel + px.colors.qualitative.Set2

def get_custom_css(colors):
    return f"""
    <style>
    .stApp {{
        background: {colors['bg']};
        color: #333642;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background: {colors['sidebar']};
        border-right: 1px solid {colors['secondary']};
    }}
    h1, h2, h3 {{
        color: {colors['primary']} !important;
        font-weight: 700 !important;
    }}
    [data-testid="stMetric"] {{
        background: white;
        border-left: 5px solid {colors['primary']};
        border: 1px solid {colors['secondary']};
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .kpi-box {{
        background: white;
        border-left: 5px solid {colors['primary']};
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 10px;
        border-top: 1px solid {colors['secondary']};
        border-right: 1px solid {colors['secondary']};
        border-bottom: 1px solid {colors['secondary']};
    }}
    .kpi-title {{
        font-size: 12px;
        font-weight: 600;
        color: #7B7F93;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-value {{
        font-size: 24px;
        font-weight: 800;
        color: {colors['primary']};
        margin: 4px 0;
    }}
    .insight-card {{
        background: white;
        border-left: 5px solid #529E7E;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
        margin-bottom: 12px;
        border-top: 1px solid #E2F0EA;
        border-right: 1px solid #E2F0EA;
        border-bottom: 1px solid #E2F0EA;
    }}
    .stButton > button {{
        background: {colors['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        min-height: 40px;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background: {colors['accent']};
        color: #111;
    }}
    </style>
    """