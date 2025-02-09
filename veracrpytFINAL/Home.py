import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openai import OpenAI
import numpy as np
from datetime import datetime
from utils.database import Database
from pathlib import Path
import os

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set page configuration
st.set_page_config(
    page_title="Data Analysis Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session states
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Theme toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Theme colors (same as existing)
THEME_COLORS = {
    'light': {
        'bg': '#f7f4ed',
        'text': '#2c2c2c',
        'card_bg': '#ffffff',
        'card_shadow': '0 4px 6px rgba(0,0,0,0.1)',
        'gradient': 'linear-gradient(120deg, #8fa3bf, #6d7f99)',
        'subtitle': '#6d7f99',
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

    .title {{
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: black;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    .subtitle {{
        font-size: 1.4rem;
        color: {theme_colors['subtitle']};
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .card {{
        background: {theme_colors['card_bg']};
        padding: 2rem;
        border-radius: 10px;
        box-shadow: {theme_colors['card_shadow']};
        border: 1px solid {theme_colors['card_border']};
        margin-bottom: 1.5rem;
        transition: transform 0.2s;
    }}
    
    .card:hover {{
        transform: translateY(-5px);
        box-shadow: {theme_colors['hover_shadow']};
    }}
    
    .nav-button {{
        display: inline-block;
        padding: 0.8rem 1.5rem;
        background: {theme_colors['gradient']};
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-weight: 600;
        margin: 0.5rem;
        text-align: center;
    }}
    
    .nav-button:hover {{
        opacity: 0.9;
    }}
    </style>
    """

def analyze_with_chatgpt(synthetic_data_description):
    """Send synthetic data analysis request to ChatGPT"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data analysis expert. Analyze the following synthetic dataset and provide insights."},
                {"role": "user", "content": f"Analyze this synthetic dataset: {synthetic_data_description}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in ChatGPT analysis: {str(e)}")
        return None

def main():
    # Apply theme CSS
    st.markdown(get_css(THEME_COLORS[st.session_state.theme]), unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("logo.png")
        if st.button("🌓 Toggle Theme"):
            toggle_theme()
            st.rerun()
    
    # Main content
    st.markdown("<h1 class='title'>Veracrypt</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:black;' class='subtitle'>Upload data sets for secure analysis or explore our survey tools</p>", unsafe_allow_html=True)

    # Two-column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📊 Data Analysis")
        uploaded_file = st.file_uploader("Upload your CSV file for analysis", type=['csv'])
        
        if uploaded_file:
            # Reset analysis state when new file is uploaded
            st.session_state.analysis_complete = False
            st.session_state.analysis_result = None
            try:
                # Read the CSV
                df = pd.read_csv(uploaded_file)
                
                # Initialize Database instance for synthetic data generation
                db = Database()
                
                # Generate synthetic data and immediately store it
                synthetic_data = db.generate_base_synthetic_data(df)
                
                # Show a one-time preview of original data with warning
                st.markdown("---")
                st.warning("⚠️ Original Data Preview - Will be deleted after synthetic generation")
                st.dataframe(df.head())
                
                # Clear original dataframe from memory
                original_shape = df.shape
                original_columns = list(df.columns)
                df = None
                
                # Show synthetic data and confirmation
                st.markdown("---")
                st.success("✅ Original data has been cleared from memory for privacy")
                st.markdown("### 🔒 Synthetic Data")
                st.info("All analysis will be performed on this privacy-preserving synthetic dataset")
                st.dataframe(synthetic_data.head())
                
                # Interactive Visualizations
                st.markdown("---")
                st.markdown("## 📊 Interactive Data Visualizations")
                st.info("All visualizations are based on synthetic data only")
                
                # Create tabs for different visualization types
                viz_tabs = st.tabs(["📈 Distribution Analysis", "🔄 Correlation Analysis", "📊 Comparative Analysis", "🎯 Custom Analysis"])
                
                with viz_tabs[0]:
                    st.write("### Distribution Analysis")
                    
                    # Column selector for distribution analysis
                    numeric_cols = synthetic_data.select_dtypes(include=['float64', 'int64']).columns
                    selected_col = st.selectbox(
                        "Select column for distribution analysis",
                        numeric_cols,
                        key="dist_col"
                    )
                    
                    # Create distribution plot
                    fig_dist = go.Figure()
                    fig_dist.add_trace(go.Histogram(
                        x=synthetic_data[selected_col],
                        name='Synthetic Data',
                        opacity=0.7,
                        nbinsx=30
                    ))
                    fig_dist.update_layout(
                        title=f"Distribution of {selected_col} (Synthetic Data)",
                        xaxis_title=selected_col,
                        yaxis_title="Count",
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)
                    
                    # Box plot
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(
                        y=synthetic_data[selected_col],
                        name='Synthetic Data',
                        boxpoints='outliers'
                    ))
                    fig_box.update_layout(
                        title=f"Box Plot of {selected_col} (Synthetic Data)",
                        yaxis_title=selected_col,
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                    
                    # Display summary statistics
                    st.write("### 📊 Summary Statistics (Synthetic Data)")
                    stats_synth = synthetic_data[selected_col].describe()
                    st.dataframe(stats_synth, use_container_width=True)
                
                with viz_tabs[1]:
                    st.write("### Correlation Analysis (Synthetic Data)")
                    
                    # Create correlation matrix
                    corr_synth = synthetic_data.select_dtypes(include=['float64', 'int64']).corr()
                    
                    fig_corr = px.imshow(
                        corr_synth,
                        title="Correlation Matrix (Synthetic Data)",
                        color_continuous_scale='RdBu_r',
                        aspect='auto'
                    )
                    fig_corr.update_layout(
                        template='plotly_white',
                        height=500
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
                
                with viz_tabs[2]:
                    st.write("### Comparative Analysis")
                    
                    # Select columns for scatter plot
                    col_x = st.selectbox("Select X-axis column", numeric_cols, key="scatter_x")
                    col_y = st.selectbox("Select Y-axis column", numeric_cols, key="scatter_y")
                    
                    # Create scatter plot with only synthetic data
                    fig_scatter = go.Figure()
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=synthetic_data[col_x],
                        y=synthetic_data[col_y],
                        mode='markers',
                        name='Synthetic Data',
                        marker=dict(size=8, opacity=0.6)
                    ))
                    
                    fig_scatter.update_layout(
                        title=f"Scatter Plot: {col_x} vs {col_y}",
                        xaxis_title=col_x,
                        yaxis_title=col_y,
                        template='plotly_white',
                        height=600
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
                    # Add trend line option
                    if st.checkbox("Show Trend Line"):
                        fig_trend = go.Figure()
                        
                        # Synthetic data with trend line
                        z_synth = np.polyfit(synthetic_data[col_x], synthetic_data[col_y], 1)
                        p_synth = np.poly1d(z_synth)
                        
                        fig_trend.add_trace(go.Scatter(
                            x=synthetic_data[col_x],
                            y=synthetic_data[col_y],
                            mode='markers',
                            name='Synthetic Data',
                            marker=dict(size=8, opacity=0.6)
                        ))
                        
                        fig_trend.add_trace(go.Scatter(
                            x=synthetic_data[col_x],
                            y=p_synth(synthetic_data[col_x]),
                            name='Trend Line',
                            line=dict(color='blue', dash='dash')
                        ))
                        
                        fig_trend.update_layout(
                            title=f"Scatter Plot with Trend Line: {col_x} vs {col_y}",
                            xaxis_title=col_x,
                            yaxis_title=col_y,
                            template='plotly_white',
                            height=600
                        )
                        
                        st.plotly_chart(fig_trend, use_container_width=True)
                
                with viz_tabs[3]:
                    st.write("### Custom Analysis")
                    
                    # Multi-select columns for custom analysis
                    selected_cols = st.multiselect(
                        "Select columns for custom analysis",
                        numeric_cols,
                        default=list(numeric_cols)[:3] if len(numeric_cols) >= 3 else list(numeric_cols)
                    )
                    
                    if selected_cols:
                        # Choose plot type
                        plot_type = st.selectbox(
                            "Select plot type",
                            ["Line Plot", "Bar Plot", "Area Plot", "Violin Plot"]
                        )
                        
                        if plot_type == "Line Plot":
                            fig_custom = go.Figure()
                            for col in selected_cols:
                                fig_custom.add_trace(go.Scatter(
                                    y=synthetic_data[col],
                                    name=f'{col}',
                                    mode='lines'
                                ))
                        
                        elif plot_type == "Bar Plot":
                            fig_custom = go.Figure()
                            for col in selected_cols:
                                fig_custom.add_trace(go.Bar(
                                    name=f'{col}',
                                    y=synthetic_data[col],
                                    x=synthetic_data.index
                                ))
                        
                        elif plot_type == "Area Plot":
                            fig_custom = go.Figure()
                            for col in selected_cols:
                                fig_custom.add_trace(go.Scatter(
                                    y=synthetic_data[col],
                                    name=f'{col}',
                                    fill='tonexty'
                                ))
                        
                        elif plot_type == "Violin Plot":
                            fig_custom = go.Figure()
                            for col in selected_cols:
                                fig_custom.add_trace(go.Violin(
                                    y=synthetic_data[col],
                                    name=f'{col}',
                                    side='positive'
                                ))
                        
                        fig_custom.update_layout(
                            title=f"Custom {plot_type} (Synthetic Data)",
                            template='plotly_white',
                            height=600
                        )
                        st.plotly_chart(fig_custom, use_container_width=True)
                
                # Prepare analysis description for GPT using only synthetic data
                analysis_description = f"""
                Synthetic Dataset Summary:
                - Shape: {synthetic_data.shape}
                - Number of features: {len(synthetic_data.columns)}
                - Numerical columns: {', '.join(synthetic_data.select_dtypes(include=['number']).columns)}
                
                Basic Statistics:
                {synthetic_data.describe().to_string()}
                
                Key Correlations:
                {db.get_significant_correlations(synthetic_data)}
                """
                
                # Get ChatGPT analysis only if not already completed
                if not st.session_state.analysis_complete:
                    with st.spinner("Analyzing data with AI..."):
                        st.session_state.analysis_result = analyze_with_chatgpt(analysis_description)
                        st.session_state.analysis_complete = True
                
                # Display analysis if available
                if st.session_state.analysis_result:
                    st.write("### AI Analysis Insights")
                    st.write(st.session_state.analysis_result)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("🔍 Survey Tools")
        st.write("Access our comprehensive suite of anonymous survey tools")
        
        # Navigation link to the survey dashboard
        st.markdown(
            '<a href="/Home" target="_self" style="text-decoration: none;">'
            '<div class="nav-button">Go to Survey Dashboard</div></a>', 
            unsafe_allow_html=True
        )
        
        st.write("""
        ### Available Survey Categories:
        - Mental Health & Well-being
        - Academic Integrity
        - Socioeconomic Status
        - Diversity & Equality
        - Sexual Health
        - Substance Use
        """)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()