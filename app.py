import streamlit as st
import requests

st.set_page_config(page_title="Microbiology PhD Assistant", layout="wide")
st.title("🔬 Clinical Microbiology Research Suite")

# Sidebar for Free Keys
with st.sidebar:
    st.header("Settings")
    st.markdown("Get your free keys at: [Groq](https://console.groq.com) and [GPTZero](https://gptzero.me)")
    groq_key = st.text_input("Groq API Key (Auto-complete)", type="password")
    gz_key = st.text_input("GPTZero API Key (Integrity Check)", type="password")

tab1, tab2, tab3 = st.tabs(["📝 AI Writer", "🔎 Literature", "🛡️ Integrity"])

with tab1:
    st.subheader("Academic Writing & Polish")
    text = st.text_area("Write your draft here...", height=300)
    if st.button("Jenni AI: Auto-complete Next Paragraph"):
        if groq_key:
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            data = {"model": "llama3-8b-8192", "messages": [{"role": "system", "content": "You are a PhD in Microbiology. Use Lancet Microbe style."}, {"role": "user", "content": text}]}
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data).json()
            st.write("### Suggested Addition:")
            st.info(res['choices'][0]['message']['content'])
        else: st.error("Add Groq Key in Sidebar")

with tab2:
    st.subheader("Semantic Scholar Research")
    q = st.text_input("Search (e.g., S. Typhi XDR)")
    if st.button("Search"):
        data = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit=5&fields=title,url,year,abstract").json()
        for p in data.get('data', []):
            st.markdown(f"**{p['title']} ({p['year']})**  \n[View Paper]({p['url']})")
            st.caption(p['abstract'][:250] + "...")

with tab3:
    st.subheader("AI Detection (Turnitin-style)")
    check = st.text_area("Paste text to check...")
    if st.button("Run Check"):
        if gz_key:
            res = requests.post("https://api.gptzero.me/v2/predict/text", headers={"x-api-key": gz_key}, json={"document": check}).json()
            score = res['documents'][0]['completely_generated_prob']
            st.metric("AI Probability", f"{round(score*100, 2)}%")
        else: st.error("Add GPTZero Key in Sidebar")
