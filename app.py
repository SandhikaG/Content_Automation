
import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Content Generator", layout="wide")

st.title("🚀 AI Content Generator")

# 🔹 Task Type
task_type = st.selectbox("Task Type", ["create", "optimize"])

# 🔹 Inputs
if task_type == "create":
    topic = st.text_input("Topic", "Cloud Security Basics")
else:
    page_url = st.text_input("Page URL", "https://example.com")

primary_keyword = st.text_input("Primary Keyword", "cloud security")
secondary_keywords = st.text_input(
    "Secondary Keywords (comma separated)", 
    "cloud threats, cloud tools"
)

website_url = st.text_input("Website URL", "https://example.com")
key_services = st.text_input("Key Services (comma separated)", "Cloud Security, SIEM")
key_competitors = st.text_input("Competitors (comma separated)", "AWS, Palo Alto")

target_audience = st.text_input("Audience", "IT Leaders")

funnel_stage = st.selectbox("Funnel Stage", ["Awareness", "Consideration", "Decision"])
target_location = st.selectbox("Location", ["US", "India", "Worldwide"])
word_count = st.selectbox("Word Count", [1200, 1500, 2000])

page_type = st.selectbox("Page Type", ["Blog", "Product", "Listicle", "Use Case", "Success Story"])
page_objective = st.selectbox("Page Objective", ["Generate Leads", "Generate Traffic"])
brand_tone = st.selectbox("Brand Tone", ["Professional", "Conversational", "Authoritative"])

# 🔹 Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "article" not in st.session_state:
    st.session_state.article = ""

# 🔥 Brief history storage
if "brief_history" not in st.session_state:
    st.session_state.brief_history = {}

if "selected_brief" not in st.session_state:
    st.session_state.selected_brief = None

# 🔹 Build payload
def get_payload():
    payload = {
        "task_type": task_type,
        "primary_keyword": primary_keyword,
        "secondary_keywords": [k.strip() for k in secondary_keywords.split(",")],
        "target_audience": target_audience,
        "funnel_stage": funnel_stage,
        "target_location": target_location,
        "word_count": int(word_count),
        "page_type": page_type,
        "page_objective": page_objective,
        "brand_tone": brand_tone,
        "website_url": website_url,
        "key_services": [s.strip() for s in key_services.split(",")],
        "key_competitors": [c.strip() for c in key_competitors.split(",")]
    }

    if task_type == "create":
        payload["topic"] = topic
    else:
        payload["page_url"] = page_url

    return payload

# 🔹 Generate Brief Button
if st.button("📊 Generate Brief"):
    with st.spinner("Generating content brief..."):
        try:
            res = requests.post(
                f"{BACKEND_URL}/generate-brief",
                json=get_payload(),
                timeout=60
            )

            data = res.json()

            if data.get("success"):
                st.session_state.session_id = data["session_id"]

                # Store brief
                brief_id = f"Brief {len(st.session_state.brief_history) + 1}"
                st.session_state.brief_history[brief_id] = data["data"]
                st.session_state.selected_brief = brief_id

                # Reset article when new brief generated
                st.session_state.article = ""

                st.success("✅ Content Brief Generated")

            else:
                st.error(data.get("error", "Unknown error"))

        except Exception as e:
            st.error(f"❌ Request failed: {e}")

# 🔥 Brief Dropdown (Revisit Feature)
if st.session_state.brief_history:
    selected = st.selectbox(
        "📂 View Previous Briefs",
        list(st.session_state.brief_history.keys()),
        index=len(st.session_state.brief_history) - 1
    )

    st.session_state.selected_brief = selected

# 🔥 Display Brief (ALWAYS FIRST)
if st.session_state.selected_brief:
    st.subheader("📊 Content Brief")

    st.markdown(f"""
    <div style="padding:20px;border-radius:10px;background:#f5f7fa">
    {st.session_state.brief_history[st.session_state.selected_brief]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

# 🔹 Generate Article Button (BELOW BRIEF)
if st.session_state.session_id:
    if st.button("📝 Generate Article"):
        with st.spinner("Generating article..."):
            try:
                res = requests.get(
                    f"{BACKEND_URL}/generate-article/{st.session_state.session_id}",
                    timeout=120
                )

                data = res.json()

                if data.get("success"):
                    st.session_state.article = data["article"]
                    st.success("✅ Article Generated")

                else:
                    st.error(data.get("error", "Unknown error"))

            except Exception as e:
                st.error(f"❌ Request failed: {e}")

# 🔹 Show Article BELOW
if st.session_state.article:
    st.info("💡 Scroll up to compare with the brief")

    st.subheader("📝 Full Article")

    st.markdown(f"""
    <div style="padding:20px;border-radius:10px;background:#ffffff">
    {st.session_state.article}
    </div>
    """, unsafe_allow_html=True)

