import streamlit as st
import requests

st.set_page_config(page_title="Microbiology Research Lab", layout="wide")

st.title("🔬 Clinical Microbiology AI Assistant")
st.markdown("---")

# --- SIDEBAR: MANUAL INPUT (NO SECRETS NEEDED) ---
with st.sidebar:
    st.header("🔑 API Setup")
    st.markdown("Paste your keys here. If they work, you will see a green 'Active' status.")
    
    # We use manual input here to bypass any "Secrets" formatting errors
    groq_input = st.text_input("Groq API Key (starts with gsk_)", type="password", help="Get at console.groq.com")
    hf_input = st.text_input("Hugging Face Token (starts with hf_)", type="password", help="Get at huggingface.co/settings/tokens")
    
    if groq_input.startswith("gsk_"):
        st.success("✅ Groq Key format looks correct.")
    else:
        st.warning("⚠️ Groq Key must start with 'gsk_'")

    if hf_input.startswith("hf_"):
        st.success("✅ HF Token format looks correct.")
    else:
        st.warning("⚠️ HF Token must start with 'hf_'")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer", "🔎 Research", "🛡️ Integrity Check"])

# --- TAB 1: AI WRITER ---
with tab1:
    st.subheader("Jenni-Style Academic Writer")
    user_text = st.text_area("Write your draft here...", height=250)
    
    if st.button("Generate Next Paragraph"):
        if not groq_input:
            st.error("Please paste your Groq key in the sidebar.")
        else:
            # CLEAN THE KEY (Remove any hidden spaces)
            CLEAN_KEY = groq_input.strip()
            
            headers = {
                "Authorization": f"Bearer {CLEAN_KEY}",
                "Content-Type": "application/json"
            }
            
            # Using the most stable Llama model
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a PhD Clinical Microbiologist. Write in formal Lancet style. Italicize species names (e.g. S Typhi)."},
                    {"role": "user", "content": f"Continue this text: {user_text}"}
                ]
            }
            
            try:
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                
                if response.status_code == 200:
                    st.info(response.json()['choices'][0]['message']['content'])
                elif response.status_code == 401:
                    st.error("❌ 401 Error: Your Groq key is invalid. Please go to console.groq.com, delete your old key, and create a brand new one.")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

# --- TAB 2: RESEARCH ---
with tab2:
    st.subheader("Semantic Scholar Literature Search")
    query = st.text_input("Search keywords...")
    if st.button("Search"):
        res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,url,year,abstract").json()
        if 'data' in res:
            for p in res['data']:
                st.markdown(f"**{p['title']} ({p['year']})**")
                st.caption(f"[Link]({p['url']})")
                st.write(p.get('abstract', 'No abstract')[:200] + "...")

# --- TAB 3: INTEGRITY ---
with tab3:
    st.subheader("AI Detection")
    check_text = st.text_area("Paste text to check...")
    if st.button("Check Accuracy"):
        if not hf_input:
            st.error("Paste HF Token in sidebar.")
        else:
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {hf_input.strip()}"}
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": check_text})
                output = response.json()
                # Detection result
                ai_score = output[0]
                val = next(item for item in ai_score if item["label"] == "ChatGPT")["score"]
                st.metric("AI Probability", f"{round(val * 100, 2)}%")
            except:
                st.warning("Model is loading. Wait 10 seconds and try again.")
