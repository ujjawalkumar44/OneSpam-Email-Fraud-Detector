import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
import base64
import re
import string
import nltk
from pathlib import Path
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

APP_ROOT = Path(__file__).resolve().parent

def ensure_nltk_data():
    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)

ensure_nltk_data()

# Page Configuration
st.set_page_config(
    page_title="OneSpam AI — Straw Hat Email Guard",
    page_icon="☠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAV_HOME = "🏠 Thousand Sunny"
NAV_ANALYZE = "🔍 Den Den Mushi Scan"
NAV_HISTORY = "📜 Ship's Log"
NAV_STATS = "📊 Navigator's Charts"
NAV_ABOUT = "ℹ️ Straw Hat Crew"

# Text Preprocessing Function
ps = PorterStemmer()
def transform_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    words = [word for word in words if word not in stopwords.words('english')]
    words = [ps.stem(word) for word in words]
    return " ".join(words)

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def load_models():
    model_path = APP_ROOT / "models" / "model.pkl"
    vectorizer_path = APP_ROOT / "models" / "vectorizer.pkl"
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
        return model, vectorizer
    except Exception:
        return None, None

@st.cache_data
def background_data_url() -> str:
    for name in ("assets/thousand_sunny_bg_web.jpg", "assets/thousand_sunny_bg.png"):
        path = APP_ROOT / name
        if path.is_file():
            mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
            encoded = base64.b64encode(path.read_bytes()).decode()
            return f"data:{mime};base64,{encoded}"
    return ""

def asset_path(relative_path: str) -> Path:
    return APP_ROOT / relative_path

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Pirata+One&family=Creepster&display=swap');

.stApp {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Wooden Glassmorphism Board */
.glass-card {
    background: rgba(101, 67, 33, 0.82);
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 20px,
        rgba(0,0,0,0.1) 20px,
        rgba(0,0,0,0.1) 21px
    );
    border-radius: 12px;
    border: 5px solid #4a2e15;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5);
    padding: 25px;
    margin: 15px 0;
    color: #fceea7;
    position: relative;
    overflow: hidden;
}

.danger-glow {
    animation: pulseDanger 2s infinite;
}
@keyframes pulseDanger {
    0% { box-shadow: 0 0 20px rgba(225, 112, 85, 0.5); border: 2px solid #e17055; }
    50% { box-shadow: 0 0 40px rgba(225, 112, 85, 1); border: 2px solid #ff7675; transform: scale(1.02); }
    100% { box-shadow: 0 0 20px rgba(225, 112, 85, 0.5); border: 2px solid #e17055; }
}
.safe-glow {
    animation: pulseSafe 2s infinite;
}
@keyframes pulseSafe {
    0% { box-shadow: 0 0 20px rgba(85, 239, 196, 0.5); border: 2px solid #55efc4; }
    50% { box-shadow: 0 0 40px rgba(85, 239, 196, 1); border: 2px solid #00b894; transform: scale(1.02); }
    100% { box-shadow: 0 0 20px rgba(85, 239, 196, 0.5); border: 2px solid #55efc4; }
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(11, 29, 58, 0.92) 0%, rgba(19, 39, 68, 0.88) 100%) !important;
    border-right: 3px solid #8B6914;
    box-shadow: inset -4px 0 12px rgba(0,0,0,0.4);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
h1, h2, h3, p, label {
    color: white !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}

/* ===== Straw Hat Jolly Roger Waving Flag ===== */
@keyframes flagWave {
    0%   { 
        transform: perspective(600px) rotateY(0deg) skewY(0deg) scaleX(1);
        border-radius: 20px 5px 5px 40px / 30px 5px 5px 20px;
    }
    25%  { 
        transform: perspective(600px) rotateY(6deg) skewY(-4deg) scaleX(0.95);
        border-radius: 40px 8px 8px 15px / 20px 8px 8px 50px;
    }
    50%  { 
        transform: perspective(600px) rotateY(-10deg) skewY(5deg) scaleX(1.06);
        border-radius: 15px 5px 5px 60px / 40px 5px 5px 15px;
    }
    75%  { 
        transform: perspective(600px) rotateY(4deg) skewY(-3deg) scaleX(0.96);
        border-radius: 50px 8px 8px 20px / 15px 8px 8px 40px;
    }
    100% { 
        transform: perspective(600px) rotateY(0deg) skewY(0deg) scaleX(1);
        border-radius: 20px 5px 5px 40px / 30px 5px 5px 20px;
    }
}
@keyframes fabricFold {
    0%,100% { background-position: 0% 0%; }
    25%      { background-position: 30px 5px; }
    50%      { background-position: -20px -5px; }
    75%      { background-position: 15px 3px; }
}
@keyframes skullPulse {
    0%,100% { opacity: 0.85; text-shadow: 0 0 10px rgba(255,255,255,0.4); }
    50%      { opacity: 1;    text-shadow: 0 0 25px rgba(255,255,255,0.9), 0 0 50px rgba(255,215,0,0.4); }
}
@keyframes poleSway {
    0%,100% { transform: rotate(0deg); }
    50%      { transform: rotate(1.5deg); }
}

/* Flag container — wooden pole on RIGHT like a mast */
.stButton {
    position: relative;
    padding-right: 22px !important;
}
.stButton::before {
    content: '';
    position: absolute;
    right: 6px;
    top: -18px;
    bottom: -18px;
    width: 14px;
    background: linear-gradient(90deg, #6B3A1F, #A0652C, #8B5E3C, #5C3317, #3E200D);
    border-radius: 7px;
    box-shadow: -2px 0 8px rgba(0,0,0,0.5), inset -2px 0 4px rgba(0,0,0,0.3);
    z-index: 10;
    animation: poleSway 4s ease-in-out infinite;
    transform-origin: bottom center;
}
/* Pole knot / rope tie */
.stButton::after {
    content: '';
    position: absolute;
    right: 2px;
    top: -4px;
    width: 22px;
    height: 14px;
    background: #3E200D;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    z-index: 11;
}

/* The black pirate flag cloth */
.stButton>button {
    background: #111111;
    background-image:
        radial-gradient(ellipse at 30% 50%, rgba(40,40,40,0.6) 0%, transparent 60%),
        repeating-linear-gradient(
            80deg,
            transparent 0px, transparent 25px,
            rgba(255,255,255,0.02) 25px, rgba(255,255,255,0.02) 27px
        );
    color: white !important;
    border: none !important;
    padding: 20px 60px 20px 30px !important;
    font-size: 22px !important;
    font-weight: 900 !important;
    font-family: 'Segoe UI', 'Trebuchet MS', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 5px;
    height: 90px !important;
    width: 100% !important;
    transform-origin: right center;
    border-radius: 20px 5px 5px 40px / 30px 5px 5px 20px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    box-shadow: -5px 5px 15px rgba(0,0,0,0.7) !important;
    transition: all 0.3s ease;
}

/* Skull and crossbones watermark */
.stButton>button::before {
    content: '☠';
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    font-size: 55px;
    opacity: 0.15;
    animation: skullPulse 3s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

/* Fabric wrinkle / fold shadow lines */
.stButton>button::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        linear-gradient(120deg, transparent 30%, rgba(0,0,0,0.3) 45%, transparent 55%),
        linear-gradient(100deg, transparent 60%, rgba(0,0,0,0.2) 70%, transparent 80%);
    pointer-events: none;
    animation: fabricFold 2.5s ease-in-out infinite reverse;
    z-index: 1;
}

.stButton>button:hover {
    background: #1a0000 !important;
    background-image:
        radial-gradient(ellipse at 30% 50%, rgba(139,0,0,0.4) 0%, transparent 60%),
        repeating-linear-gradient(
            80deg,
            transparent 0px, transparent 25px,
            rgba(255,0,0,0.04) 25px, rgba(255,0,0,0.04) 27px
        ) !important;
    box-shadow: -5px 5px 25px rgba(139,0,0,0.5), 0 0 40px rgba(255,0,0,0.2) !important;
    letter-spacing: 7px;
}
.stButton>button:active {
    animation-play-state: paused !important;
}

/* Text Area */
.stTextArea textarea {
    background-color: rgba(0,0,0,0.5) !important;
    color: white !important;
    border: 2px solid rgba(255,255,255,0.4) !important;
    border-radius: 15px !important;
    transition: all 0.3s ease;
}
.stTextArea textarea:focus {
    border-color: #55efc4 !important;
    box-shadow: 0 0 15px rgba(85, 239, 196, 0.5) !important;
}

/* Image Animations */
@keyframes slideIn {
    0% { transform: translateX(-200px) scale(0.5) rotate(-20deg); opacity: 0; filter: blur(10px); }
    70% { transform: translateX(20px) scale(1.1) rotate(5deg); opacity: 1; filter: blur(0px); }
    100% { transform: translateX(0) scale(1) rotate(0deg); opacity: 1; filter: blur(0px); }
}
@keyframes bounceIn {
    0% { transform: translateY(200px) scale(0.5); opacity: 0; }
    50% { transform: translateY(-20px) scale(1.1); opacity: 1; }
    100% { transform: translateY(0) scale(1); opacity: 1; }
}
.zoro-anim, .sanji-anim {
    animation: slideIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.6));
    max-height: 180px;
    object-fit: contain;
}
.luffy-anim, .nami-anim {
    animation: bounceIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.6));
    max-height: 180px;
    object-fit: contain;
}

/* ===== Crew Banner - Characters Hanging Above Bar ===== */
@keyframes titleGlow {
    0%,100% { text-shadow: 0 0 20px rgba(255,215,0,0.5), 0 4px 8px rgba(0,0,0,0.8); }
    50% { text-shadow: 0 0 40px rgba(255,215,0,0.9), 0 0 60px rgba(255,69,0,0.4), 0 4px 8px rgba(0,0,0,0.8); }
}

/* ===== ONE SPAM Logo — Jolly Roger as the O ===== */
.onespam-logo {
    text-align: center;
    padding: 30px 0 10px 0;
}
.onespam-logo .logo-text {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0px;
    font-size: 72px;
    font-weight: 900;
    font-family: Impact, 'Arial Black', sans-serif;
    letter-spacing: 6px;
    color: #ffd700;
    animation: titleGlow 3s ease-in-out infinite;
    line-height: 1;
}
.onespam-logo .logo-text .skull-o {
    display: inline-block;
    font-size: 72px;
    line-height: 1;
    vertical-align: middle;
    margin: 0 4px;
    color: #1a1a1a;
    text-shadow: 0 0 12px rgba(255,215,0,0.8), 2px 2px 0 #ffd700;
    animation: skullSpin 8s ease-in-out infinite;
}
@keyframes skullSpin {
    0%,100% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 12px rgba(255,215,0,0.6)); }
    25% { transform: scale(1.08) rotate(3deg); filter: drop-shadow(0 0 20px rgba(255,215,0,0.9)); }
    50% { transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 12px rgba(255,215,0,0.6)); }
    75% { transform: scale(1.08) rotate(-3deg); filter: drop-shadow(0 0 20px rgba(255,215,0,0.9)); }
}
.onespam-logo .logo-text .red { color: #ff3333; }
.onespam-logo .subtitle {
    font-size: 18px;
    color: #fceea7;
    letter-spacing: 8px;
    text-transform: uppercase;
    margin-top: 8px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
}

.op-heading {
    font-family: 'Pirata One', Impact, cursive !important;
    color: #ffd700 !important;
    letter-spacing: 2px;
}
.op-body {
    color: #fceea7 !important;
    line-height: 1.65;
}
.wanted-poster {
    background: linear-gradient(145deg, #f4e4bc 0%, #e8d4a8 40%, #d4b896 100%);
    border: 6px solid #3d2817;
    border-radius: 4px;
    padding: 20px;
    color: #1a0f00 !important;
    box-shadow: inset 0 0 30px rgba(0,0,0,0.15), 8px 8px 0 #2a1810;
    position: relative;
}
.wanted-poster::before {
    content: 'WANTED';
    position: absolute;
    top: 8px;
    right: 12px;
    font-family: 'Creepster', Impact, cursive;
    font-size: 28px;
    color: #8b0000;
    opacity: 0.35;
    letter-spacing: 4px;
}
.wanted-poster h3, .wanted-poster p {
    color: #1a0f00 !important;
    text-shadow: none !important;
}
.deck-tile {
    background: rgba(74, 46, 21, 0.85);
    border: 3px solid #8B6914;
    border-radius: 10px;
    padding: 18px 12px;
    text-align: center;
    min-height: 120px;
    box-shadow: inset 0 2px 8px rgba(255,215,0,0.1);
}
.deck-tile h3 {
    font-family: 'Pirata One', cursive !important;
    color: #ffd700 !important;
    margin: 0;
}
.deck-tile p {
    color: #fceea7 !important;
    font-size: 14px;
    margin-top: 8px;
}
.berry-metric {
    font-family: 'Pirata One', cursive;
    font-size: 2rem;
    color: #ffd700;
    text-shadow: 0 0 12px rgba(255,215,0,0.5);
}
.berry-metric span {
    font-size: 1rem;
    color: #e17055;
}
.sidebar-brand {
    text-align: center;
    padding: 12px 0 20px;
    border-bottom: 2px dashed rgba(255,215,0,0.35);
    margin-bottom: 16px;
}
.sidebar-brand img {
    width: 72px;
    height: 72px;
    filter: drop-shadow(0 4px 8px rgba(0,0,0,0.6));
}
.sidebar-brand h2 {
    font-family: 'Pirata One', cursive !important;
    color: #ffd700 !important;
    margin: 8px 0 4px;
    font-size: 1.4rem;
}
.crew-roster {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    margin-top: 20px;
}
.crew-card {
    background: rgba(19, 39, 68, 0.7);
    border: 2px solid #ffd700;
    border-radius: 12px;
    padding: 12px;
    text-align: center;
}
.crew-card img {
    max-height: 100px;
    object-fit: contain;
}
.crew-card h4 {
    font-family: 'Pirata One', cursive !important;
    color: #ffd700 !important;
    margin: 8px 0 4px;
}
[data-testid="stMetric"] {
    background: rgba(101, 67, 33, 0.6) !important;
    border: 2px solid #8B6914 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}
[data-testid="stMetric"] label {
    font-family: 'Pirata One', cursive !important;
    color: #ffd700 !important;
}
[data-testid="stDataFrame"] {
    border: 3px solid #4a2e15;
    border-radius: 8px;
}
div[data-baseweb="radio"] label {
    font-family: 'Segoe UI', sans-serif !important;
    padding: 8px 4px !important;
}
.stSpinner > div {
    border-top-color: #ffd700 !important;
}

"""

def inject_styles():
    bg = background_data_url()
    if bg:
        app_bg = f"""
.stApp {{
    background-image: linear-gradient(rgba(11, 29, 58, 0.25), rgba(11, 29, 58, 0.45)),
        url("{bg}");
    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}}
"""
    else:
        app_bg = """
.stApp {
    background: linear-gradient(165deg, #0B1D3A 0%, #1a4a6e 35%, #0d2847 65%, #0B1D3A 100%);
    background-attachment: fixed;
}
"""
    st.markdown(f"<style>{BASE_CSS}{app_bg}</style>", unsafe_allow_html=True)

inject_styles()

# Sidebar Navigation — Thousand Sunny helm
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size:56px; line-height:1;">☠️</div>
        <h2>OneSpam AI</h2>
        <p style="font-size:12px; color:#fceea7; margin:0;">Thousand Sunny · East Blue</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("##### 🧭 Set your Log Pose")
    selection = st.radio(
        "Route",
        [NAV_HOME, NAV_ANALYZE, NAV_HISTORY, NAV_STATS, NAV_ABOUT],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("⚓ Grand Line Cyber Security · Straw Hat Pirates")

if selection == NAV_HOME:
    st.markdown(f"""
    <div class="onespam-logo">
        <div class="logo-text">
            <span class="skull-o">☠</span><span class="red">NE</span>&nbsp;SPAM
        </div>
        <div class="subtitle">⚓ Sail the Grand Line of Your Inbox ⚓</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("""
    <p class="op-body">
    Ahoy, Nakama! <strong>OneSpam AI</strong> is the Straw Hat crew's Den Den Mushi for the digital seas.
    Marines and fraudsters hide in phishing mail like treasure under false maps — our Devil Fruit–powered
    NLP model reads the wind and tells safe harbors from pirate traps.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="deck-tile">
            <h3>⚡ Gum-Gum Speed</h3>
            <p>Instant scans — faster than Luffy stretching to the crow's nest.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="deck-tile">
            <h3>🧠 Robin's Archive</h3>
            <p>Naive Bayes + NLTK — ancient texts decoded for modern spam.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="deck-tile">
            <h3>🏴‍☠️ Pirate Soul</h3>
            <p>Full One Piece voyage — pirate UI on every deck.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='op-heading'>🗺️ Chart Your Next Island</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p class="op-body">Use the <strong>Log Pose</strong> in the sidebar: scan suspicious mail on
    <em>Den Den Mushi Scan</em>, review bounties in the <em>Ship's Log</em>, and let Nami plot trends on
    <em>Navigator's Charts</em>.</p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif selection == NAV_ANALYZE:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='op-heading'>🔍 Den Den Mushi — Email Scan</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p class="op-body">Transmit the suspicious message below. The crew will judge whether it's
    <strong>treasure mail</strong> or a <strong>World Government trap</strong>.</p>
    """, unsafe_allow_html=True)

    email_text = st.text_area(
        "Message from the sea:",
        height=200,
        placeholder="Ahoy! Paste the suspicious email here — Robin is ready to read the Poneglyph..."
    )

    analyze_clicked = st.button("🏴‍☠️ HOIST THE FLAG — SCAN")

    if analyze_clicked:
        if email_text.strip() == "":
            st.warning("⚠️ Empty seas! Paste email text before we set sail.")
        else:
            model, vectorizer = load_models()
            if not model or not vectorizer:
                st.error("⚓ Models missing! Add models/model.pkl and models/vectorizer.pkl to the repo.")
            else:
                with st.spinner("⚔️ Zoro's three-sword style… slicing through spam syntax…"):
                    transformed = transform_text(email_text)
                    vectorized = vectorizer.transform([transformed])
                    prediction = model.predict(vectorized)[0]
                    proba = model.predict_proba(vectorized)[0]
                    confidence = proba[prediction] * 100
                    risk = "High" if confidence > 80 else "Medium" if prediction == 1 else "Low"

                    st.session_state.history.append({
                        "text": email_text[:50] + "...",
                        "prediction": "Phishing/Fraud" if prediction == 1 else "Safe",
                        "confidence": confidence,
                        "risk": risk
                    })

                    if prediction == 1:
                        st.markdown("""
                            <div class='glass-card danger-glow' style='text-align: center;'>
                                <h2 class='op-heading' style='color: #ff9f43 !important;'>☠️ WANTED — PHISHING PIRATE!</h2>
                                <p class="op-body">Marine alert! This mail smells like a fraudster from the New World.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            st.image(str(asset_path("assets/zoro_slash.png")), width=160)
                            st.markdown("**Zoro:** Santoryu — spam cut down!")
                        with c2:
                            st.image(str(asset_path("assets/nami_attack.png")), width=160)
                            st.markdown("**Nami:** Bounty raised — do not open!")
                        st.markdown(
                            f"<p class='berry-metric' style='text-align:center;'>"
                            f"Threat: {risk} <span>·</span> Berry confidence: {confidence:.2f}%</p>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown("""
                            <div class='glass-card safe-glow' style='text-align: center;'>
                                <h2 class='op-heading' style='color: #55efc4 !important;'>✅ SAFE HARBOR — LEGIT MAIL!</h2>
                                <p class="op-body">Shishishi! No fraud detected — feast at the Sunny's galley!</p>
                            </div>
                        """, unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            st.image(str(asset_path("assets/luffy_thumbsup.png")), width=160)
                            st.markdown("**Luffy:** Meat party approved!")
                        with c2:
                            st.image(str(asset_path("assets/chopper_happy.png")), width=160)
                            st.markdown("**Chopper:** All clear, doc!")
                        st.markdown(
                            f"<p class='berry-metric' style='text-align:center;'>"
                            f"Threat: {risk} <span>·</span> Berry confidence: {confidence:.2f}%</p>",
                            unsafe_allow_html=True,
                        )
    st.markdown("</div>", unsafe_allow_html=True)

elif selection == NAV_HISTORY:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='op-heading'>📜 Ship's Log — Wanted Posters</h2>", unsafe_allow_html=True)
    if len(st.session_state.history) == 0:
        st.markdown('<div class="wanted-poster" style="text-align:center;">', unsafe_allow_html=True)
        st.image(str(asset_path("assets/robin_detective.png")), width=120)
        st.markdown("<h3>No bounties posted yet</h3><p>Robin says: the log is empty. Scan mail on Den Den Mushi first!</p></div>", unsafe_allow_html=True)
    else:
        df = pd.DataFrame(st.session_state.history)
        fraud_count = (df["prediction"] == "Phishing/Fraud").sum()
        safe_count = len(df) - fraud_count
        c1, c2, c3 = st.columns(3)
        c1.metric("📋 Total scans", len(df))
        c2.metric("☠️ Pirates caught", fraud_count)
        c3.metric("✅ Safe harbors", safe_count)
        st.markdown("#### Latest wanted notices")
        st.dataframe(df, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif selection == NAV_STATS:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='op-heading'>📊 Navigator's Charts — Nami's Deck</h2>", unsafe_allow_html=True)

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4 class='op-heading'>🏴‍☠️ Pirates vs Marines (Safe)</h4>", unsafe_allow_html=True)
            fig_pie = px.pie(
                df, names='prediction', color='prediction',
                title="Grand Line Mail Split",
                color_discrete_map={'Safe': '#55efc4', 'Phishing/Fraud': '#E63946'}
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fceea7', title_font_color='#ffd700'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown("<h4 class='op-heading'>⚡ Clima-Tact Risk Levels</h4>", unsafe_allow_html=True)
            fig_bar = px.histogram(
                df, x='risk', color='risk',
                title="Storm intensity on the seas",
                color_discrete_map={'Low': '#55efc4', 'Medium': '#fdcb6e', 'High': '#E63946'}
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fceea7', title_font_color='#ffd700'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.image(str(asset_path("assets/franky_super.png")), width=100)
        st.markdown("<p class='op-body' style='text-align:center;'><strong>Franky:</strong> SUPER charts! Keep scanning to fill the log pose!</p>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="wanted-poster" style="text-align:center;">', unsafe_allow_html=True)
        st.image(str(asset_path("assets/nami_attack.png")), width=120)
        st.markdown("<h3>Empty chart table</h3><p>Nami needs voyage data! Analyze emails first, then return to plot the Grand Line.</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif selection == NAV_ABOUT:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 class='op-heading'>ℹ️ Straw Hat Crew — About OneSpam AI</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p class="op-body">
    <strong>OneSpam AI</strong> guards your inbox like the Thousand Sunny crosses the Grand Line.
    NLP + Naive Bayes (Robin-grade text analysis) spots phishing before fraudsters steal your berry bounty.
    </p>
    """, unsafe_allow_html=True)
    st.markdown("### ⚙️ Shipwright's Blueprint")
    st.markdown("""
    - **Deck (UI)**: Streamlit, One Piece CSS & Jolly Roger styling
    - **Engine Room**: Python, NLTK, Scikit-learn
    - **Charts**: Plotly — Nami-approved navigation
    """)
    st.markdown("### 👒 Crew on this voyage")
    crew = [
        ("assets/luffy_sprite.png", "Monkey D. Luffy", "Captain — celebrates safe mail"),
        ("assets/zoro_sprite.png", "Roronoa Zoro", "First mate — slashes spam"),
        ("assets/nami_attack.png", "Nami", "Navigator — risk & stats"),
        ("assets/sanji_kick.png", "Sanji", "Cook — kicks fraud links"),
        ("assets/chopper_happy.png", "Chopper", "Doctor — all-clear checks"),
        ("assets/robin_detective.png", "Nico Robin", "Archaeologist — reads mail glyphs"),
        ("assets/franky_super.png", "Franky", "Shipwright — SUPER dashboards"),
    ]
    cols = st.columns(4)
    for i, (img, name, role) in enumerate(crew):
        with cols[i % 4]:
            st.image(str(asset_path(img)), width=110)
            st.markdown(f"**{name}**")
            st.caption(role)
    st.markdown("</div>", unsafe_allow_html=True)
