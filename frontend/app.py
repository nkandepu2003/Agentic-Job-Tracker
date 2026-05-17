# app.py - Main Dashboard
import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db, JobApplication
from datetime import datetime

st.set_page_config(
    page_title="AI Job Tracker",
    page_icon="💼",
    layout="wide"
)

# ─────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────
st.title("💼 AI Agentic Job Tracker")
st.markdown(
    "Your complete AI-powered job hunting platform. "
    "Built with LangChain, Groq Llama 3, and Streamlit.")

st.divider()

# ─────────────────────────────────────
# AGENT CARDS
# ─────────────────────────────────────
st.subheader("🚀 Your AI Agents")

card_col1, card_col2, card_col3 = st.columns(3)

with card_col1:
    st.info(
        "🤖 **Resume Tailor**\n\n"
        "Rewrites your resume to match "
        "any job description using Llama 3 AI"
    )
    st.info(
        "✉️ **Cover Letter**\n\n"
        "Writes personalized cover letters "
        "for any company and role"
    )

with card_col2:
    st.success(
        "🔍 **Job Scout**\n\n"
        "Searches 7 job variations, scores "
        "against your resume, removes duplicates"
    )
    st.success(
        "📧 **Follow Up**\n\n"
        "Finds old applications and drafts "
        "professional follow-up emails"
    )

with card_col3:
    st.warning(
        "🎯 **Interview Prep**\n\n"
        "Generates technical, behavioral, "
        "and system design questions per company"
    )
    st.warning(
        "📊 **Dashboard**\n\n"
        "Track all applications, stats, "
        "and filter by status"
    )

st.divider()

# ─────────────────────────────────────
# SIDEBAR - Add Application
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
# STATS ROW
# ─────────────────────────────────────
st.subheader("📊 Your Job Hunt Stats")

db = get_db()
applications = db.query(JobApplication).all()
db.close()

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
        "👆 Add your first job application "
        "using the sidebar on the left!")

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
            f"No applications with status: "
            f"{selected_status}")