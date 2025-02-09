import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from utils.database import Database
from utils.config import get_survey_config
from utils.session_manager import SessionManager
import pandas as pd

# Get survey-specific configuration
config = get_survey_config('academic_integrity')
SESSION_DURATION_MINUTES = config['SESSION_DURATION_MINUTES']

# Initialize session state for theme if it doesn't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Set page configuration
st.set_page_config(
    page_title="Academic Integrity - VeraCrypt",
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

    .stButton button {{
        background: linear-gradient(135deg, #7d8aa1, #5c6b84);  /* Muted gradient blue/gray */
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;  /* Larger padding for prominent button */
        border-radius: 5px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}

    .stButton button:hover {{
        opacity: 0.85;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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
    """Display the academic integrity survey form and handle submissions."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        
        with st.form("academic_integrity_survey", clear_on_submit=True):
            # Demographics
            st.subheader("Demographics")
            age = st.number_input("Age:", min_value=16, max_value=100, step=1)
            gender = st.selectbox("Gender:", ["Male", "Female", "Non-binary", "Other", "Prefer not to say"])
            academic_year = st.selectbox("Academic Year:", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
            living_situation = st.selectbox("Living Situation:", ["On-campus", "Off-campus"])
            employment_status = st.selectbox("Employment Status:", ["Unemployed", "Part-time", "Full-time"])
            
            # Mental Health Support & Resources
            professional_help = st.selectbox("Professional Help Utilization:", ["Never", "Occasionally", "Regularly"])
            access_counseling = st.selectbox("Access to Counseling:", ["Yes", "No", "Unsure"])
            support_network = st.slider("Support Network Rating (1-10):", 1, 10, 5)
            campus_resources = st.selectbox("Knowledge of Campus Resources:", ["Poor", "Moderate", "Good", "Excellent"])
            barriers_help = st.selectbox("Barriers to Seeking Help:", ["None", "Cost", "Availability", "Other"])
            
            # Financial Hardship Factors
            access_financial_aid = st.selectbox("Do you have access to financial aid?", ["Yes", "No"])
            receiving_scholarships = st.selectbox("Are you receiving scholarships?", ["Yes", "No"])
            food_insecurity = st.selectbox("How often do you experience food insecurity?", ["Never", "Sometimes", "Often"])
            housing_instability = st.selectbox("Housing Stability:", ["Stable", "Unstable"])
            financial_stress = st.slider("Financial Stress Level (1-10):", 1, 10, 5)
            impact_academic = st.slider("Impact of Financial Hardship on Academic Success (1-10):", 1, 10, 5)
            
            # Academic Integrity Factors
            experienced_dishonesty = st.selectbox("Have you experienced academic dishonesty?", ["Yes", "No"])
            type_of_dishonesty = st.selectbox("Type of Dishonesty:", ["None", "Plagiarism", "Cheating", "Other"])
            academic_integrity_pressure = st.slider("Perceived Pressure (1-10):", 1, 10, 5)
            study_hours_integrity = st.number_input("Study Hours Per Week:", min_value=0, max_value=100, step=1)
            workload_stress_integrity = st.slider("Workload Stress Level (1-10):", 1, 10, 5)

            st.info("🔒 Your responses are encrypted and will be deleted after the session expires")
            
            submitted = st.form_submit_button("Submit Survey")
            
            if submitted:
                try:
                    response_data = {
                        'age': age,
                        'gender': gender,
                        'academic_year': academic_year,
                        'living_situation': living_situation,
                        'employment_status': employment_status,
                        'professional_help': professional_help,
                        'access_counseling': access_counseling,
                        'support_network': support_network,
                        'campus_resources': campus_resources,
                        'barriers_help': barriers_help,
                        'access_financial_aid': access_financial_aid,
                        'receiving_scholarships': receiving_scholarships,
                        'food_insecurity': food_insecurity,
                        'financial_stress': financial_stress,
                        'impact_academic': impact_academic,
                        'experienced_dishonesty': experienced_dishonesty,
                        'type_of_dishonesty': type_of_dishonesty,
                        'academic_integrity_pressure': academic_integrity_pressure,
                        'study_hours_integrity': study_hours_integrity,
                        'workload_stress_integrity': workload_stress_integrity,
                        'submitted_at': datetime.utcnow().isoformat()
                    }
                    
                    db.store_response(response_data, session_id)
                    st.success("✨ Thank you for completing the survey!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error submitting survey: {str(e)}")
                    
        st.markdown("</div>", unsafe_allow_html=True)

def generate_survey_link():
    """Generate a new survey session link"""
    session_manager = SessionManager(SESSION_DURATION_MINUTES, 'academic_integrity')
    link, expiry_time = session_manager.generate_session_link()
    
    st.markdown(
        f"""
        <div class="survey-section">
            <h3>🔗 Survey Session Link</h3>
            <p>Access your personalized diversity & equality survey by clicking the button below.</p>
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
    """Display synthetic data and provide download option"""
    if synthetic_datasets:
        st.markdown("### 📊 Synthetic Data Generated")
        
        for i, dataset in enumerate(synthetic_datasets, 1):
            st.markdown(f"#### Synthetic Dataset {i}")
            
            # Create tabs for different views
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
                
                # Academic metrics
                st.subheader("Academic Performance Metrics")
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'gpa' in dataset['data'].columns:
                        avg_gpa = dataset['data']['gpa'].mean()
                        st.metric("Average GPA", f"{avg_gpa:.2f}")
                        st.bar_chart(dataset['data']['gpa'].value_counts(bins=10))
                
                with col2:
                    if 'pressure_level' in dataset['data'].columns:
                        avg_pressure = dataset['data']['pressure_level'].mean()
                        st.metric("Average Pressure Level", f"{avg_pressure:.2f}/5")
                        st.bar_chart(dataset['data']['pressure_level'].value_counts())
                
                # Integrity metrics
                st.subheader("Academic Integrity Metrics")
                metrics_cols = st.columns(3)
                
                if 'cheating_awareness' in dataset['data'].columns:
                    with metrics_cols[0]:
                        avg_awareness = dataset['data']['cheating_awareness'].mean()
                        st.metric("Perceived Prevalence", f"{avg_awareness:.2f}/5")
                
                if 'reporting_comfort' in dataset['data'].columns:
                    with metrics_cols[1]:
                        avg_comfort = dataset['data']['reporting_comfort'].mean()
                        st.metric("Reporting Comfort", f"{avg_comfort:.2f}/5")
                
                if 'policy_effectiveness' in dataset['data'].columns:
                    with metrics_cols[2]:
                        avg_effectiveness = dataset['data']['policy_effectiveness'].mean()
                        st.metric("Policy Effectiveness", f"{avg_effectiveness:.2f}/5")
            
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

    st.markdown("<div class='title'>Academic Integrity Survey</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Help us understand and improve academic integrity in our community</div>",
        unsafe_allow_html=True
    )
    
    try:
        db = Database('academic_integrity')  # Initialize with survey type
        
        session_id = st.query_params.get("session", None)
        
        if session_id:
            # Respondent view
            session_manager = SessionManager(SESSION_DURATION_MINUTES, 'academic_integrity')
            if session_manager.validate_session(session_id):
                display_survey_form(db, session_id)
            else:
                st.error("This survey session has expired.")
                # Check for and display any synthetic data generated
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
                # Check for expired sessions and display synthetic data
                synthetic_datasets = db.cleanup_expired_sessions()
                if synthetic_datasets:
                    display_synthetic_data(synthetic_datasets)
                else:
                    st.info("No synthetic data available yet. It will appear here when sessions expire.")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()