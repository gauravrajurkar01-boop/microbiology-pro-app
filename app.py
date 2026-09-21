import streamlit as st
import requests
import json

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")

# --- AUTO-LOAD KEYS FROM SECRETS ---
# This looks for your saved keys automatically
SECRET_GROQ = st.secrets.get("groq_key", "")
SECRET_HF = st.secrets.get("hf_token", "")

st.title("🔬 Clinical Microbiology Research Suite")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 API Configuration")
    
    # If secrets exist, we show a message. If not, we ask for manual input.
    if SECRET_GROQ:
        st.success("✅ Groq Key loaded from Secrets")
        user_groq = SECRET_GROQ
    else:
        user_groq = st.text_input("Groq API Key (gsk_...)", type="password")
        
    if SECRET_HF:
        st.success("✅ Hugging Face Token loaded")
        user_hf = SECRET_HF
    else:
        user_hf = st.text_input("Hugging Face Token (hf_...)", type="password")

    st.divider()
    st.subheader("🤖 AI Model Selection")
    
    # Fetch models dynamically
    model_list = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]
    if user_groq:
        try:
            m_res = requests.get("https://api.groq.com/openai/v1/models", 
                                 headers={"Authorization": f"Bearer {user_groq.strip()}"})
            if m_res.status_code == 200:
                model_list = [m['id'] for m in m_res.json()['data'] if 'vision' not in m['id']]
        except: pass
    
    model_choice = st.selectbox("Active Model:", model_list)

tab1, tab2, tab3 = st.tabs(["📝 AI Writer", "🔎 Literature", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Academic Writing Assistant")
    text_input = st.text_area("Type your draft here...", height=250)
    
    if st.button("Jenni AI: Auto-complete"):
        if not user_groq:
            st.error("❌ No Groq Key found. Add it to Sidebar or Secrets.")
        else:
            headers = {
                "Authorization": f"Bearer {user_groq.strip()}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_choice,
                "messages": [
                    {"role": "system", "content": "You are a Senior Clinical Microbiologist. Use Lancet Microbe style. Italicize species names."},
                    {"role": "user", "content": f"Continue this text: {text_input}"}
                ]
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                st.info(res.json()['choices'][0]['message']['content'])
            else:
                st.error(f"Error {res.status_code}: {res.text}")

# --- TAB 2: LITERATURE ---
with tab2:
    st.subheader("Literature Search")
    query = st.text_input("Keywords")
    if st.button("Search"):
        res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract").json()
        for p in res.get('data', []):
            st.markdown(f"**{p['title']} ({p['year']})**  \n[View Paper]({p['url']})")

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Content Detector")
    check_text = st.text_area("Paste text to analyze...")
    if st.button("Run Check"):
        if not user_hf:
            st.error("❌ No Hugging Face Token found.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {user_hf.strip()}"}
            res = requests.post(API_URL, headers=headers, json={"inputs": check_text}).json()
            try:
                # Handle potential list response
                if isinstance(res, list): scores = res[0]
                else: scores = res
                val = next(item for item in scores if item["label"] == "ChatGPT")["score"]
                st.metric("AI Probability", f"{round(val * 100, 2)}%")
            except:
                st.error("Model is waking up. Try again in 10 seconds.")
