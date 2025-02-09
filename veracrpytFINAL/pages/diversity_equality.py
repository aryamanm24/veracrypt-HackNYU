import streamlit as st
import sys
from pathlib import Path
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta
from utils.database import Database
from utils.config import get_survey_config
from utils.session_manager import SessionManager
import pandas as pd

# Get survey-specific configuration
config = get_survey_config('diversity_equality')
SESSION_DURATION_MINUTES = config['SESSION_DURATION_MINUTES']

# Initialize session state for theme if it doesn't exist
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Set page configuration
st.set_page_config(
    page_title="Diversity & Equality - VeraCrypt",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Define theme colors (same as your existing theme colors)
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
        'card_border': 'rgba(44, 62, 80, 0.1)',
        'success': '#2ecc71',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'info': '#3498db'
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
        'card_border': '#404040',
        'success': '#27ae60',
        'warning': '#f1c40f',
        'error': '#c0392b',
        'info': '#2980b9'
    }
}

# Apply the same CSS styling (your existing get_css function)
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
    
    .form-container {{
        background: {theme_colors['card_bg']};
        padding: 2rem;
        border-radius: 10px;
        box-shadow: {theme_colors['card_shadow']};
        border: 1px solid {theme_colors['card_border']};
        margin-bottom: 1.5rem;
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
    """Display the diversity and equality survey form and handle submissions."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        
        with st.form("diversity_equality_survey", clear_on_submit=True):
            # Demographics
            st.subheader("Demographics")
            age = st.number_input("Age:", min_value=16, max_value=100, step=1)
            gender = st.selectbox("Gender:", ["Male", "Female", "Non-binary", "Other", "Prefer not to say"])
            academic_year = st.selectbox("Academic Year:", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
            living_situation = st.selectbox("Living Situation:", ["On-campus", "Off-campus"])
            employment_status = st.selectbox("Employment Status:", ["Unemployed", "Part-time", "Full-time"])
            
            # Academic & Mental Health Factors
            academic_dishonesty = st.selectbox("Experiences with academic dishonesty:", ["None", "Minor", "Severe"])
            perceived_pressure = st.slider("Perceived pressure to perform well (1-5):", 1, 5, 3)
            workload_stress = st.slider("Workload stress (1-5):", 1, 5, 3)
            depression_score = st.number_input("Depression score (PHQ-9 items):", min_value=0, max_value=27, step=1)
            anxiety_score = st.number_input("Anxiety score (GAD-7 items):", min_value=0, max_value=21, step=1)
            
            # Lifestyle Factors
            study_hours = st.number_input("Study Hours per Week:", min_value=0, max_value=100, step=1)
            academic_pressure = st.slider("Academic pressure (1-5):", 1, 5, 3)
            exercise_frequency = st.selectbox("Exercise Frequency:", ["Never", "Rarely", "Regularly"])
            meditation = st.selectbox("Meditation/Mindfulness Practice:", ["Never", "Occasionally", "Regularly"])
            social_activities = st.selectbox("Social Activities Level:", ["Low", "Moderate", "High"])
            
            # Mental Health Support & Resources
            professional_help = st.selectbox("Professional Help Utilization:", ["Never", "Occasionally", "Regularly"])
            access_counseling = st.selectbox("Access to Counseling:", ["Yes", "No", "Unsure"])
            support_network = st.slider("Support Network Rating (1-10):", 1, 10, 5)
            campus_resources = st.selectbox("Knowledge of Campus Resources:", ["Poor", "Moderate", "Good", "Excellent"])
            barriers_help = st.selectbox("Barriers to Seeking Help:", ["None", "Cost", "Availability", "Other"])
            
            # Sexual Health Factors
            sexually_active = st.selectbox("Are you sexually active?", ["Yes", "No"])
            contraception_use = st.selectbox("Contraception Use:", ["Always", "Sometimes", "Never", "Not Applicable"])
            sti_awareness = st.slider("STI Awareness Level (1-10):", 1, 10, 5)
            experienced_harassment = st.selectbox("Have you experienced harassment?", ["Yes", "No"])
            experienced_assault = st.selectbox("Have you experienced assault?", ["Yes", "No"])
            consent_education = st.slider("Consent Education Level (1-10):", 1, 10, 5)
            support_resources_knowledge = st.slider("Support Resources Knowledge (1-10):", 1, 10, 5)
            
            # Financial Hardship Factors
            access_financial_aid = st.selectbox("Do you have access to financial aid?", ["Yes", "No"])
            receiving_scholarships = st.selectbox("Are you receiving scholarships?", ["Yes", "No"])
            food_insecurity = st.selectbox("How often do you experience food insecurity?", ["Never", "Sometimes", "Often"])
            housing_instability = st.selectbox("Housing Stability:", ["Stable", "Unstable"])
            financial_stress = st.slider("Financial Stress Level (1-10):", 1, 10, 5)
            impact_academic = st.slider("Impact of Financial Hardship on Academic Success (1-10):", 1, 10, 5)
            
            # DEI Factors
            experienced_discrimination = st.selectbox("Have you experienced discrimination?", ["Yes", "No"])
            type_of_discrimination = st.selectbox("Type of Discrimination:", ["None", "Gender-based", "LGBTQ+", "Disability-related", "Other"])
            microaggressions_faced = st.selectbox("How often have you faced microaggressions?", ["Never", "Rarely", "Sometimes", "Often"])
            campus_climate = st.slider("Campus Climate Rating (1-10):", 1, 10, 5)
            sense_of_belonging = st.slider("Sense of Belonging (1-10):", 1, 10, 5)

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
                        'academic_dishonesty': academic_dishonesty,
                        'perceived_pressure': perceived_pressure,
                        'workload_stress': workload_stress,
                        'depression_score': depression_score,
                        'anxiety_score': anxiety_score,
                        'study_hours': study_hours,
                        'academic_pressure': academic_pressure,
                        'exercise_frequency': exercise_frequency,
                        'meditation': meditation,
                        'social_activities': social_activities,
                        'professional_help': professional_help,
                        'access_counseling': access_counseling,
                        'support_network': support_network,
                        'campus_resources': campus_resources,
                        'barriers_help': barriers_help,
                        'sexually_active': sexually_active,
                        'contraception_use': contraception_use,
                        'sti_awareness': sti_awareness,
                        'experienced_harassment': experienced_harassment,
                        'experienced_assault': experienced_assault,
                        'consent_education': consent_education,
                        'support_resources_knowledge': support_resources_knowledge,
                        'access_financial_aid': access_financial_aid,
                        'receiving_scholarships': receiving_scholarships,
                        'food_insecurity': food_insecurity,
                        'housing_instability': housing_instability,
                        'financial_stress': financial_stress,
                        'impact_academic': impact_academic,
                        'experienced_discrimination': experienced_discrimination,
                        'type_of_discrimination': type_of_discrimination,
                        'microaggressions_faced': microaggressions_faced,
                        'campus_climate': campus_climate,
                        'sense_of_belonging': sense_of_belonging,
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
    session_manager = SessionManager(SESSION_DURATION_MINUTES, 'diversity_equality')
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
    
    # Add copy button
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
                # Display the synthetic data preview
                st.markdown("**Preview of Synthetic Data**")
                st.dataframe(dataset['data'].head())
                
                # Provide download button
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
                
                # Demographics breakdown
                st.subheader("Demographics Distribution")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gender distribution
                    if 'gender' in dataset['data'].columns:
                        gender_counts = dataset['data']['gender'].value_counts()
                        st.bar_chart(gender_counts)
                        st.markdown("**Gender Distribution**")
                
                with col2:
                    # Ethnicity distribution
                    if 'ethnicity' in dataset['data'].columns:
                        ethnicity_counts = dataset['data']['ethnicity'].value_counts()
                        st.bar_chart(ethnicity_counts)
                        st.markdown("**Ethnicity Distribution**")
                
                # Inclusion metrics
                st.subheader("Inclusion Metrics")
                metrics_cols = st.columns(3)
                
                if 'inclusion_rating' in dataset['data'].columns:
                    with metrics_cols[0]:
                        avg_inclusion = dataset['data']['inclusion_rating'].mean()
                        st.metric("Average Inclusion Rating", f"{avg_inclusion:.2f}/5")
                
                if 'support_rating' in dataset['data'].columns:
                    with metrics_cols[1]:
                        avg_support = dataset['data']['support_rating'].mean()
                        st.metric("Average DEI Support Rating", f"{avg_support:.2f}/5")
                
                if 'program_effectiveness' in dataset['data'].columns:
                    with metrics_cols[2]:
                        avg_effectiveness = dataset['data']['program_effectiveness'].mean()
                        st.metric("Program Effectiveness", f"{avg_effectiveness:.2f}/5")
            
            with corr_tab:
                st.markdown("**📊 Correlation Analysis**")
                
                # Calculate correlations for numeric columns
                numeric_cols = dataset['data'].select_dtypes(include=['float64', 'int64']).columns
                if not numeric_cols.empty:
                    corr_matrix = dataset['data'][numeric_cols].corr()
                    st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlBu'))
                    
                    # Display notable correlations
                    st.markdown("**Notable Correlations:**")
                    for col1 in numeric_cols:
                        for col2 in numeric_cols:
                            if col1 < col2:  # Avoid duplicate pairs
                                corr = corr_matrix.loc[col1, col2]
                                if abs(corr) > 0.5:  # Show strong correlations
                                    st.write(f"- {col1} vs {col2}: {corr:.2f}")
                else:
                    st.info("No numerical data available for correlation analysis.")
            
            st.markdown("---")
    else:
        st.info("No synthetic data available yet. It will appear here when sessions expire.")

def main():
    if st.button("← Back to Dashboard"):
        st.switch_page("/survey_dashboard.py")

    st.markdown("<div class='title'>Diversity & Equality Survey</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Help us create a more inclusive and equitable environment</div>",
        unsafe_allow_html=True
    )
    
    try:
        db = Database('diversity_equality')
        
        session_id = st.query_params.get("session", None)
        
        if session_id:
            # Respondent view
            session_manager = SessionManager(SESSION_DURATION_MINUTES, 'diversity_equality')
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