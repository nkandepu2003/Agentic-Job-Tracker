# followup_agent.py
# This agent checks your job applications
# Finds ones older than 7 days with no response
# Drafts professional follow-up emails
# You review and send manually

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ─────────────────────────────────────
# SETUP GROQ + LLAMA 3
# ─────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "Groq API key not found! "
        "Check your .env file has: "
        "GROQ_API_KEY=gsk_xxx"
    )

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.7,
    max_tokens=1024
)

# ─────────────────────────────────────
# FUNCTION 1: FIND APPLICATIONS NEEDING FOLLOWUP
# ─────────────────────────────────────

def find_applications_needing_followup(days_threshold=7):
    """
    Checks your database for applications
    that are older than X days with no response.

    Think of it like:
    Going through your filing cabinet
    finding forms submitted weeks ago
    that nobody replied to yet.

    Returns list of applications needing followup.
    """

    from database.models import get_db, JobApplication

    db = get_db()

    # Get all applications
    all_applications = db.query(JobApplication).all()
    db.close()

    # Calculate cutoff date
    # Applications older than this need followup
    cutoff_date = datetime.now() - timedelta(
        days=days_threshold)

    # Filter applications that need followup
    needs_followup = []

    for app in all_applications:

        # Only check "Applied" status
        # Skip interviews, offers, rejections
        if app.status != "Applied":
            continue

        # Check if application is old enough
        if app.date_applied and app.date_applied < cutoff_date:
            days_since = (
                datetime.now() - app.date_applied).days

            needs_followup.append({
                "id": app.id,
                "company": app.company,
                "job_title": app.job_title,
                "date_applied": app.date_applied.strftime(
                    "%d %b %Y"),
                "days_since": days_since,
                "location": app.location or "N/A",
                "job_url": app.job_url or "N/A",
                "notes": app.notes or ""
            })

    # Sort by oldest first
    needs_followup.sort(
        key=lambda x: x["days_since"],
        reverse=True
    )

    return needs_followup


# ─────────────────────────────────────
# FUNCTION 2: DRAFT FOLLOWUP EMAIL
# ─────────────────────────────────────

def draft_followup_email(
    company,
    job_title,
    date_applied,
    days_since,
    candidate_name="Niharika Kandepu"
):
    """
    Uses Llama 3 to write a professional
    follow-up email for a specific application.

    Like having a career coach write
    a polite follow-up on your behalf.
    """

    prompt_template = PromptTemplate(
        input_variables=[
            "company",
            "job_title",
            "date_applied",
            "days_since",
            "candidate_name"
        ],
        template="""
You are an expert career coach writing a
professional follow-up email.

Write a SHORT, polite follow-up email for
a job application with these details:

Company: {company}
Job Title: {job_title}
Date Applied: {date_applied}
Days Since Applied: {days_since} days
Candidate Name: {candidate_name}

Rules:
- Keep it SHORT (3-4 sentences max)
- Be polite and professional
- Show genuine interest in the role
- Don't sound desperate or pushy
- Ask politely about application status
- End with a thank you
- Include subject line at the top

Format:
Subject: [write subject line here]

[write email body here]

Write the follow-up email now:
"""
    )

    chain = prompt_template | llm | StrOutputParser()

    result = chain.invoke({
        "company": company,
        "job_title": job_title,
        "date_applied": date_applied,
        "days_since": days_since,
        "candidate_name": candidate_name
    })

    return result


# ─────────────────────────────────────
# FUNCTION 3: MAIN FUNCTION
# ─────────────────────────────────────

def run_followup_agent(days_threshold=7):
    """
    Main function that runs the complete agent.

    Steps:
    1. Check database for old applications
    2. For each one draft a follow-up email
    3. Return list of applications + emails

    You review each email and send manually.
    We never send automatically.
    YOU are always in control.
    """

    print("📧 Starting Follow-up Agent...")

    # STEP 1: Find applications needing followup
    print(
        f"🔍 Finding applications older than "
        f"{days_threshold} days...")
    applications = find_applications_needing_followup(
        days_threshold)

    if not applications:
        return [], None

    print(f"📋 Found {len(applications)} applications "
          f"needing follow-up!")

    # STEP 2: Draft email for each application
    results = []
    for i, app in enumerate(applications):
        print(
            f"✍️  Drafting email {i+1}/{len(applications)}: "
            f"{app['company']}...")

        email = draft_followup_email(
            company=app["company"],
            job_title=app["job_title"],
            date_applied=app["date_applied"],
            days_since=app["days_since"]
        )

        results.append({
            "application": app,
            "email": email
        })

    print("✅ All follow-up emails drafted!")
    return results, None


if __name__ == "__main__":
    print("Follow-up Agent Ready!")
    print("Checks applications older than 7 days.")
    print("Drafts professional follow-up emails.")