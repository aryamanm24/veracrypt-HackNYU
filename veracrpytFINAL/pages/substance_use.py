import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from utils.database import Database
from utils.config import get_survey_config
from utils.session_manager import SessionManager
import pandas as pd

# Get survey-specific configuration
config = get_survey_config('substance_use')
SESSION_DURATION_MINUTES = config['SESSION_DURATION_MINUTES']

# Initialize session state for theme if it doesn't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Set page configuration
st.set_page_config(
    page_title="Substance Use Survey - VeraCrypt",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Define theme colors
THEME_COLORS = {
    'light': {
        'bg': 'linear-gradient(135deg, rgba(242,240,233,0.95), rgba(242,240,233,0.85))',
        'text': '#2C3E50',
        'card_bg': 'rgba(255, 255, 255, 0.9)',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.08)',
        'gradient': 'linear-gradient(120deg, #34495E, #2C3E50)',
        'subtitle': '#516170',
        'stat_number': '#34495E',
        'stat_label': '#516170',
        'card_border': 'rgba(44, 62, 80, 0.1)'
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

# Enhanced CSS with theme support
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

    .title {{
        font-size: 2.5rem;
        font-weight: bold;
        background: {theme_colors['gradient']};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}
    
    .subtitle {{
        font-size: 1.2rem;
        color: {theme_colors['subtitle']};
        margin-bottom: 2rem;
    }}
    
    .resource-card, .upload-section {{
        background: {theme_colors['card_bg']};
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: {theme_colors['card_shadow']};
        border: 1px solid {theme_colors['card_border']};
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .resource-card:hover, .upload-section:hover {{
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }}
    
    .resource-title, .upload-title {{
        color: {theme_colors['text']};
        font-size: 1.4rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }}
    
    .resource-description, .upload-description {{
        color: {theme_colors['subtitle']};
        margin-bottom: 1rem;
    }}
    
    .resource-link {{
        color: {theme_colors['stat_number']};
        text-decoration: none;
        font-weight: 600;
        transition: opacity 0.2s;
    }}
    
    .resource-link:hover {{
        opacity: 0.8;
    }}
    
    .success-message {{
        color: #2ecc71;
        font-weight: 600;
        margin-top: 1rem;
        padding: 0.5rem;
        border-radius: 5px;
        background: rgba(46, 204, 113, 0.1);
        border: 1px solid rgba(46, 204, 113, 0.2);
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

    /* File uploader customization */
    .stFileUploader {{
        background: {theme_colors['card_bg']};
        padding: 1rem;
        border-radius: 5px;
        border: 1px dashed {theme_colors['card_border']};
    }}

    .uploadedFile {{
        background: {theme_colors['card_bg']};
        color: {theme_colors['text']};
    }}

    .survey-section {{
        background: {theme_colors['card_bg']};
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid {theme_colors['card_border']};
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
        st.rerun()

def display_survey_form(db, session_id):
    """Display a simplified substance use survey form and handle submissions."""
    st.title("Substance Use Survey")
    st.write("Please fill out the survey below.")
    
    with st.form("substance_use_survey", clear_on_submit=True):
        # Substance Use Patterns
        alcohol_use = st.selectbox(
            "How often do you consume alcohol?",
            ["Never", "Rarely", "Sometimes", "Often"]
        )
        
        tobacco_use = st.selectbox(
            "How often do you use tobacco?",
            ["Never", "Rarely", "Sometimes", "Often"]
        )
        
        drug_use = st.selectbox(
            "How often do you use drugs?",
            ["Never", "Rarely", "Sometimes", "Often"]
        )
        
        # Rating Scales
        peer_pressure = st.slider(
            "Rate the level of peer pressure you experience (1-10):",
            1, 10, 5
        )
        
        academic_performance = st.slider(
            "Rate your academic performance (1-10):",
            1, 10, 5
        )
        
        well_being = st.slider(
            "Rate your overall well-being (1-10):",
            1, 10, 5
        )

        st.info("🔒 Your responses are encrypted and will be deleted after the session expires")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            try:
                response_data = {
                    'alcohol_use': alcohol_use,
                    'tobacco_use': tobacco_use,
                    'drug_use': drug_use,
                    'peer_pressure': peer_pressure,
                    'academic_performance': academic_performance,
                    'well_being': well_being,
                    'submitted_at': datetime.utcnow().isoformat()
                }
                
                db.store_response(response_data, session_id)
                st.success("Thank you for completing the survey!")
                
                # Display responses
                st.write("### Your Responses:")
                st.write(f"**Alcohol Use:** {alcohol_use}")
                st.write(f"**Tobacco Use:** {tobacco_use}")
                st.write(f"**Drug Use:** {drug_use}")
                st.write(f"**Peer Pressure Level:** {peer_pressure}")
                st.write(f"**Academic Performance:** {academic_performance}")
                st.write(f"**Well-Being Level:** {well_being}")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Error submitting survey: {str(e)}")

def generate_survey_link():
    """Generate a new survey session link"""
    session_manager = SessionManager(SESSION_DURATION_MINUTES, 'substance_use')
    link, expiry_time = session_manager.generate_session_link()
    
    st.markdown(
        f"""
        <div class="survey-section">
            <h3>🔗 Survey Session Link</h3>
            <p>Access your personalized substance use survey by clicking the button below.</p>
            <a href="{link}" target="_blank" style="text-decoration: none;">
                <button>Access Survey Session</button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display countdown timer
    time_remaining = expiry_time - datetime.utcnow()
    minutes_remaining = int(time_remaining.total_seconds() / 60)
    
    st.markdown(
        f"""
        <div class="survey-section">
            <h3>⏱️ Session Expiry Information</h3>
            <p>Session expires in <strong>{minutes_remaining} minutes</strong>.</p>
            <p>- This link will be active for {SESSION_DURATION_MINUTES} minutes.</p>
            <p>- Multiple responses can be collected during this time.</p>
            <p>- All responses will be automatically deleted after session expiry.</p>
            <p>- Your privacy and anonymity are guaranteed throughout the process.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.button("Copy Link", key="copy_link"):
        st.code(link)
        st.success("Link copied to clipboard!")
        
    return link

def display_responses(db):
    """Display encrypted responses and statistics"""
    st.markdown("### 📊 Encrypted Survey Responses")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    stats = db.get_response_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Active Responses", stats['total_responses'])
    with col2:
        st.metric("Last Updated", stats['last_updated'].strftime("%H:%M:%S"))

    st.warning("🔒 For privacy and security, all responses are shown in their encrypted form.")
    
    try:
        current_time = datetime.utcnow()
        cursor = db.collection.find({
            'expires_at': {'$gt': current_time}
        }).sort('created_at', -1)
        
        encrypted_responses = list(cursor)
        
        if not encrypted_responses:
            st.info("No active responses found. Responses may have expired or none have been submitted yet.")
            return
        
        display_data = []
        for resp in encrypted_responses:
            display_data.append({
                'Response ID': str(resp['_id']),
                'Encrypted Data': resp['data'],
                'Created At': resp['created_at'],
                'Expires At': resp['expires_at']
            })
        
        df = pd.DataFrame(display_data)
        
        st.dataframe(
            df,
            column_config={
                "Created At": st.column_config.DatetimeColumn(format="D MMM, YYYY, HH:mm:ss"),
                "Expires At": st.column_config.DatetimeColumn(format="D MMM, YYYY, HH:mm:ss"),
                "Encrypted Data": st.column_config.TextColumn(width="large"),
            },
            hide_index=True,
        )
        
    except Exception as e:
        st.error(f"Error displaying encrypted responses: {str(e)}")

def display_synthetic_data(synthetic_datasets):
    """Display synthetic data with substance use specific visualizations"""
    if synthetic_datasets:
        st.markdown("### 📊 Synthetic Data Generated")
        
        for i, dataset in enumerate(synthetic_datasets, 1):
            st.markdown(f"#### Synthetic Dataset {i}")
            
            data_tab, visualizations_tab, corr_tab = st.tabs([
                "Dataset Preview", 
                "Visualizations",
                "Correlation Analysis"
            ])
            
            with data_tab:
                st.markdown("**Preview of Synthetic Data**")
                st.dataframe(dataset['data'].head())
                
                csv = dataset['data'].to_csv(index=False)
                st.download_button(
                    label="💾 Download Complete Synthetic Dataset (CSV)",
                    data=csv,
                    file_name=dataset['filename'],
                    mime='text/csv',
                    key=f"download_{i}"
                )
            
            with visualizations_tab:
                st.markdown("**📈 Key Insights**")
                
                # Usage Patterns
                st.subheader("Substance Use Patterns")
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'alcohol_frequency' in dataset['data'].columns:
                        alcohol_dist = dataset['data']['alcohol_frequency'].value_counts()
                        st.bar_chart(alcohol_dist)
                        st.markdown("**Alcohol Use Distribution**")
                
                with col2:
                    if 'cannabis_use' in dataset['data'].columns:
                        cannabis_dist = dataset['data']['cannabis_use'].value_counts()
                        st.bar_chart(cannabis_dist)
                        st.markdown("**Cannabis Use Distribution**")
                
                # Risk and Support Metrics
                st.subheader("Risk and Support Indicators")
                metrics_cols = st.columns(3)
                
                with metrics_cols[0]:
                    if 'stress_level' in dataset['data'].columns:
                        avg_stress = dataset['data']['stress_level'].mean()
                        st.metric("Average Stress Level", f"{avg_stress:.2f}/5")
                
                with metrics_cols[1]:
                    if 'support_awareness' in dataset['data'].columns:
                        support_dist = dataset['data']['support_awareness'].value_counts()
                        aware_pct = (
                            (support_dist.get('Very aware', 0) + support_dist.get('Somewhat aware', 0))
                            / len(dataset['data']) * 100
                        )
                        st.metric("Resource Awareness", f"{aware_pct:.1f}%")
                
                with metrics_cols[2]:
                    if 'education_effectiveness' in dataset['data'].columns:
                        avg_effectiveness = dataset['data']['education_effectiveness'].mean()
                        st.metric("Education Effectiveness", f"{avg_effectiveness:.2f}/5")
            
            with corr_tab:
                st.markdown("**📊 Correlation Analysis**")
                numeric_cols = dataset['data'].select_dtypes(include=['float64', 'int64']).columns
                if not numeric_cols.empty:
                    corr_matrix = dataset['data'][numeric_cols].corr()
                    st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlBu'))
                    
                    st.markdown("**Notable Correlations:**")
                    for col1 in numeric_cols:
                        for col2 in numeric_cols:
                            if col1 < col2:
                                corr = corr_matrix.loc[col1, col2]
                                if abs(corr) > 0.5:
                                    st.write(f"- {col1} vs {col2}: {corr:.2f}")
                else:
                    st.info("No numerical data available for correlation analysis.")
            
            st.markdown("---")
    else:
        st.info("No synthetic data available yet. It will appear here when sessions expire.")

def main():
    if st.button("← Back to Dashboard"):
        st.switch_page("/survey_dashboard.py")

    st.markdown("<div class='title'>Substance Use & Risk Behavior Survey</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Help us understand patterns and develop effective prevention strategies</div>",
        unsafe_allow_html=True
    )
    
    try:
        db = Database('substance_use')  # Initialize with substance use survey type
        
        session_id = st.query_params.get("session", None)
        
        if session_id:
            # Respondent view
            session_manager = SessionManager(SESSION_DURATION_MINUTES, 'substance_use')
            if session_manager.validate_session(session_id):
                # Extra privacy notice for sensitive data
                st.info("""
                🔒 **Privacy Notice**
                - All responses are completely anonymous
                - Data is encrypted end-to-end
                - No personally identifiable information is collected
                - Responses are automatically deleted after the session expires
                """)
                display_survey_form(db, session_id)
            else:
                st.error("This survey session has expired.")
                synthetic_datasets = db.cleanup_expired_sessions()
                if synthetic_datasets:
                    display_synthetic_data(synthetic_datasets)
                st.info("Please request a new survey link from the administrator.")
        else:
            # Admin view - show link generator and responses
            tab1, tab2, tab3 = st.tabs(["📝 Generate Survey Link", "📊 View Responses", "🔄 Synthetic Data"])
            
            with tab1:
                st.markdown("""
                ### Generate Anonymous Survey Link
                Create a secure, time-limited link for collecting anonymous substance use data.
                Each session automatically expires to ensure data privacy.
                """)
                generate_survey_link()
            
            with tab2:
                st.markdown("""
                ### View Encrypted Responses
                Monitor incoming survey responses. All data is encrypted and anonymous.
                Responses are automatically removed after expiration.
                """)
                display_responses(db)
                
            with tab3:
                st.markdown("""
                ### Synthetic Data Analysis
                View anonymized patterns and trends from expired sessions.
                All data is aggregated and synthetic to protect individual privacy.
                """)
                synthetic_datasets = db.cleanup_expired_sessions()
                if synthetic_datasets:
                    display_synthetic_data(synthetic_datasets)
                else:
                    st.info("No synthetic data available yet. It will appear here when sessions expire.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("""
        If you're experiencing issues, please try:
        - Refreshing the page
        - Checking your connection
        - Requesting a new survey link
        """)

if __name__ == "__main__":
    main()