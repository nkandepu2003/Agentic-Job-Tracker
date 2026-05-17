# pages/1_Resume_Tailor.py
import streamlit as st
import sys
import os
import re
import io

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Resume Tailor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Resume Tailor Agent")
st.markdown(
    "Paste a job description and AI will "
    "tailor your resume instantly!")

st.info(
    "💡 Your resume (resume.pdf) is stored "
    "in the project folder. "
    "AI reads it automatically!")

job_description = st.text_area(
    "Paste Job Description Here:",
    height=250,
    placeholder="Copy and paste the full job description here..."
)

if st.button("✨ Tailor My Resume with AI",
             use_container_width=True):
    if job_description:
        with st.spinner(
            "🤖 AI is tailoring your resume... "
            "10-30 seconds..."
        ):
            try:
                from agents.tailor_agent import (
                    run_tailor_agent)
                resume_path = "resume.pdf"
                tailored_resume, error = run_tailor_agent(
                    resume_path, job_description)

                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.success(
                        "✅ Your tailored resume is ready!")
                    st.subheader("👀 Preview")
                    st.markdown(tailored_resume)
                    st.divider()

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="⬇️ Download as TXT",
                            data=tailored_resume,
                            file_name="tailored_resume.txt",
                            mime="text/plain"
                        )
                    with col2:
                        if st.button("📄 Download as Word"):
                            try:
                                from docx import Document
                                doc = Document()
                                for line in tailored_resume.split('\n'):
                                    if not line.strip():
                                        doc.add_paragraph('')
                                        continue
                                    if (line.strip().startswith('*') and
                                            not line.strip().startswith('**')):
                                        p = doc.add_paragraph(
                                            style='List Bullet')
                                        line = line.strip().lstrip(
                                            '*').strip()
                                    else:
                                        p = doc.add_paragraph()
                                    parts = re.split(
                                        r'\*\*(.*?)\*\*', line)
                                    for i, part in enumerate(parts):
                                        if i % 2 == 0:
                                            p.add_run(part)
                                        else:
                                            run = p.add_run(part)
                                            run.bold = True
                                doc_bytes = io.BytesIO()
                                doc.save(doc_bytes)
                                doc_bytes.seek(0)
                                st.download_button(
                                    label="⬇️ Save Word File",
                                    data=doc_bytes.getvalue(),
                                    file_name="tailored_resume.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="word_doc"
                                )
                            except Exception as e:
                                st.error(f"❌ {str(e)}")

            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")
    else:
        st.warning("⚠️ Please paste a job description first!")