# pages/3_Job_Scout.py
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Job Scout",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Smart Job Scout Agent")
st.markdown(
    "Searches 7 job variations, scores against "
    "your resume, shows matching keywords!")

# Load previous search preferences
try:
    from agents.scout_agent import load_search_preferences
    prefs = load_search_preferences()
    recent_roles = prefs.get("recent_roles", [])
    recent_locations = prefs.get("recent_locations", [])
except Exception:
    recent_roles = []
    recent_locations = []

if recent_roles:
    st.info(
        f"💡 Recent searches: "
        f"{', '.join(recent_roles[:3])}")

col1, col2 = st.columns(2)

with col1:
    default_role = recent_roles[0] if recent_roles else ""
    job_role = st.text_input(
        "Job Role:",
        value=default_role,
        placeholder="e.g. Machine Learning Engineer"
    )
    if recent_roles:
        selected_role = st.selectbox(
            "Or pick from recent searches:",
            [""] + recent_roles,
            key="role_select"
        )
        if selected_role:
            job_role = selected_role

with col2:
    default_location = (
        recent_locations[0] if recent_locations else "")
    job_location = st.text_input(
        "Location:",
        value=default_location,
        placeholder="e.g. New York or Remote"
    )
    if recent_locations:
        selected_location = st.selectbox(
            "Or pick from recent locations:",
            [""] + recent_locations,
            key="location_select"
        )
        if selected_location:
            job_location = selected_location

keywords_input = st.text_input(
    "Filter by keywords (optional, comma separated):",
    placeholder="e.g. Python, LangChain, Remote"
)

show_new_only = st.checkbox(
    "Show only NEW jobs (hide previously seen)",
    value=False
)

if st.button("🔍 Find Best Matching Jobs",
             use_container_width=True):
    if job_role and job_location:
        with st.spinner(
            "🔍 Searching 7 job variations... "
            "30-60 seconds..."
        ):
            try:
                from agents.scout_agent import (
                    run_scout_agent,
                    format_posted_time
                )
                from database.models import (
                    get_db, JobApplication)

                keywords = None
                if keywords_input:
                    keywords = [
                        k.strip()
                        for k in keywords_input.split(",")
                    ]

                jobs, error = run_scout_agent(
                    job_role,
                    job_location,
                    keywords=keywords,
                    show_new_only=show_new_only,
                    pdf_path="resume.pdf"
                )

                if error:
                    st.error(f"❌ Error: {error}")
                elif not jobs:
                    st.warning("⚠️ No jobs found!")
                else:
                    new_count = len(
                        [j for j in jobs
                         if j.get("is_new", True)])
                    st.success(
                        f"✅ Found {len(jobs)} jobs "
                        f"({new_count} new)!")

                    for i, job in enumerate(jobs):
                        score = job.get("match_score", 0)
                        matching = job.get(
                            "matching_keywords", [])
                        missing = job.get(
                            "missing_keywords", [])

                        if score >= 80:
                            score_emoji = "🟢"
                            score_label = "Excellent Match"
                        elif score >= 65:
                            score_emoji = "🟡"
                            score_label = "Good Match"
                        else:
                            score_emoji = "🔴"
                            score_label = "Low Match"

                        is_new = job.get("is_new", True)
                        new_badge = "🆕 " if is_new else "👀 "
                        posted_fmt = format_posted_time(
                            job.get("posted", "N/A"))

                        with st.expander(
                            f"{new_badge}🏢 {job['company']} "
                            f"— {job['title']} | "
                            f"{score_emoji} {score}% "
                            f"{score_label}"
                        ):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(
                                    f"📍 **Location:** "
                                    f"{job['location']}")
                                st.write(
                                    f"⏰ **Posted:** "
                                    f"{posted_fmt}")
                            with col2:
                                st.write(
                                    f"💰 **Salary:** "
                                    f"{job['salary']}")
                                st.write(
                                    f"🎯 **Match:** {score}%")
                            with col3:
                                if job['apply_link'] != 'N/A':
                                    st.link_button(
                                        "🚀 Apply Now",
                                        job['apply_link']
                                    )

                            st.progress(
                                min(score / 100, 1.0),
                                text=f"Resume Match: {score}%"
                            )

                            kw_col1, kw_col2 = st.columns(2)
                            with kw_col1:
                                if matching:
                                    st.success(
                                        "✅ **Keywords you have:**\n" +
                                        " • ".join(matching))
                            with kw_col2:
                                if missing:
                                    st.error(
                                        "❌ **Missing keywords:**\n" +
                                        " • ".join(missing))
                                    st.caption(
                                        "💡 Add these to your resume!")

                            st.write("**📋 Description:**")
                            st.write(job['description'])

                            if st.button(
                                "➕ Add to Tracker",
                                key=f"add_{i}"
                            ):
                                db = get_db()
                                new_app = JobApplication(
                                    company=job['company'],
                                    job_title=job['title'],
                                    job_url=job['apply_link'],
                                    location=job['location'],
                                    salary=job['salary'],
                                    status="Applied"
                                )
                                db.add(new_app)
                                db.commit()
                                db.close()
                                st.success(
                                    f"✅ Added to tracker!")

            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")
    else:
        st.warning("⚠️ Please fill Job Role and Location!")