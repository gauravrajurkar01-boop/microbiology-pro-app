import streamlit as st
import requests
import json

# Force Lancet Style and Page Config
st.set_page_config(page_title="Microbiology PhD Suite", layout="wide")

# --- INTERNAL KEY LOGIC ---
# This version prioritizes Secrets and cleans them automatically
GROQ_API_KEY = st.secrets.get("groq_key", "").strip()
HF_API_TOKEN = st.secrets.get("hf_token", "").strip()

st.title("🔬 Clinical Microbiology Research Suite")
st.caption("Jenni + Paperguide + Paperpal + AI Detection (Custom PhD Edition)")

# --- SIDEBAR STATUS ---
with st.sidebar:
    st.header("System Status")
    if GROQ_API_KEY.startswith("gsk_"):
        st.success("✅ Writing Engine: Connected")
    else:
        st.error("❌ Writing Engine: Key Missing/Invalid")
        
    if HF_API_TOKEN.startswith("hf_"):
        st.success("✅ Integrity Check: Connected")
    else:
        st.error("❌ Integrity Check: Token Missing/Invalid")
    
    st.divider()
    st.info("If you see 401 errors, please verify your keys in the Streamlit Secrets dashboard.")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer", "🔎 Literature Search", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Academic Writing & Auto-complete")
    user_input = st.text_area("Paste your draft here...", height=250, placeholder="Start typing about clinical microbiology...")
    
    if st.button("Jenni AI: Auto-complete"):
        if not GROQ_API_KEY:
            st.error("Missing Groq Key in Secrets.")
        else:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            # Using the most powerful current model llama-3.3-70b
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a PhD in Clinical Microbiology. Write in a formal Lancet Microbe style. Italicize species names like S Typhi."},
                    {"role": "user", "content": f"Continue this text: {user_input}"}
                ],
                "temperature": 0.5
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                st.info(response.json()['choices'][0]['message']['content'])
            else:
                st.error(f"Error {response.status_code}: {response.text}")

# --- TAB 2: LITERATURE ---
with tab2:
    st.subheader("Semantic Scholar Literature Search")
    query = st.text_input("Keywords (e.g., S Typhi XDR Pakistan)")
    if st.button("Find Papers"):
        res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract").json()
        if 'data' in res:
            for p in res['data']:
                st.markdown(f"**{p['title']} ({p['year']})**")
                st.caption(f"[Direct Link to Paper]({p['url']})")
                st.write(p.get('abstract', 'No abstract available')[:250] + "...")
                st.divider()

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Content Detector")
    detect_text = st.text_area("Paste text to analyze...", height=200)
    if st.button("Check for AI"):
        if not HF_API_TOKEN:
            st.error("Missing Hugging Face Token in Secrets.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            response = requests.post(API_URL, headers=headers, json={"inputs": detect_text})
            
            try:
                res = response.json()
                # Handle model loading
                if "error" in res:
                    st.warning("The model is loading. Please wait 20 seconds and try again.")
                else:
                    scores = res[0]
                    ai_score = next(item for item in scores if item["label"] == "ChatGPT")["score"]
                    st.metric("AI Probability", f"{round(ai_score * 100, 2)}%")
            except Exception as e:
                st.error("Could not process detection. Verify your token.")
