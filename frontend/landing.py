import streamlit as st

st.set_page_config(page_title="Book Summarizer", layout="wide")

def landing_page():
    st.title("Welcome to Book Summarizer")
    if st.button("Get Started"):
        st.session_state["current_page"] = "register"
        st.rerun()
    if st.button("Login"):
        st.session_state["current_page"] = "login"
        st.rerun()

# =======================
# Custom CSS - Full Design
# =======================
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Navigation Bar */
    .nav-bar {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .logo {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Hero Section */
    .hero {
        text-align: center;
        color: white;
        margin: 3rem 0;
        padding: 2rem;
    }
    
    .hero h1 {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-weight: 800;
        line-height: 1.2;
    }
    
    .hero p {
        font-size: 1.4rem;
        opacity: 0.95;
        margin-bottom: 2rem;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Custom Buttons */
    .stButton > button {
        width: 100%;
        padding: 1rem 2rem;
        border-radius: 30px;
        font-size: 1.2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:first-child {
        background: white;
        color: #667eea;
        border: 2px solid white;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    /* Feature Cards */
    .feature-section {
        background: white;
        padding: 4rem 2rem;
        border-radius: 20px;
        margin: 3rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    
    .feature-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        transition: transform 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        height: 100%;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .feature-box:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(102, 126, 234, 0.3);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        display: block;
    }
    
    .feature-box h3 {
        color: #333;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .feature-box p {
        color: #666;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* How It Works Section */
    .how-it-works {
        color: white;
        text-align: center;
        padding: 3rem 0;
    }
    
    .how-it-works h2 {
        font-size: 2.5rem;
        margin-bottom: 3rem;
        font-weight: 700;
    }
    
    .step-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        height: 100%;
    }
    
    .step-number {
        width: 70px;
        height: 70px;
        background: white;
        color: #667eea;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 0 auto 1.5rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .step-box h3 {
        font-size: 1.4rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .step-box p {
        font-size: 1.1rem;
        opacity: 0.9;
        line-height: 1.6;
    }
    
    /* Stats Section */
    .stats-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .footer {
        background: rgba(0, 0, 0, 0.2);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-top: 3rem;
    }
    
    .footer p {
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero h1 {
            font-size: 2.5rem;
        }
        
        .hero p {
            font-size: 1.1rem;
        }
        
        .feature-box {
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# =======================
# Navigation Bar
# =======================
st.markdown("""
<div class="nav-bar">
    <div class="logo">📚 BookSummarizer</div>
</div>
""", unsafe_allow_html=True)

# =======================
# Hero Section
# =======================
st.markdown("""
<div class="hero">
    <h1>Transform Books into Summaries with AI</h1>
    <p>Upload any book and get intelligent, concise summaries powered by advanced NLP technology. Save time and extract key insights effortlessly.</p>
</div>
""", unsafe_allow_html=True)

# Hero Buttons
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚀 Get Started", use_container_width=True):
            st.switch_page("frontend/Register.py")
    
    with btn_col2:
        if st.button("🔐 Login", use_container_width=True):
            st.switch_page("frontend/Login.py")

# =======================
# Features Section
# =======================
st.markdown("""
<div class="feature-section">
    <h2 style="text-align: center; color: #333; font-size: 2.5rem; margin-bottom: 3rem; font-weight: 700;">
        🚀 Powerful Features
    </h2>
</div>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">🤖</span>
        <h3>AI-Powered Summaries</h3>
        <p>Leverage state-of-the-art transformer models to generate accurate, coherent summaries that capture the essence of your books.</p>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">📄</span>
        <h3>Multiple Formats</h3>
        <p>Support for TXT, PDF, and DOCX files. Upload books in any format and get consistent, high-quality summaries.</p>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">🌍</span>
        <h3>Multi-Language Support</h3>
        <p>Automatic language detection for 55+ languages. Process books in English, Spanish, French, German, and many more.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

f4, f5, f6 = st.columns(3)

with f4:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">⚙️</span>
        <h3>Customizable Output</h3>
        <p>Choose summary length, style, and detail level. Get exactly what you need - from brief overviews to detailed analyses.</p>
    </div>
    """, unsafe_allow_html=True)

with f5:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">📊</span>
        <h3>Smart Analytics</h3>
        <p>Get insights into reading time, word count, complexity, and more. Track your reading progress with detailed statistics.</p>
    </div>
    """, unsafe_allow_html=True)

with f6:
    st.markdown("""
    <div class="feature-box">
        <span class="feature-icon">💾</span>
        <h3>Save & Export</h3>
        <p>Save your summaries to your library. Export to PDF, TXT, or copy to clipboard. Access them anytime, anywhere.</p>
    </div>
    """, unsafe_allow_html=True)

# =======================
# How It Works Section
# =======================
st.markdown("""
<div class="how-it-works">
    <h2>How It Works</h2>
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">1</div>
        <h3>Upload Your Book</h3>
        <p>Simply drag and drop or select your book file. We support TXT, PDF, and DOCX formats.</p>
    </div>
    """, unsafe_allow_html=True)

with s2:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">2</div>
        <h3>AI Processing</h3>
        <p>Our advanced AI analyzes the text, identifies key concepts, and extracts important information.</p>
    </div>
    """, unsafe_allow_html=True)

with s3:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">3</div>
        <h3>Get Your Summary</h3>
        <p>Receive a well-structured summary in seconds. Customize length and style to your preference.</p>
    </div>
    """, unsafe_allow_html=True)

with s4:
    st.markdown("""
    <div class="step-box">
        <div class="step-number">4</div>
        <h3>Save & Share</h3>
        <p>Save to your library, export as PDF, or share with others. Access your summaries anytime.</p>
    </div>
    """, unsafe_allow_html=True)

# =======================
# Stats Section
# =======================
st.markdown("<br><br>", unsafe_allow_html=True)

stat1, stat2, stat3, stat4 = st.columns(4)

with stat1:
    st.markdown("""
    <div class="stats-box">
        <div class="stat-number">50+</div>
        <div class="stat-label">Languages Supported</div>
    </div>
    """, unsafe_allow_html=True)

with stat2:
    st.markdown("""
    <div class="stats-box">
        <div class="stat-number">99%</div>
        <div class="stat-label">Accuracy Rate</div>
    </div>
    """, unsafe_allow_html=True)

with stat3:
    st.markdown("""
    <div class="stats-box">
        <div class="stat-number">10x</div>
        <div class="stat-label">Faster Reading</div>
    </div>
    """, unsafe_allow_html=True)

with stat4:
    st.markdown("""
    <div class="stats-box">
        <div class="stat-number">24/7</div>
        <div class="stat-label">Available</div>
    </div>
    """, unsafe_allow_html=True)

# =======================
# Footer
# =======================
st.markdown("""
<div class="footer">
    <p style="font-size: 1.2rem; font-weight: 600;">© 2024 BookSummarizer — Powered by Advanced AI Technology</p>
    <p style="opacity: 0.8;">Developed as part of an Intelligent Book Summarization Platform</p>
</div>
""", unsafe_allow_html=True)



