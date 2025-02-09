import streamlit as st
from datetime import datetime
from utils.database import Database

# Initialize session state for theme if it doesn't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Set page configuration
st.set_page_config(
    page_title="Veracrypt Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add this near the top of your main content section, before the title
if st.button("← Back to Home"):
    st.switch_page("Home.py")

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

THEME_COLORS = {
    'light': {
        'bg': '#f7f4ed',  # Light beige/cream background
        'text': '#2c2c2c',  # Darker muted gray for text
        'card_bg': '#ffffff',  # White card background
        'card_shadow': '0 4px 6px rgba(0,0,0,0.1)',
        'gradient': 'linear-gradient(120deg, #8fa3bf, #6d7f99)',  # Muted blue-gray gradient
        'subtitle': '#6d7f99',  # Subtle blue-gray for subtitles
        'stat_number': '#2c3e50',
        'stat_label': '#516170',
        'card_border': 'rgba(44, 62, 80, 0.08)',
        'hover_shadow': '0 8px 15px rgba(0,0,0,0.15)'
    },
    'dark': {
        'bg': '#1a1a1a',
        'text': '#ffffff',
        'card_bg': '#2d2d2d',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.3)',
        'gradient': 'linear-gradient(120deg, #64B5F6, #1E88E5)',
        'subtitle': '#a0a0a0',
        'stat_number': '#64B5F6',
        'stat_label': '#a0a0a0',
        'card_border': '#404040'
    }
}
THEME_COLORS = {
    'light': {
        'bg': '#f7f4ed',  # Light beige/cream background
        'text': '#2c2c2c',  # Darker muted gray for text
        'card_bg': '#ffffff',  # White card background
        'card_shadow': '0 4px 6px rgba(0,0,0,0.1)',
        'gradient': 'linear-gradient(120deg, #8fa3bf, #6d7f99)',  # Muted blue-gray gradient
        'subtitle': '#6d7f99',  # Subtle blue-gray for subtitles
        'stat_number': '#2c3e50',
        'stat_label': '#516170',
        'card_border': 'rgba(44, 62, 80, 0.08)',
        'hover_shadow': '0 8px 15px rgba(0,0,0,0.15)'
    },
    'dark': {
        'bg': '#1a1a1a',
        'text': '#ffffff',
        'card_bg': '#2d2d2d',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.3)',
        'gradient': 'linear-gradient(120deg, #64B5F6, #1E88E5)',
        'subtitle': '#a0a0a0',
        'stat_number': '#64B5F6',
        'stat_label': '#a0a0a0',
        'card_border': '#404040'
    }
}
THEME_COLORS = {
    'light': {
        'bg': '#f7f4ed',  # Light beige/cream background
        'text': '#2c2c2c',  # Darker muted gray for text
        'card_bg': '#ffffff',  # White card background
        'card_shadow': '0 4px 6px rgba(0,0,0,0.1)',
        'gradient': 'linear-gradient(120deg, #8fa3bf, #6d7f99)',  # Muted blue-gray gradient
        'subtitle': '#6d7f99',  # Subtle blue-gray for subtitles
        'stat_number': '#2c3e50',
        'stat_label': '#516170',
        'card_border': 'rgba(44, 62, 80, 0.08)',
        'hover_shadow': '0 8px 15px rgba(0,0,0,0.15)'
    },
    'dark': {
        'bg': '#1a1a1a',
        'text': '#ffffff',
        'card_bg': '#2d2d2d',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.3)',
        'gradient': 'linear-gradient(120deg, #64B5F6, #1E88E5)',
        'subtitle': '#a0a0a0',
        'stat_number': '#64B5F6',
        'stat_label': '#a0a0a0',
        'card_border': '#404040'
    }
}
THEME_COLORS = {
    'light': {
        'bg': '#f7f4ed',  # Light beige/cream background
        'text': '#2c2c2c',  # Darker muted gray for text
        'card_bg': '#ffffff',  # White card background
        'card_shadow': '0 4px 6px rgba(0,0,0,0.1)',
        'gradient': 'linear-gradient(120deg, #8fa3bf, #6d7f99)',  # Muted blue-gray gradient
        'subtitle': '#6d7f99',  # Subtle blue-gray for subtitles
        'stat_number': '#2c3e50',
        'stat_label': '#516170',
        'card_border': 'rgba(44, 62, 80, 0.08)',
        'hover_shadow': '0 8px 15px rgba(0,0,0,0.15)'
    },
    'dark': {
        'bg': '#1a1a1a',
        'text': '#ffffff',
        'card_bg': '#2d2d2d',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.3)',
        'gradient': 'linear-gradient(120deg, #64B5F6, #1E88E5)',
        'subtitle': '#a0a0a0',
        'stat_number': '#64B5F6',
        'stat_label': '#a0a0a0',
        'card_border': '#404040'
    }
}
def get_css(theme_colors):
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    body {{
        font-family: 'Poppins', sans-serif;
        background: {theme_colors['bg']};
        color: {theme_colors['text']};
        min-height: 100vh;
    }}
    
    .stApp {{
        background: {theme_colors['bg']};
    }}

    h1 {{
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-align: left;
        color: {theme_colors['text']};
    }}
    
    h3 {{
        font-size: 1.4rem;
        font-weight: 400;
        color: #000000;  /* Black subtitle text */
        margin-bottom: 1.5rem;
        line-height: 1.3;
    }}
    
    .category-card {{
        background: {theme_colors['card_bg']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: {theme_colors['card_shadow']};
        margin-bottom: 1rem;
        border: 1px solid {theme_colors['card_border']};
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .category-card:hover {{
        transform: translateY(-5px);
        box-shadow: {theme_colors['hover_shadow']};
    }}
    
    .category-card h3 {{
        color: {theme_colors['stat_number']};
        font-size: 1.4rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }}
    
    .category-description {{
        color: #000000;  /* Black for category descriptions */
        font-size: 1rem;
        line-height: 1.5;
    }}

    .stButton button {{
        background: {theme_colors['gradient']};
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        transition: opacity 0.2s;
    }}
    
    .stButton button:hover {{
        opacity: 0.9;
    }}
    </style>
    """

# Apply current theme CSS
st.markdown(get_css(THEME_COLORS[st.session_state.theme]), unsafe_allow_html=True)

# Theme toggle button in sidebar
with st.sidebar:
    st.image("logo.png")
    if st.button("🌓 Toggle Theme", key="theme_toggle"):
        toggle_theme()
        st.experimental_rerun()

# Initialize database for stats
try:
    db = Database()
    stats = db.get_response_stats()
except Exception as e:
    stats = {'total_responses': 0, 'last_updated': datetime.utcnow()}

# Title and description
st.markdown("<h1>Welcome to VeraCrypt Surveys</h1>", unsafe_allow_html=True)
st.markdown("<h3>Discover meaningful insights through anonymous surveys</h3>", unsafe_allow_html=True)

# Survey categories
categories = {
    "Mental Health & Well-being": {
        "description": "Gain valuable insights into community mental health trends and support needs through anonymous feedback",
        "url": "mental_health"
    },
    "Academic Integrity & Performance": {
        "description": "Evaluate academic honesty practices and identify areas for improving educational outcomes",
        "url": "academic_integrity"
    },
    "Socioeconomic Status & Financial Hardship": {
        "description": "Understand economic challenges and develop targeted support strategies for your community",
        "url": "socioeconomic_status"
    },
    "Diversity, Equality & Inclusion": {
        "description": "Assess inclusivity initiatives and gather insights to create a more equitable environment",
        "url": "diversity_equality"
    },
    "Sexual Health & Awareness": {
        "description": "Promote comprehensive sexual health education and awareness through confidential feedback",
        "url": "sexual_health"
    },
    "Substance Use & Risk Behavior": {
        "description": "Address substance use patterns and develop effective prevention strategies",
        "url": "substance_use"
    }
}

# Display survey options in two columns using custom grid layout
# Display survey options in two columns using custom grid layout with clickable URLs
for category, info in categories.items():
    st.markdown(f"""
        <div class="category-card">
            <h3>{category}</h3>
            <p class="category-description">{info['description']}</p>
            <a href="{info['url']}" style="
                background: {THEME_COLORS[st.session_state.theme]['gradient']}; 
                color: white; 
                padding: 0.5rem 1rem; 
                border-radius: 5px; 
                text-decoration: none; 
                display: inline-block;
            ">Explore {category}</a>
        </div>
    """, unsafe_allow_html=True)


# Footer with privacy notice
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: var(--text-color); padding: 1rem;'>
        🔒 All surveys are completely anonymous and encrypted. Data automatically expires after 2 minutes.
    </div>
""", unsafe_allow_html=True)
