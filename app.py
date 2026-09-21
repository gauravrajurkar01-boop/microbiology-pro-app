import streamlit as st
import requests

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")
st.title("🔬 Clinical Microbiology Research Suite")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("🔑 API Configuration")
    st.markdown("Get keys: [Groq (Free)](https://console.groq.com) | [HF (Free)](https://huggingface.co/settings/tokens)")
    
    # Check if keys exist in Streamlit Secrets, otherwise use empty string
    default_groq = st.secrets.get("groq_key", "")
    default_hf = st.secrets.get("hf_token", "")
    
    user_groq = st.text_input("Groq API Key (starts with gsk_)", value=default_groq, type="password")
    user_hf = st.text_input("Hugging Face Token (starts with hf_)", value=default_hf, type="password")
    
    st.info("Note: If you saved keys in 'Secrets', they will appear here as dots.")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer (Jenni Style)", "🔎 Literature Search", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Academic Writing Assistant")
    text_input = st.text_area("Start your clinical draft here...", height=300)
    
    if st.button("Jenni AI: Auto-complete Next Paragraph"):
        if not user_groq:
            st.error("⚠️ Error: Groq Key is missing. Please paste it in the sidebar.")
        else:
            headers = {
                "Authorization": f"Bearer {user_groq.strip()}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": "You are a PhD in Clinical Microbiology. Write in formal academic tone for a Q1 journal. Use Lancet style (middle dots for decimals, italics for S Typhi)."},
                    {"role": "user", "content": f"Continue this text: {text_input}"}
                ],
                "temperature": 0.5
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    result = response.json()
                    st.write("### Suggested Addition:")
                    st.info(result['choices'][0]['message']['content'])
                elif response.status_code == 401:
                    st.error("❌ Key Error: The Groq key you provided is invalid. Go to Groq and make a new one.")
                else:
                    st.error(f"❌ Connection Error: Server responded with {response.status_code}")
            except Exception as e:
                st.error(f"❌ Critical Error: {str(e)}")

# --- TAB 2: LITERATURE ---
with tab2:
    st.subheader("Semantic Scholar Search")
    query = st.text_input("Keywords (e.g. S Typhi biofilm resistance)")
    if st.button("Search Papers"):
        try:
            res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract")
            data = res.json()
            for p in data.get('data', []):
                st.markdown(f"**{p['title']} ({p['year']})**  \n[View Paper]({p['url']})")
                st.caption(p.get('abstract', 'No abstract available')[:300] + "...")
        except:
            st.error("Could not connect to literature database.")

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Content Detector")
    check_text = st.text_area("Paste text to analyze...", height=200)
    if st.button("Run Detection"):
        if not user_hf:
            st.error("⚠️ Error: Hugging Face Token is missing in the sidebar.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {user_hf.strip()}"}
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": check_text})
                output = response.json()
                # Extract ChatGPT score
                scores = output[0]
                ai_score = next(item for item in scores if item["label"] == "ChatGPT")["score"]
                st.metric("AI Probability", f"{round(ai_score * 100, 2)}%")
            except:
                st.error("The detector model is loading. Please wait 20 seconds and try again.")
