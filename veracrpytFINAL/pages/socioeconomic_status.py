import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from utils.database import Database
from utils.config import get_survey_config
from utils.session_manager import SessionManager
import pandas as pd

# Get survey-specific configuration
config = get_survey_config('socioeconomic_status')
SESSION_DURATION_MINUTES = config['SESSION_DURATION_MINUTES']

# Initialize session state for theme if it doesn't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Set page configuration
st.set_page_config(
    page_title="Socioeconomic Status - VeraCrypt",
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
    """Display the financial hardship survey form and handle submissions."""
    st.title("Financial Hardship Survey")
    st.write("Please fill out the survey below.")
    
    with st.form("financial_hardship_survey", clear_on_submit=True):
        # Demographics
        age = st.number_input("Age:", min_value=16, max_value=100, step=1)
        gender = st.selectbox("Gender:", ["Male", "Female", "Non-binary", "Other", "Prefer not to say"])
        academic_year = st.selectbox("Academic Year:", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
        living_situation = st.selectbox("Living Situation:", ["On-campus", "Off-campus"])
        employment_status = st.selectbox("Employment Status:", ["Unemployed", "Part-time", "Full-time"])

        # Financial Hardship Factors
        access_financial_aid = st.selectbox("Do you have access to financial aid?", ["Yes", "No"])
        receiving_scholarships = st.selectbox("Are you receiving scholarships?", ["Yes", "No"])
        food_insecurity = st.selectbox("How often do you experience food insecurity?", ["Never", "Sometimes", "Often"])
        housing_instability = st.selectbox("Housing Stability:", ["Stable", "Unstable"])
        financial_stress = st.slider("Financial Stress Level (1-10):", 1, 10, 5)
        impact_academic = st.slider("Impact of Financial Hardship on Academic Success (1-10):", 1, 10, 5)

        st.info("🔒 Your responses are encrypted and will be deleted after the session expires")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            try:
                response_data = {
                    'age': age,
                    'gender': gender,
                    'academic_year': academic_year,
                    'living_situation': living_situation,
                    'employment_status': employment_status,
                    'access_financial_aid': access_financial_aid,
                    'receiving_scholarships': receiving_scholarships,
                    'food_insecurity': food_insecurity,
                    'housing_instability': housing_instability,
                    'financial_stress': financial_stress,
                    'impact_academic': impact_academic,
                    'submitted_at': datetime.utcnow().isoformat()
                }
                
                db.store_response(response_data, session_id)
                st.success("Thank you for completing the survey!")
                
                # Display responses
                st.write("### Your Responses:")
                st.write(f"**Age:** {age}")
                st.write(f"**Gender:** {gender}")
                st.write(f"**Academic Year:** {academic_year}")
                st.write(f"**Living Situation:** {living_situation}")
                st.write(f"**Employment Status:** {employment_status}")
                st.write(f"**Food Insecurity:** {food_insecurity}")
                st.write(f"**Housing Instability:** {housing_instability}")
                st.write(f"**Financial Stress Level:** {financial_stress}")
                st.write(f"**Impact on Academic Success:** {impact_academic}")
                st.write(f"**Access to Financial Aid:** {access_financial_aid}")
                st.write(f"**Receiving Scholarships:** {receiving_scholarships}")
                
                st.balloons()
                
            except Exception as e:
                st.error(f"Error submitting survey: {str(e)}")

def display_synthetic_data(synthetic_datasets):
    """Display synthetic data with socioeconomic-specific visualizations"""
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
                
                # Income Distribution
                st.subheader("Income Distribution")
                if 'income_range' in dataset['data'].columns:
                    income_dist = dataset['data']['income_range'].value_counts()
                    st.bar_chart(income_dist)
                
                # Financial Stress Metrics
                st.subheader("Financial Stress Indicators")
                metrics_cols = st.columns(3)
                
                with metrics_cols[0]:
                    if 'financial_stress' in dataset['data'].columns:
                        avg_stress = dataset['data']['financial_stress'].mean()
                        st.metric("Average Financial Stress", f"{avg_stress:.2f}/5")
                
                with metrics_cols[1]:
                    if 'education_impact' in dataset['data'].columns:
                        avg_impact = dataset['data']['education_impact'].mean()
                        st.metric("Education/Work Impact", f"{avg_impact:.2f}/5")
                
                with metrics_cols[2]:
                    if 'household_size' in dataset['data'].columns:
                        avg_household = dataset['data']['household_size'].mean()
                        st.metric("Average Household Size", f"{avg_household:.1f}")
                
                # Common Challenges
                if 'financial_difficulties' in dataset['data'].columns:
                    st.subheader("Common Financial Challenges")
                    difficulties = dataset['data']['financial_difficulties'].explode().value_counts()
                    st.bar_chart(difficulties)
            
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

def generate_survey_link():
    """Generate a new survey session link"""
    session_manager = SessionManager(SESSION_DURATION_MINUTES, 'socioeconomic_status')
    link, expiry_time = session_manager.generate_session_link()
    
    st.markdown(
        f"""
        <div class="survey-section">
            <h3>🔗 Survey Session Link</h3>
            <p>Access your personalized socioeconomic status survey by clicking the button below.</p>
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
    
    # Add copy button
    if st.button("Copy Link", key="copy_link"):
        st.code(link)
        st.success("Link copied to clipboard! Share this link with participants.")
        
    return link

def display_responses(db):
    """Display encrypted responses and statistics"""
    st.markdown("### 📊 Encrypted Survey Responses")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    stats = db.get_response_stats()
    
    # Display statistics in multiple columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Active Responses", stats['total_responses'])
    with col2:
        st.metric("Last Updated", stats['last_updated'].strftime("%H:%M:%S"))
    with col3:
        # Calculate time until next expiry
        current_time = datetime.utcnow()
        next_expiry = None
        try:
            next_expiry = db.collection.find_one(
                {'expires_at': {'$gt': current_time}},
                sort=[('expires_at', 1)]
            )
        except Exception:
            pass
        
        if next_expiry:
            time_remaining = next_expiry['expires_at'] - current_time
            minutes_remaining = int(time_remaining.total_seconds() / 60)
            st.metric("Next Response Expiry", f"{minutes_remaining} minutes")

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
        
        # Display the dataframe with custom column configurations
        st.dataframe(
            df,
            column_config={
                "Response ID": st.column_config.TextColumn(
                    "Response ID",
                    help="Unique identifier for each response",
                    width="medium"
                ),
                "Created At": st.column_config.DatetimeColumn(
                    "Created At",
                    format="D MMM, YYYY, HH:mm:ss",
                    help="When the response was submitted"
                ),
                "Expires At": st.column_config.DatetimeColumn(
                    "Expires At",
                    format="D MMM, YYYY, HH:mm:ss",
                    help="When the response will be automatically deleted"
                ),
                "Encrypted Data": st.column_config.TextColumn(
                    "Encrypted Data",
                    help="Encrypted response data for privacy",
                    width="large"
                ),
            },
            hide_index=True,
        )
        
        # Add a note about data privacy
        st.info("""
        ℹ️ **Privacy Notice**
        - All response data is end-to-end encrypted
        - Data is automatically deleted after expiration
        - No personally identifiable information is stored
        - Access to raw data is strictly controlled
        """)
        
    except Exception as e:
        st.error(f"Error displaying encrypted responses: {str(e)}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

def main():
    if st.button("← Back to Dashboard"):
        st.switch_page("/survey_dashboard.py")

    st.markdown("<div class='title'>Socioeconomic Status Survey</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Help us understand economic challenges and develop effective support strategies</div>",
        unsafe_allow_html=True
    )
    
    try:
        db = Database('socioeconomic_status')
        
        session_id = st.query_params.get("session", None)
        
        if session_id:
            # Respondent view
            session_manager = SessionManager(SESSION_DURATION_MINUTES, 'socioeconomic_status')
            if session_manager.validate_session(session_id):
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
                generate_survey_link()
            
            with tab2:
                display_responses(db)
                
            with tab3:
                synthetic_datasets = db.cleanup_expired_sessions()
                if synthetic_datasets:
                    display_synthetic_data(synthetic_datasets)
                else:
                    st.info("No synthetic data available yet. It will appear here when sessions expire.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()