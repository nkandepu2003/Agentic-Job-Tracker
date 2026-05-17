# pages/4_Follow_Up.py
import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Follow Up",
    page_icon="📧",
    layout="wide"
)

st.title("📧 AI Follow-up Agent")
st.markdown(
    "Finds applications with no response "
    "and drafts professional follow-up emails!")

days_threshold = st.slider(
    "Check applications older than (days):",
    min_value=3,
    max_value=30,
    value=7,
    step=1
)

st.caption(
    f"Will find applications older than "
    f"{days_threshold} days with status 'Applied'")

if st.button("📧 Check & Draft Follow-ups",
             use_container_width=True):
    with st.spinner(
        "📧 Checking applications and "
        "drafting follow-up emails..."
    ):
        try:
            from agents.followup_agent import (
                run_followup_agent)

            results, error = run_followup_agent(
                days_threshold)

            if error:
                st.error(f"❌ Error: {error}")
            elif not results:
                st.success(
                    f"✅ No applications need "
                    f"follow-up yet! "
                    f"(None older than "
                    f"{days_threshold} days)")
            else:
                st.success(
                    f"✅ Found {len(results)} "
                    f"applications needing follow-up!")

                for i, result in enumerate(results):
                    app = result["application"]
                    email = result["email"]

                    with st.expander(
                        f"📧 {app['company']} — "
                        f"{app['job_title']} | "
                        f"Applied {app['days_since']} "
                        f"days ago"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(
                                f"📅 **Applied:** "
                                f"{app['date_applied']}")
                            st.write(
                                f"⏰ **Days since:** "
                                f"{app['days_since']} days")
                        with col2:
                            st.write(
                                f"📍 **Location:** "
                                f"{app['location']}")
                            if app['job_url'] != 'N/A':
                                st.link_button(
                                    "🔗 View Job",
                                    app['job_url']
                                )

                        st.divider()
                        st.write(
                            "**✉️ Drafted Follow-up Email:**")
                        st.markdown(email)

                        st.download_button(
                            label="⬇️ Download Email",
                            data=email,
                            file_name=f"followup_{app['company']}.txt",
                            mime="text/plain",
                            key=f"followup_{i}"
                        )
                        st.caption(
                            "👆 Review, personalize "
                            "if needed, then send manually.")

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")