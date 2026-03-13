import streamlit as st
import requests
import json
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Resume Analyzer RAG",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [role="tab"] {
        font-size: 1.1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    api_url = st.text_input("API Base URL", value=API_BASE_URL)
    st.markdown("---")
    
    # Health check
    try:
        response = requests.get(f"{api_url}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            st.success("✅ API Connected")
            health_data = response.json()
            st.json(health_data)
        else:
            st.error(f"❌ API Error: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Cannot connect to API: {str(e)}")
        st.info("Make sure the API server is running on http://localhost:8000")
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    try:
        response = requests.get(f"{api_url}/stats", timeout=TIMEOUT)
        if response.status_code == 200:
            stats = response.json()
            st.metric("Documents", stats.get("total_documents", 0))
            st.metric("Status", stats.get("status", "unknown"))
    except Exception as e:
        st.warning(f"Could not load stats: {str(e)}")

# Main content
st.title("📄 Resume Analyzer RAG")
st.markdown("AI-powered resume search and analysis system")

# Create tabs
tab1, tab2 = st.tabs(["📤 Upload Resumes", "🔍 Search"])

# Tab 1: Upload Resumes
with tab1:
    st.subheader("Upload Resume PDFs")
    st.markdown("Upload one or multiple PDF resumes to index them in the system.")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        key="resume_uploader"
    )
    
    if uploaded_files:
        st.info(f"Selected {len(uploaded_files)} file(s) for upload")
        
        if st.button("📤 Upload Files", key="upload_button"):
            progress_bar = st.progress(0)
            status_container = st.container()
            
            success_count = 0
            error_count = 0
            
            for idx, file in enumerate(uploaded_files):
                try:
                    with status_container:
                        st.info(f"Uploading: {file.name}")
                    
                    # Upload file to API
                    files = {"file": (file.name, file.getbuffer(), "application/pdf")}
                    response = requests.post(
                        f"{api_url}/upload",
                        files=files,
                        timeout=TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        with status_container:
                            st.success(
                                f"✅ Uploaded: {file.name}\n"
                                f"Chunks ingested: {result.get('chunks_ingested', 0)}"
                            )
                        success_count += 1
                    else:
                        error_msg = response.json().get("detail", "Unknown error")
                        with status_container:
                            st.error(f"❌ Failed to upload {file.name}: {error_msg}")
                        error_count += 1
                    
                    # Update progress
                    progress = (idx + 1) / len(uploaded_files)
                    progress_bar.progress(progress)
                    
                except Exception as e:
                    with status_container:
                        st.error(f"❌ Error uploading {file.name}: {str(e)}")
                    error_count += 1
            
            # Summary
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Successful", success_count)
            with col2:
                st.metric("Failed", error_count)
            
            if success_count > 0:
                st.success(f"✅ Successfully uploaded {success_count} file(s)!")

# Tab 2: Search
with tab2:
    st.subheader("Search Resumes")
    st.markdown("Ask questions about the uploaded resumes. The AI will search through all documents and provide relevant answers.")
    
    # Search input
    query = st.text_area(
        "Enter your search query",
        placeholder="e.g., Find candidates with Python experience...",
        height=100,
        key="search_input"
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        search_button = st.button("🔍 Search", key="search_button")
    
    if search_button:
        if not query or not query.strip():
            st.error("❌ Please enter a search query")
        elif len(query) > 500:
            st.error("❌ Query is too long (max 500 characters)")
        else:
            try:
                with st.spinner("Searching resumes..."):
                    response = requests.post(
                        f"{api_url}/search",
                        json={"query": query, "top_k": 5},
                        timeout=TIMEOUT
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Add to search history
                    st.session_state.search_history.append({
                        "query": query,
                        "answer": result.get("answer", "No response")
                    })
                    
                    # Display result
                    st.markdown("---")
                    st.markdown("### 📋 Search Result")
                    st.markdown(result.get("answer", "No answer generated"))
                    
                    # Show sources if available
                    if result.get("sources"):
                        st.markdown("### 📚 Sources")
                        for source in result["sources"]:
                            st.info(source)
                    
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Search failed: {error_detail}")
                    
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. The API is taking too long to respond.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Search history
    if st.session_state.search_history:
        st.markdown("---")
        st.subheader("📜 Search History")
        
        for idx, item in enumerate(reversed(st.session_state.search_history[-5:])):
            with st.expander(f"Query: {item['query'][:50]}..."):
                st.markdown("**Question:**")
                st.write(item['query'])
                st.markdown("**Answer:**")
                st.write(item['answer'])
        
        if st.button("🗑️ Clear History"):
            st.session_state.search_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
    Resume Analyzer RAG | Powered by LangChain, Mistral AI, and MongoDB
    </div>
    """,
    unsafe_allow_html=True
)