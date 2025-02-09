from datetime import datetime, timedelta
import secrets
import streamlit as st
from utils.database import Database
from utils.config import get_survey_config

class SessionManager:
    def __init__(self, session_duration, survey_type='mental_health'):
        self.session_duration = session_duration
        self.survey_type = survey_type
        self.config = get_survey_config(survey_type)
        self.db = Database(survey_type)
    
    def generate_session_link(self):
        """Generate a unique session link valid for the configured duration"""
        session_id = secrets.token_urlsafe(16)
        expiry_time = datetime.utcnow() + timedelta(minutes=self.session_duration)
        
        # Store session information
        session_data = {
            'session_id': session_id,
            'created_at': datetime.utcnow(),
            'expires_at': expiry_time,
            'is_active': True,
            'survey_type': self.survey_type
        }
        
        self.db.sessions.insert_one(session_data)
        
        # Generate the complete link using BASE_URL from config
        link = f"{self.config['BASE_URL']}?session={session_id}"
        
        return link, expiry_time

    def validate_session(self, session_id):
        """Check if a session is still valid"""
        if not session_id:
            return False
            
        session = self.db.sessions.find_one({
            'session_id': session_id,
            'expires_at': {'$gt': datetime.utcnow()},
            'is_active': True,
            'survey_type': self.survey_type
        })
        
        return bool(session)
    
    def get_session_expiry(self, session_id):
        """Get session expiry time"""
        session = self.db.sessions.find_one({
            'session_id': session_id,
            'survey_type': self.survey_type
        })
        return session['expires_at'] if session else None
    
    def validate_session(self, session_id):
        """Check if a session is still valid"""
        if not session_id:
            return False
            
        session = self.db.sessions.find_one({
            'session_id': session_id,
            'expires_at': {'$gt': datetime.utcnow()},
            'is_active': True
        })
        
        return bool(session)
    
    def get_session_expiry(self, session_id):
        """Get session expiry time"""
        session = self.db.sessions.find_one({'session_id': session_id})
        return session['expires_at'] if session else None