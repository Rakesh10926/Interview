import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

st.set_page_config(
    page_title="AI Interview Preparation Agent",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Interview Preparation Agent")
st.write("Your personal AI-powered interview preparation assistant.")

api_key = os.environ.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.8-flash")
else:
    model = None

st.sidebar.header("Interview Settings")
role = st.sidebar.text_input("Target Job Role", "Software Developer")
level = st.sidebar.selectbox(
    "Experience Level",
    ["Fresher", "Beginner", "Intermediate", "Experienced"]
)
interview_type = st.sidebar.selectbox(
    "Interview Type",
    ["Technical", "HR", "Mixed"]
)

st.subheader("📄 Resume Analysis")
resume = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"]
)

resume_text = ""

if resume:
    try:
        reader = PdfReader(resume)
        resume_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )
        st.success("Resume uploaded successfully!")
    except Exception as e:
        st.error(f"Could not read the PDF: {e}")

job_description = st.text_area(
    "Job Description",
    placeholder="Paste the job description here..."
)

if st.button("Generate Interview Preparation Report"):
    if not model:
        st.error("Please configure your Gemini API key.")
    elif not resume_text and not job_description.strip():
        st.warning("Upload a resume or enter a job description.")
    else:
        prompt = f"""
You are an expert interview coach.

Target job role: {role}
Experience level: {level}
Interview type: {interview_type}

Resume:
{resume_text[:12000]}

Job description:
{job_description[:6000]}

Generate:
1. Candidate profile summary.
2. Key skills identified.
3. Strengths and missing skills.
4. Ten personalized interview questions.
5. Suggested answers to each question.
6. Important preparation topics.
7. Tips to improve interview performance.

Use clear headings and practical advice.
"""

        with st.spinner("Generating your report..."):
            try:
                response = model.generate_content(prompt)
                report = response.text

                st.session_state["report"] = report

            except Exception as e:
                st.error(f"AI generation failed: {e}")

if "report" in st.session_state:
    st.subheader("📊 Interview Preparation Report")
    st.markdown(st.session_state["report"])

    st.download_button(
        "Download Report",
        st.session_state["report"],
        file_name="interview_report.txt",
        mime="text/plain"
    )
