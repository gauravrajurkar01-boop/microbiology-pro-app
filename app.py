import streamlit as st
import requests
import json

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")
st.title("🔬 Clinical Microbiology Research Suite")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🔑 API Configuration")
    user_groq = st.text_input("Groq API Key (gsk_...)", value=st.secrets.get("groq_key", ""), type="password")
    user_hf = st.text_input("Hugging Face Token (hf_...)", value=st.secrets.get("hf_token", ""), type="password")
    
    st.divider()
    st.subheader("🤖 Model Selection")
    # If one model gives a 404, you can just pick another from this list!
    model_choice = st.selectbox(
        "If you get a 404 error, switch models here:",
        ["llama-3.1-8b-instant", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]
    )
    st.caption("Suggested: 'llama-3.1-8b-instant' is currently the most stable.")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer (Jenni Style)", "🔎 Literature Search", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Academic Writing Assistant")
    text_input = st.text_area("Type your clinical draft here...", height=250)
    
    if st.button("Jenni AI: Auto-complete Next Paragraph"):
        if not user_groq:
            st.error("⚠️ Please paste your Groq Key in the sidebar.")
        elif len(text_input.strip()) < 5:
            st.warning("⚠️ Please type a few words first.")
        else:
            headers = {
                "Authorization": f"Bearer {user_groq.strip()}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_choice,
                "messages": [
                    {"role": "system", "content": "You are a Senior Clinical Microbiologist. Write in formal academic tone for a Q1 journal (Lancet style). Italicize species names (e.g., S Typhi)."},
                    {"role": "user", "content": f"Continue the following research text: {text_input}"}
                ],
                "temperature": 0.6
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                         headers=headers, 
                                         data=json.dumps(payload))
                
                if response.status_code == 200:
                    st.write("### Suggested Addition:")
                    st.info(response.json()['choices'][0]['message']['content'])
                else:
                    err = response.json().get('error', {}).get('message', 'Unknown Error')
                    st.error(f"❌ Error {response.status_code}: {err}")
                    st.info("💡 TIP: If it says 'Model not found', change the 'Model Selection' in the sidebar.")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

# --- TAB 2: LITERATURE ---
with tab2:
    st.subheader("Semantic Scholar Search")
    query = st.text_input("Keywords (e.g., S. Typhi XDR)")
    if st.button("Search Papers"):
        try:
            res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract")
            data = res.json()
            if 'data' in data:
                for p in data['data']:
                    st.markdown(f"**{p['title']} ({p['year']})**  \n[View Paper]({p['url']})")
            else: st.write("No papers found.")
        except: st.error("Database unreachable.")

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Content Detector")
    check_text = st.text_area("Paste text to analyze...", height=200)
    if st.button("Run Detection"):
        if not user_hf:
            st.error("⚠️ Please paste your Hugging Face Token in the sidebar.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {user_hf.strip()}"}
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": check_text})
                ai_score = response.json()[0]
                val = next(item for item in ai_score if item["label"] == "ChatGPT")["score"]
                st.metric("AI Probability", f"{round(val * 100, 2)}%")
            except:
                st.error("Model is waking up. Please wait 20 seconds.")
