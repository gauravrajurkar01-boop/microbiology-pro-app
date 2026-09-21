import streamlit as st
import requests
import json

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")
st.title("🔬 Clinical Microbiology Research Suite")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🔑 API Configuration")
    # Priority: 1. Sidebar, 2. Streamlit Secrets
    user_groq = st.text_input("Groq API Key (gsk_...)", value=st.secrets.get("groq_key", ""), type="password")
    user_hf = st.text_input("Hugging Face Token (hf_...)", value=st.secrets.get("hf_token", ""), type="password")
    st.markdown("[Get Groq Key](https://console.groq.com/keys)")
    st.markdown("[Get HF Token](https://huggingface.co/settings/tokens)")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer (Jenni Style)", "🔎 Literature Search", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Academic Writing Assistant")
    text_input = st.text_area("Type your clinical observations or draft here...", height=250)
    
    if st.button("Jenni AI: Auto-complete Next Paragraph"):
        if not user_groq:
            st.error("⚠️ Please paste your Groq Key in the sidebar.")
        elif len(text_input.strip()) < 10:
            st.warning("⚠️ Please type at least a few words first so the AI has context to continue.")
        else:
            headers = {
                "Authorization": f"Bearer {user_groq.strip()}",
                "Content-Type": "application/json"
            }
            # Updated to the most stable high-performance model
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a Senior Clinical Microbiologist. Write in a formal academic tone for a Q1 journal (Lancet style). Italicize species names (e.g., S Typhi)."},
                    {"role": "user", "content": f"Continue the following research text: {text_input}"}
                ],
                "temperature": 0.6,
                "max_tokens": 1024
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                         headers=headers, 
                                         data=json.dumps(payload))
                
                if response.status_code == 200:
                    st.write("### Suggested Addition:")
                    st.info(response.json()['choices'][0]['message']['content'])
                else:
                    # This tells us EXACTLY what is wrong (e.g., 'invalid model' or 'empty message')
                    error_details = response.json().get('error', {}).get('message', 'Unknown Error')
                    st.error(f"❌ Server Error {response.status_code}: {error_details}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")

# --- TAB 2: LITERATURE ---
with tab2:
    st.subheader("Semantic Scholar Literature Search")
    query = st.text_input("Keywords (e.g., Carbapenem resistance Klebsiella)")
    if st.button("Search Papers"):
        try:
            res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract")
            data = res.json()
            if 'data' in data:
                for p in data['data']:
                    st.markdown(f"**{p['title']} ({p['year']})**  \n[View Full Paper]({p['url']})")
                    st.caption(p.get('abstract', 'No abstract available')[:250] + "...")
            else:
                st.write("No papers found for this query.")
        except:
            st.error("Literature database is currently unreachable.")

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Content Detector")
    check_text = st.text_area("Paste text to analyze for AI/Plagiarism patterns...", height=200)
    if st.button("Run Detection"):
        if not user_hf:
            st.error("⚠️ Please paste your Hugging Face Token in the sidebar.")
        elif len(check_text.strip()) < 50:
            st.warning("⚠️ Please paste at least 50 words for an accurate detection.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {user_hf.strip()}"}
            with st.spinner("Analyzing text patterns..."):
                try:
                    response = requests.post(API_URL, headers=headers, json={"inputs": check_text})
                    output = response.json()
                    scores = output[0]
                    ai_score = next(item for item in scores if item["label"] == "ChatGPT")["score"]
                    st.metric("AI Probability", f"{round(ai_score * 100, 2)}%")
                    if ai_score > 0.5:
                        st.warning("High AI signature detected. Revision recommended.")
                    else:
                        st.success("Human-like writing patterns confirmed.")
                except:
                    st.error("Model is initializing. Please wait 20 seconds and click again.")
