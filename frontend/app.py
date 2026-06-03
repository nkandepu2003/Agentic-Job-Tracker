# app.py
# AI Agentic Job Tracker Dashboard
# Dark Purple AI Research Lab Theme

import os
import sys

# ─────────────────────────────────────
# LANGSMITH MONITORING SETUP
# MUST BE FIRST - before any LangChain imports
# ─────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

langsmith_key = os.getenv("LANGCHAIN_API_KEY", "")
if langsmith_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "agentic-job-tracker"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_key
    print("✅ LangSmith tracing enabled for project: agentic-job-tracker")
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    print("⚠️ LangSmith key not found. Tracing disabled.")

# ─────────────────────────────────────
# LANGSMITH DEBUG (temporary - remove after confirmed working)
# ─────────────────────────────────────
try:
    import langsmith
    client = langsmith.Client()
    projects = list(client.list_projects())
    print(f"✅ LangSmith connected! Projects found: {[p.name for p in projects]}")
except Exception as e:
    print(f"❌ LangSmith connection failed: {str(e)}")

# ─────────────────────────────────────
# ALL OTHER IMPORTS
# ─────────────────────────────────────
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

from database.models import get_db, JobApplication, delete_application
from frontend.theme import apply_dark_theme, handle_resume_upload

# ─────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────
st.set_page_config(
    page_title="AI Job Tracker",
    page_icon="💼",
    layout="wide"
)

# Apply dark theme first
apply_dark_theme()

# ─────────────────────────────────────
# RESUME UPLOAD
# ─────────────────────────────────────
resume_path = handle_resume_upload()
if resume_path:
    st.session_state["resume_path"] = resume_path

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────
st.sidebar.markdown(
    '<p style="color:#AFA9EC; font-size:16px; font-weight:500; margin-bottom:16px;">💼 AI Job Tracker</p>',
    unsafe_allow_html=True
)

st.sidebar.markdown(
    '<p style="color:#6b6783; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">TECH STACK</p>',
    unsafe_allow_html=True
)

stack_items = [
    ("LangGraph", "Agentic AI"),
    ("Llama 3 70B", "via Groq"),
    ("ChromaDB", "Vector DB"),
    ("Sentence Transformers", "BERT"),
    ("LangChain", "RAG"),
    ("SerpAPI", "Job Search"),
    ("LangSmith", "Monitoring"),
]

for name, tag in stack_items:
    st.sidebar.markdown(
        f'<div style="display:flex; justify-content:space-between; align-items:center; padding:5px 0; border-bottom:0.5px solid #2d2b3d;"><span style="font-size:12px; color:#e2d9f3;">{name}</span><span style="font-size:10px; color:#AFA9EC; background:#1e1a2e; padding:2px 8px; border-radius:20px; border:0.5px solid #534AB7;">{tag}</span></div>',
        unsafe_allow_html=True
    )

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown(
    '<p style="color:#6b6783; font-size:10px; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">ADD APPLICATION</p>',
    unsafe_allow_html=True
)

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
        st.sidebar.success("✅ Saved!")
        st.rerun()
    else:
        st.sidebar.error("❌ Fill Company and Job Title!")

# ─────────────────────────────────────
# HEADER
# ─────────────────────────────────────
st.markdown(
    '<h1 style="color:#e2d9f3; font-size:26px; font-weight:500; margin-bottom:4px;">AI Agentic Job Tracker</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="color:#6b6783; font-size:14px; margin-bottom:12px;">Your complete AI-powered job hunting platform</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="margin-bottom:1.5rem;">'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px;">LangGraph</span>'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px;">Llama 3 70B</span>'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px;">RAG Pipeline</span>'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px;">ChromaDB</span>'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px; margin-right:6px;">Groq Inference</span>'
    '<span style="background:#1e1a2e; border:0.5px solid #534AB7; color:#AFA9EC; font-size:11px; padding:3px 10px; border-radius:20px;">LangSmith</span>'
    '</div>',
    unsafe_allow_html=True
)

# ─────────────────────────────────────
# GET DATA
# ─────────────────────────────────────
db = get_db()
applications = db.query(JobApplication).all()
db.close()

total = len(applications)
interviews = len([a for a in applications if "Interview" in a.status])
offers = len([a for a in applications if a.status == "Offer Received"])
rejected = len([a for a in applications if a.status == "Rejected"])

# ─────────────────────────────────────
# STATS
# ─────────────────────────────────────
st.markdown(
    '<p style="color:#AFA9EC; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">JOB HUNT STATS</p>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

def stat_card(value, label, color, pct=None):
    bar = f'<div style="height:3px; background:#2d2b3d; border-radius:2px; margin-top:8px;"><div style="width:{pct or min(value*5,100)}%; height:100%; background:{color}; border-radius:2px;"></div></div>'
    return f'''<div style="background:#13111c; border:0.5px solid #2d2b3d; border-top:2px solid {color}; border-radius:10px; padding:1rem; text-align:center;">
    <div style="font-size:28px; font-weight:500; color:#e2d9f3;">{value}</div>
    <div style="font-size:12px; color:#6b6783; margin-top:4px;">{label}</div>
    {bar}</div>'''

with col1:
    st.markdown(stat_card(total, "Total Applied", "#7F77DD"), unsafe_allow_html=True)
with col2:
    pct = round(interviews/total*100) if total > 0 else 0
    st.markdown(stat_card(interviews, f"Interviews · {pct}%", "#1D9E75", pct), unsafe_allow_html=True)
with col3:
    pct = round(offers/total*100) if total > 0 else 0
    st.markdown(stat_card(offers, f"Offers · {pct}%", "#639922", pct), unsafe_allow_html=True)
with col4:
    pct = round(rejected/total*100) if total > 0 else 0
    st.markdown(stat_card(rejected, f"Rejected · {pct}%", "#E24B4A", pct), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────
# LANGGRAPH PIPELINE
# ─────────────────────────────────────
st.markdown(
    '<p style="color:#AFA9EC; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">LANGGRAPH PIPELINE — Smart Apply</p>',
    unsafe_allow_html=True
)

pipe_col1, pipe_arr1, pipe_col2, pipe_arr2, pipe_col3, pipe_arr3, pipe_col4 = st.columns([3, 1, 3, 1, 3, 1, 3])

with pipe_col1:
    st.markdown(
        '<div style="background:#0a1a14; border:0.5px solid #1D9E75; border-radius:10px; padding:12px; text-align:center;"><div style="color:#5DCAA5; font-size:20px;">✓</div><div style="color:#5DCAA5; font-size:12px; font-weight:500; margin-top:4px;">Score Job</div><div style="color:#6b6783; font-size:10px; margin-top:2px;">Sentence Transformers</div></div>',
        unsafe_allow_html=True
    )
with pipe_arr1:
    st.markdown('<div style="text-align:center; padding-top:20px; color:#534AB7; font-size:20px;">→</div>', unsafe_allow_html=True)
with pipe_col2:
    st.markdown(
        '<div style="background:#1e1a2e; border:0.5px solid #7F77DD; border-radius:10px; padding:12px; text-align:center;"><div style="color:#AFA9EC; font-size:20px;">⟳</div><div style="color:#AFA9EC; font-size:12px; font-weight:500; margin-top:4px;">Tailor Resume</div><div style="color:#6b6783; font-size:10px; margin-top:2px;">Llama 3 + LangChain</div></div>',
        unsafe_allow_html=True
    )
with pipe_arr2:
    st.markdown('<div style="text-align:center; padding-top:20px; color:#534AB7; font-size:20px;">→</div>', unsafe_allow_html=True)
with pipe_col3:
    st.markdown(
        '<div style="background:#13111c; border:0.5px solid #2d2b3d; border-radius:10px; padding:12px; text-align:center;"><div style="color:#6b6783; font-size:20px;">○</div><div style="color:#6b6783; font-size:12px; font-weight:500; margin-top:4px;">Cover Letter</div><div style="color:#6b6783; font-size:10px; margin-top:2px;">Llama 3 + LangChain</div></div>',
        unsafe_allow_html=True
    )
with pipe_arr3:
    st.markdown('<div style="text-align:center; padding-top:20px; color:#534AB7; font-size:20px;">→</div>', unsafe_allow_html=True)
with pipe_col4:
    st.markdown(
        '<div style="background:#13111c; border:0.5px solid #2d2b3d; border-radius:10px; padding:12px; text-align:center;"><div style="color:#6b6783; font-size:20px;">○</div><div style="color:#6b6783; font-size:12px; font-weight:500; margin-top:4px;">Log Application</div><div style="color:#6b6783; font-size:10px; margin-top:2px;">Supabase PostgreSQL</div></div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────
# ACTIVITY LOG
# ─────────────────────────────────────
st.markdown(
    '<p style="color:#AFA9EC; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">AGENT ACTIVITY LOG</p>',
    unsafe_allow_html=True
)

if applications:
    recent = sorted(
        applications,
        key=lambda x: x.date_applied or datetime.min,
        reverse=True
    )[:4]

    for app in recent:
        days = (datetime.now() - app.date_applied).days if app.date_applied else 0
        time_str = f"{days}d ago" if days > 0 else "Today"
        icon = "🤖" if "Auto" in (app.notes or "") else "📝"
        st.markdown(
            f'<div style="background:#1a1727; border:0.5px solid #2d2b3d; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;"><div><span style="font-size:13px; font-weight:500; color:#e2d9f3;">{icon} Applied to {app.company} — {app.job_title}</span><br><span style="font-size:11px; color:#6b6783;">Status: {app.status} · {app.notes or "Manually added"}</span></div><span style="font-size:11px; color:#6b6783; white-space:nowrap; margin-left:12px;">{time_str}</span></div>',
            unsafe_allow_html=True
        )
else:
    st.markdown(
        '<div style="background:#1a1727; border:0.5px solid #2d2b3d; border-radius:8px; padding:16px; text-align:center;"><span style="color:#6b6783; font-size:13px;">No activity yet. Add your first application!</span></div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────
# ALL APPLICATIONS WITH DELETE + UPDATE
# ─────────────────────────────────────
st.markdown(
    '<p style="color:#AFA9EC; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">ALL APPLICATIONS</p>',
    unsafe_allow_html=True
)

if applications:
    for app in applications:
        date_str = app.date_applied.strftime("%d %b %Y") if app.date_applied else "N/A"

        with st.expander(f"🏢 {app.company} — {app.job_title} | {app.status}"):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(f"📅 Applied: {date_str}")
                st.write(f"📍 Location: {app.location or 'N/A'}")

            with col2:
                st.write(f"💰 Salary: {app.salary or 'N/A'}")
                st.write(f"📊 Status: {app.status}")

            with col3:
                new_status = st.selectbox(
                    "Update:",
                    ["Applied", "Interview Scheduled",
                     "Interview Done", "Offer Received",
                     "Rejected", "Withdrawn"],
                    index=["Applied", "Interview Scheduled",
                           "Interview Done", "Offer Received",
                           "Rejected", "Withdrawn"].index(app.status)
                    if app.status in ["Applied", "Interview Scheduled",
                                      "Interview Done", "Offer Received",
                                      "Rejected", "Withdrawn"] else 0,
                    key=f"status_{app.id}"
                )

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("✏️ Update", key=f"update_{app.id}"):
                        db = get_db()
                        db_app = db.query(JobApplication).filter(
                            JobApplication.id == app.id).first()
                        if db_app:
                            db_app.status = new_status
                            db.commit()
                        db.close()
                        st.success("✅ Updated!")
                        st.rerun()

                with bcol2:
                    if st.button("🗑️ Delete", key=f"delete_{app.id}"):
                        delete_application(app.id)
                        st.success("✅ Deleted!")
                        st.rerun()

            if app.notes:
                st.caption(f"📝 {app.notes}")
            if app.job_url and app.job_url != "N/A":
                st.link_button("🔗 View Job", app.job_url)
else:
    st.info("👆 Add your first application using the sidebar!")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────
# STATUS FILTER
# ─────────────────────────────────────
st.markdown(
    '<p style="color:#AFA9EC; font-size:11px; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">FILTER BY STATUS</p>',
    unsafe_allow_html=True
)

selected_status = st.selectbox(
    "Show applications:",
    ["All", "Applied", "Interview Scheduled",
     "Interview Done", "Offer Received",
     "Rejected", "Withdrawn"]
)

if selected_status != "All" and applications:
    filtered = [a for a in applications if a.status == selected_status]
    if filtered:
        data_filtered = []
        for app in filtered:
            data_filtered.append({
                "Company": app.company,
                "Job Title": app.job_title,
                "Status": app.status,
                "Date Applied": app.date_applied.strftime("%d %b %Y") if app.date_applied else "N/A",
                "Notes": app.notes or "N/A"
            })
        st.dataframe(pd.DataFrame(data_filtered), use_container_width=True)
    else:
        st.info(f"No applications with status: {selected_status}")