from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime, timedelta
from utils.encryption import Encryptor
from utils.config import MONGO_URI, MONGO_OPTIONS, get_survey_config
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class Database:
    def __init__(self, survey_type='mental_health'):
        try:
            config = get_survey_config(survey_type)
            self.client = MongoClient(MONGO_URI, **MONGO_OPTIONS)
            self.client.admin.command('ping')
            
            self.db = self.client[config['DATABASE_NAME']]
            self.collection = self.db[config['COLLECTION_NAME']]
            self.sessions = self.db['survey_sessions']
            self.encryptor = Encryptor(config['ENCRYPTION_KEY'])
            
            # Create indices
            self.collection.create_index([("session_id", ASCENDING)])
            self.collection.create_index([("expires_at", ASCENDING)])
            self.sessions.create_index([("expires_at", ASCENDING)])
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            st.error("MongoDB Connection Error. Please check your connection.")
            raise Exception(f"MongoDB Connection Error: {str(e)}")
        
    def get_significant_correlations(self, df, threshold=0.3):
        """Extracts significant correlations where |correlation| > threshold"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numerical_cols].corr()
        
        significant_correlations = {}
        for i in range(len(numerical_cols)):
            for j in range(i+1, len(numerical_cols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > threshold:
                    pair = f"{numerical_cols[i]} and {numerical_cols[j]}"
                    significant_correlations[pair] = round(corr, 2)
        
        return significant_correlations

    def enforce_value_bounds(self, synthetic_df, original_df):
        """Ensures values stay within min-max range of the original dataset."""
        numerical_cols = original_df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            min_val = original_df[col].min()
            max_val = original_df[col].max()
            synthetic_df[col] = synthetic_df[col].clip(lower=min_val, upper=max_val)
        return synthetic_df

    def generate_base_synthetic_data(self, original_df, num_samples=100):
        """Generates initial synthetic dataset with more robust distribution matching"""
        numerical_cols = original_df.select_dtypes(include=[np.number]).columns
        synthetic_data = {}
        
        for col in numerical_cols:
            data = original_df[col].values
            
            # Check for constant values
            if len(np.unique(data)) <= 1:
                # If column has constant values, just repeat them
                synthetic_data[col] = np.repeat(data[0], num_samples)
                continue
                
            try:
                # Try KDE first
                kde = pd.Series(data).plot.kde()
                x_range = np.linspace(data.min(), data.max(), 1000)
                y_range = kde.get_lines()[0].get_ydata()
                
                # Generate samples using inverse transform sampling
                samples = np.random.choice(x_range, size=num_samples, p=y_range/y_range.sum())
                synthetic_data[col] = samples
                
            except (np.linalg.LinAlgError, ValueError) as e:
                # Fallback to basic sampling if KDE fails
                mean = np.mean(data)
                std = np.std(data)
                if std == 0:  # Handle zero standard deviation
                    synthetic_data[col] = np.repeat(mean, num_samples)
                else:
                    # Generate samples using normal distribution with same mean and std
                    samples = np.random.normal(mean, std, num_samples)
                    # Clip to original range
                    samples = np.clip(samples, data.min(), data.max())
                    synthetic_data[col] = samples
        
        return pd.DataFrame(synthetic_data)
    
    def iterative_correlation_adjustment(self, synthetic_df, original_correlations, max_iterations=200):
        """Iteratively adjusts correlations with dynamic step size"""
        numerical_cols = synthetic_df.columns
        synthetic_df = synthetic_df.copy()
        scaler = StandardScaler()
        
        best_df = synthetic_df.copy()
        best_score = float('inf')
        
        for iteration in range(max_iterations):
            step_size = 1.0 / (1 + iteration * 0.1)
            total_adjustment = 0
            
            for pair, target_corr in original_correlations.items():
                col1, col2 = pair.split(" and ")
                current_corr = synthetic_df[col1].corr(synthetic_df[col2])
                
                error = target_corr - current_corr
                
                if abs(error) > 0.01:
                    data1 = scaler.fit_transform(synthetic_df[[col1]])
                    data2 = scaler.fit_transform(synthetic_df[[col2]])
                    
                    adjustment = error * step_size
                    new_data2 = data2 + adjustment * data1
                    synthetic_df[col2] = scaler.inverse_transform(new_data2)
                    
                    total_adjustment += abs(adjustment)
            
            for i in range(len(numerical_cols)):
                for j in range(i+1, len(numerical_cols)):
                    col1, col2 = numerical_cols[i], numerical_cols[j]
                    pair = f"{col1} and {col2}"
                    reverse_pair = f"{col2} and {col1}"
                    
                    if pair not in original_correlations and reverse_pair not in original_correlations:
                        current_corr = synthetic_df[col1].corr(synthetic_df[col2])
                        if abs(current_corr) > 0.2:
                            noise = np.random.normal(0, 0.1, len(synthetic_df))
                            synthetic_df[col2] = synthetic_df[col2] + noise * synthetic_df[col2].std() * step_size
            
            score = 0
            for pair, target_corr in original_correlations.items():
                col1, col2 = pair.split(" and ")
                current_corr = synthetic_df[col1].corr(synthetic_df[col2])
                score += abs(target_corr - current_corr)
            
            if score < best_score:
                best_score = score
                best_df = synthetic_df.copy()
            
            if total_adjustment < 0.001:
                break
        
        return best_df

    def generate_synthetic_data_from_session(self, session_id):
        """Generate synthetic data from a session before deletion"""
        try:
            # Get all responses for the session
            responses = self.collection.find({'session_id': session_id})
            
            # Decrypt and compile responses into a DataFrame
            decrypted_data = []
            for response in responses:
                data = self.encryptor.decrypt_data(response['data'])
                decrypted_data.append(data)
            
            if not decrypted_data:
                return None
                
            original_df = pd.DataFrame(decrypted_data)
            
            # Process numerical columns, excluding certain fields
            exclude_columns = ['created_at', 'expires_at', '_id']
            numerical_df = original_df.select_dtypes(include=[np.number]).drop(
                columns=[col for col in exclude_columns if col in original_df.columns]
            )
            
            if numerical_df.empty:
                return None
                
            # Generate synthetic data only if we have enough samples
            if len(numerical_df) < 2:
                st.warning("Not enough responses to generate meaningful synthetic data")
                return None
                
            # Get original correlations
            original_correlations = self.get_significant_correlations(numerical_df)
            
            # Generate synthetic data
            synthetic_df = self.generate_base_synthetic_data(numerical_df)
            
            # Adjust correlations
            final_synthetic_df = self.iterative_correlation_adjustment(synthetic_df, original_correlations)
            
            # Ensure values are within bounds
            final_synthetic_df = self.enforce_value_bounds(final_synthetic_df, numerical_df)
            
            # Save synthetic data as CSV
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"synthetic_data_{session_id}_{timestamp}.csv"
            final_synthetic_df.to_csv(filename, index=False)
            
            # Return both the DataFrame and metadata for display
            return {
                'data': final_synthetic_df,
                'filename': filename,
                'original_correlations': original_correlations,
                'synthetic_correlations': self.get_significant_correlations(final_synthetic_df)
            }
            
        except Exception as e:
            st.warning(f"Error generating synthetic data: {str(e)}")
            return None
    def cleanup_expired_sessions(self):
        """Remove expired sessions and their responses after generating synthetic data"""
        try:
            current_time = datetime.utcnow()
            
            # Find expired sessions
            expired_sessions = self.sessions.find({
                'expires_at': {'$lte': current_time}
            })
            
            synthetic_datasets = []
            
            for session in expired_sessions:
                # Generate synthetic data before deletion
                synthetic_data = self.generate_synthetic_data_from_session(session['session_id'])
                if synthetic_data:
                    synthetic_datasets.append(synthetic_data)
                
                # Delete responses for this session
                self.collection.delete_many({
                    'session_id': session['session_id']
                })
            
            # Delete expired sessions
            self.sessions.delete_many({
                'expires_at': {'$lte': current_time}
            })
            
            return synthetic_datasets
            
        except Exception as e:
            st.warning(f"Error during cleanup: {str(e)}")
            return []

    def store_response(self, response_data, session_id):
        """Store encrypted response with session ID"""
        try:
            session = self.sessions.find_one({'session_id': session_id})
            if not session:
                raise Exception("Invalid session")
                
            encrypted_data = self.encryptor.encrypt_data(response_data)
            
            document = {
                'data': encrypted_data,
                'session_id': session_id,
                'created_at': datetime.utcnow(),
                'expires_at': session['expires_at']
            }
            
            result = self.collection.insert_one(document)
            return result
            
        except Exception as e:
            st.error(f"Error storing data: {str(e)}")
            raise

    def get_session_responses(self, session_id):
        """Get all responses for a session"""
        try:
            responses = self.collection.find({
                'session_id': session_id,
                'expires_at': {'$gt': datetime.utcnow()}
            })
            return list(responses)
        except Exception as e:
            st.error(f"Error retrieving responses: {str(e)}")
            return []

    def get_response_stats(self):
        """Get basic statistics about responses"""
        try:
            current_time = datetime.utcnow()
            total_responses = self.collection.count_documents({
                'expires_at': {'$gt': current_time}
            })
            
            return {
                'total_responses': total_responses,
                'last_updated': current_time
            }
        except Exception as e:
            st.error(f"Error getting stats: {str(e)}")
            return {'total_responses': 0, 'last_updated': current_time}

    def __del__(self):
        try:
            self.client.close()
        except:
            pass