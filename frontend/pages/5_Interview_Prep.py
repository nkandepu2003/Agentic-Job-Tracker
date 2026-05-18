# pages/5_Interview_Prep.py
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Interview Prep",
    page_icon="🎯",
    layout="wide"
)

from frontend.theme import apply_dark_theme
apply_dark_theme()

st.title("🎯 AI Interview Prep Agent")
st.markdown(
    "Enter company and role — AI generates "
    "specific interview questions and tips!")

col1, col2 = st.columns(2)

with col1:
    company = st.text_input(
        "Company Name:",
        placeholder="e.g. Google, Amazon, Microsoft"
    )

with col2:
    job_role = st.text_input(
        "Job Role:",
        placeholder="e.g. ML Engineer, Data Scientist"
    )

job_description = st.text_area(
    "Job Description (optional but recommended):",
    height=150,
    placeholder="Paste job description for more specific questions..."
)

if st.button("🎯 Generate Interview Questions",
             use_container_width=True,
             key="generate_btn"):
    if company and job_role:
        with st.spinner(
            "🎯 Generating interview questions... "
            "30-60 seconds..."
        ):
            try:
                from agents.interview_prep_agent import (
                    run_interview_prep_agent)

                results, error = run_interview_prep_agent(
                    company, job_role, job_description)

                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.success(
                        f"✅ Interview prep ready for "
                        f"{company} — {job_role}!")

                    tab1, tab2, tab3, tab4 = st.tabs([
                        "💻 Technical",
                        "🤝 Behavioral",
                        "🏗️ System Design",
                        "💡 Company Tips"
                    ])

                    with tab1:
                        st.subheader("💻 Technical Questions")
                        st.markdown(results["technical"])
                        st.download_button(
                            label="⬇️ Download",
                            data=results["technical"],
                            file_name=f"{company}_technical.txt",
                            mime="text/plain",
                            key="tech_dl"
                        )

                    with tab2:
                        st.subheader("🤝 Behavioral Questions")
                        st.markdown(results["behavioral"])
                        st.download_button(
                            label="⬇️ Download",
                            data=results["behavioral"],
                            file_name=f"{company}_behavioral.txt",
                            mime="text/plain",
                            key="behav_dl"
                        )

                    with tab3:
                        st.subheader("🏗️ System Design Questions")
                        st.markdown(results["system_design"])
                        st.download_button(
                            label="⬇️ Download",
                            data=results["system_design"],
                            file_name=f"{company}_systemdesign.txt",
                            mime="text/plain",
                            key="sys_dl"
                        )

                    with tab4:
                        st.subheader("💡 Company Specific Tips")
                        st.markdown(results["tips"])
                        st.download_button(
                            label="⬇️ Download",
                            data=results["tips"],
                            file_name=f"{company}_tips.txt",
                            mime="text/plain",
                            key="tips_dl"
                        )

                    st.divider()
                    full_prep = f"""
INTERVIEW PREP: {company} - {job_role}
{'='*50}

TECHNICAL QUESTIONS:
{results['technical']}

BEHAVIORAL QUESTIONS:
{results['behavioral']}

SYSTEM DESIGN QUESTIONS:
{results['system_design']}

COMPANY TIPS:
{results['tips']}
"""
                    st.download_button(
                        label="⬇️ Download Complete Prep Guide",
                        data=full_prep,
                        file_name=f"{company}_complete_prep.txt",
                        mime="text/plain",
                        key="full_dl"
                    )

            except Exception as e:
                st.error(
                    f"❌ Something went wrong: {str(e)}")
    else:
        st.warning(
            "⚠️ Please fill Company Name and Job Role!")