from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_OPTIONS = {
    'serverSelectionTimeoutMS': 5000,
    'connectTimeoutMS': 10000,
    'retryWrites': True,
    'w': 'majority'
}

# Function to get configuration based on the survey type
def get_survey_config(survey_type):
    if survey_type == 'mental_health':
        database_name = 'mental_health_survey_db'
        base_url = os.getenv('MENTAL_HEALTH_BASE_URL', 'http://localhost:8501/mental_health')
    elif survey_type == 'sexual_health':
        database_name = 'sexual_health_survey_db'
        base_url = os.getenv('SEXUAL_HEALTH_BASE_URL', 'http://localhost:8501/sexual_health')
    elif survey_type == 'diversity_equality':
        database_name = 'diversity_equality_survey_db'
        base_url = os.getenv('DIVERSITY_EQUALITY_BASE_URL', 'http://localhost:8501/diversity_equality')
    elif survey_type == 'academic_integrity':
        database_name = 'academic_integrity_survey_db'
        base_url = os.getenv('ACADEMIC_INTEGRITY_BASE_URL', 'http://localhost:8501/academic_integrity')
    elif survey_type == 'socioeconomic_status':
        database_name = 'socio_economic_survey_db'
        base_url = os.getenv('SOCIOECONOMIC_STATUS_BASE_URL', 'http://localhost:8501/socioeconomic_status')
    elif survey_type == 'substance_use':
        database_name = 'substance_use_survey_db'
        base_url = os.getenv('SUBSTANCE_USE_BASE_URL', 'http://localhost:8501/substance_use')
    else:
        raise ValueError('Invalid survey type')

    collection_name = 'responses'
    encryption_key = os.getenv('ENCRYPTION_KEY', 'default_encryption_key_12345'.ljust(32, '0'))

    config = {
        'DATABASE_NAME': database_name,
        'COLLECTION_NAME': collection_name,
        'ENCRYPTION_KEY': encryption_key,
        'BASE_URL': base_url,
        'SESSION_DURATION_MINUTES': 10
    }
    
    return config