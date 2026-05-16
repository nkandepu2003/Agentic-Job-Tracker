# app.py
# This is your Job Tracker Dashboard
# The thing you actually SEE and click on

import streamlit as st
import pandas as pd
import sys
import os
import re
import io

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db, JobApplication
from datetime import datetime

# ─────────────────────────────────────
# PAGE SETTINGS
# ─────────────────────────────────────
st.set_page_config(
    page_title="AI Job Tracker",
    page_icon="💼",
    layout="wide"
)

# ─────────────────────────────────────
# TITLE
# ─────────────────────────────────────
st.title("💼 AI Agentic Job Tracker")
st.markdown("Track every application. Never miss a follow up.")

# ─────────────────────────────────────
# SIDEBAR - Add New Job Application
# ─────────────────────────────────────
st.sidebar.title("➕ Add New Application")

company = st.sidebar.text_input("Company Name")
job_title = st.sidebar.text_input("Job Title")
job_url = st.sidebar.text_input("Job URL (optional)")
location = st.sidebar.text_input("Location (optional)")
salary = st.sidebar.text_input("Salary Range (optional)")
notes = st.sidebar.text_area("Notes (optional)")

status = st.sidebar.selectbox(
    "Status",
    ["Applied", "Interview Scheduled",
     "Interview Done", "Offer Received",
     "Rejected", "Withdrawn"]
)

if st.sidebar.button("💾 Save Application"):
    if company and job_title:
        db = get_db()
        new_application = JobApplication(
            company=company,
            job_title=job_title,
            job_url=job_url,
            location=location,
            salary=salary,
            notes=notes,
            status=status,
            date_applied=datetime.now()
        )
        db.add(new_application)
        db.commit()
        db.close()
        st.sidebar.success("✅ Application saved!")
    else:
        st.sidebar.error(
            "❌ Please fill Company and Job Title!")

# ─────────────────────────────────────
# MAIN AREA - Show All Applications
# ─────────────────────────────────────
db = get_db()
applications = db.query(JobApplication).all()
db.close()

# ─────────────────────────────────────
# STATS ROW
# ─────────────────────────────────────
st.subheader("📊 Your Job Hunt Stats")

col1, col2, col3, col4 = st.columns(4)

total = len(applications)
interviews = len([a for a in applications
                  if "Interview" in a.status])
offers = len([a for a in applications
              if a.status == "Offer Received"])
rejected = len([a for a in applications
                if a.status == "Rejected"])

with col1:
    st.metric("📨 Total Applied", total)
with col2:
    st.metric("🎯 Interviews", interviews)
with col3:
    st.metric("🎉 Offers", offers)
with col4:
    st.metric("❌ Rejected", rejected)

st.divider()

# ─────────────────────────────────────
# APPLICATIONS TABLE
# ─────────────────────────────────────
st.subheader("📋 All Applications")

if applications:
    data = []
    for app in applications:
        data.append({
            "Company": app.company,
            "Job Title": app.job_title,
            "Status": app.status,
            "Location": app.location or "N/A",
            "Salary": app.salary or "N/A",
            "Date Applied": app.date_applied.strftime(
                "%d %b %Y"
            ) if app.date_applied else "N/A",
            "Notes": app.notes or "N/A"
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.info(
        "👆 Add your first job application using the sidebar!")

st.divider()

# ─────────────────────────────────────
# STATUS FILTER
# ─────────────────────────────────────
st.subheader("🔍 Filter by Status")

selected_status = st.selectbox(
    "Show applications with status:",
    ["All", "Applied", "Interview Scheduled",
     "Interview Done", "Offer Received",
     "Rejected", "Withdrawn"]
)

if selected_status != "All" and applications:
    filtered = [a for a in applications
                if a.status == selected_status]
    if filtered:
        data_filtered = []
        for app in filtered:
            data_filtered.append({
                "Company": app.company,
                "Job Title": app.job_title,
                "Status": app.status,
                "Date Applied": app.date_applied.strftime(
                    "%d %b %Y"
                ) if app.date_applied else "N/A",
                "Notes": app.notes or "N/A"
            })
        st.dataframe(
            pd.DataFrame(data_filtered),
            use_container_width=True
        )
    else:
        st.info(
            f"No applications with status: {selected_status}")

st.divider()

# ─────────────────────────────────────
# RESUME TAILOR AGENT SECTION
# ─────────────────────────────────────
st.subheader("🤖 AI Resume Tailor Agent")
st.markdown(
    "Paste a job description and AI will tailor your resume instantly!")

job_description = st.text_area(
    "Paste Job Description Here:",
    height=200,
    placeholder="Copy and paste the full job description here..."
)

if st.button("✨ Tailor My Resume with AI"):
    if job_description:
        with st.spinner(
            "🤖 AI is tailoring your resume... This takes 10-30 seconds..."
        ):
            try:
                from agents.tailor_agent import run_tailor_agent
                resume_path = "resume.pdf"
                tailored_resume, error = run_tailor_agent(
                    resume_path,
                    job_description
                )

                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.success(
                        "✅ Your tailored resume is ready!")

                    # Show formatted preview
                    st.subheader("👀 Preview (Formatted)")
                    st.markdown(tailored_resume)

                    st.divider()

                    # Two download options
                    col1, col2 = st.columns(2)

                    with col1:
                        # Download as plain text
                        st.download_button(
                            label="⬇️ Download as TXT",
                            data=tailored_resume,
                            file_name="tailored_resume.txt",
                            mime="text/plain"
                        )

                    with col2:
                        # Download as Word document
                        if st.button("📄 Download as Word Doc"):
                            try:
                                from docx import Document

                                doc = Document()

                                # Process each line
                                for line in tailored_resume.split('\n'):
                                    if not line.strip():
                                        doc.add_paragraph('')
                                        continue

                                    # Check if bullet point
                                    if line.strip().startswith('*') and not line.strip().startswith('**'):
                                        p = doc.add_paragraph(
                                            style='List Bullet')
                                        line = line.strip().lstrip(
                                            '*').strip()
                                    else:
                                        p = doc.add_paragraph()

                                    # Handle bold text (**)
                                    parts = re.split(
                                        r'\*\*(.*?)\*\*', line)
                                    for i, part in enumerate(parts):
                                        if i % 2 == 0:
                                            p.add_run(part)
                                        else:
                                            run = p.add_run(part)
                                            run.bold = True

                                # Save to bytes
                                doc_bytes = io.BytesIO()
                                doc.save(doc_bytes)
                                doc_bytes.seek(0)

                                st.download_button(
                                    label="⬇️ Click to Save Word File",
                                    data=doc_bytes.getvalue(),
                                    file_name="tailored_resume.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                                st.success(
                                    "✅ Word document ready!")

                            except Exception as e:
                                st.error(
                                    f"❌ Error creating Word doc: {str(e)}")

            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")
    else:
        st.warning(
            "⚠️ Please paste a job description first!")