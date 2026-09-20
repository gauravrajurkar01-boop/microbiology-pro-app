import streamlit as st
import requests

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")
st.title("🔬 Clinical Microbiology Research Suite")

# Sidebar for Free Keys
with st.sidebar:
    st.header("Settings")
    st.markdown("1. Get Groq Key: [console.groq.com](https://console.groq.com)")
    st.markdown("2. Get HF Token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)")
    groq_key = st.text_input("Groq API Key (Auto-complete)", type="password")
    hf_token = st.text_input("Hugging Face Token (AI Detection)", type="password")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer", "🔎 Literature", "🛡️ Integrity"])

with tab1:
    st.subheader("Academic Writing & Polish")
    text = st.text_area("Write your draft here...", height=300)
    if st.button("Jenni AI: Auto-complete Next Paragraph"):
        if groq_key:
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            data = {"model": "llama3-8b-8192", "messages": [
                {"role": "system", "content": "You are an expert PhD in Clinical Microbiology. Use Lancet Microbe style. Ensure correct binomial nomenclature (e.g. S Typhi in italics)."},
                {"role": "user", "content": text}
            ]}
            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data).json()
                st.write("### Suggested Addition:")
                st.info(res['choices'][0]['message']['content'])
            except:
                st.error("Error connecting to Groq. Check your key.")
        else: st.error("Add Groq Key in Sidebar")

with tab2:
    st.subheader("Semantic Scholar Research")
    q = st.text_input("Search (e.g., S. Typhi XDR Pakistan)")
    if st.button("Search"):
        res = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=5&fields=title,url,year,abstract")
        data = res.json()
        for p in data.get('data', []):
            st.markdown(f"**{p['title']} ({p['year']})**  \n[View Paper]({p['url']})")
            st.caption(p['abstract'][:250] + "...")

with tab3:
    st.subheader("AI Detection (Hugging Face Free API)")
    check = st.text_area("Paste text to check for AI content...", height=200)
    if st.button("Run Integrity Check"):
        if hf_token:
            # Using the RoBERTa-base detector (highly accurate for academic text)
            API_URL = "https://api-inference.huggingface.co/models/Hello-SimpleAI/chatgpt-detector-roberta"
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            response = requests.post(API_URL, headers=headers, json={"inputs": check})
            result = response.json()
            
            try:
                # The model returns nested lists. We look for the ChatGPT score.
                ai_data = result[0]
                ai_score = next(item for item in ai_data if item["label"] == "ChatGPT")["score"]
                st.metric("AI Probability", f"{round(ai_score * 100, 2)}%")
                if ai_score > 0.5:
                    st.warning("High AI Probability. Consider manual rewriting.")
                else:
                    st.success("Text appears Human-Written.")
            except:
                st.error("Model is waking up. Please wait 30 seconds and try again.")
        else: st.error("Add Hugging Face Token in Sidebar")
