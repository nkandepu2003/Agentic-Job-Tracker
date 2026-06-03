# api/main.py
# FastAPI Backend for AI Agentic Job Tracker
# Each agent becomes a professional API endpoint
# Streamlit pages call these endpoints

import os
import sys
import tempfile
from typing import Optional

# ─────────────────────────────────────
# LANGSMITH SETUP - MUST BE FIRST
# ─────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

langsmith_key = os.getenv("LANGCHAIN_API_KEY", "")
if langsmith_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = "agentic-job-tracker"
    os.environ["LANGCHAIN_API_KEY"] = langsmith_key

# ─────────────────────────────────────
# FASTAPI IMPORTS
# ─────────────────────────────────────
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────
# CREATE FASTAPI APP
# ─────────────────────────────────────
app = FastAPI(
    title="AI Agentic Job Tracker API",
    description="Professional REST API for all 6 AI agents. Built with FastAPI + LangChain + Groq Llama 3.",
    version="1.0.0"
)

# Allow Streamlit to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────
# REQUEST MODELS
# What data each endpoint needs
# ─────────────────────────────────────

class TailorRequest(BaseModel):
    job_description: str
    resume_text: Optional[str] = None

class CoverLetterRequest(BaseModel):
    job_description: str
    company_name: str
    resume_text: Optional[str] = None

class ScoutRequest(BaseModel):
    job_role: str
    location: str
    keywords: Optional[list] = None
    show_new_only: Optional[bool] = False

class FollowUpRequest(BaseModel):
    days_threshold: Optional[int] = 7

class InterviewPrepRequest(BaseModel):
    company: str
    job_role: str
    job_description: Optional[str] = ""

class SmartApplyRequest(BaseModel):
    job_description: str
    company_name: str
    job_title: str
    job_url: Optional[str] = "N/A"
    resume_text: Optional[str] = None

# ─────────────────────────────────────
# HEALTH CHECK ENDPOINT
# ─────────────────────────────────────

@app.get("/")
def root():
    """
    Health check endpoint.
    Visit this URL to confirm API is running.
    Like a heartbeat for your server.
    """
    return {
        "status": "running",
        "message": "AI Agentic Job Tracker API is live!",
        "version": "1.0.0",
        "agents": [
            "resume-tailor",
            "cover-letter",
            "job-scout",
            "follow-up",
            "interview-prep",
            "smart-apply"
        ]
    }

@app.get("/health")
def health_check():
    """
    Detailed health check.
    Checks if all services are available.
    """
    checks = {}

    # Check Groq key
    checks["groq_api"] = "ok" if os.getenv("GROQ_API_KEY") else "missing"

    # Check SerpAPI key
    checks["serpapi"] = "ok" if os.getenv("SERPAPI_KEY") else "missing"

    # Check HuggingFace key
    checks["huggingface"] = "ok" if os.getenv("HUGGINGFACEHUB_API_TOKEN") else "missing"

    # Check database
    checks["database"] = "ok" if os.getenv("DATABASE_URL") else "using_sqlite"

    # Check LangSmith
    checks["langsmith"] = "ok" if os.getenv("LANGCHAIN_API_KEY") else "disabled"

    all_ok = all(v in ["ok", "using_sqlite", "disabled"] for v in checks.values())

    return {
        "status": "healthy" if all_ok else "degraded",
        "checks": checks
    }

# ─────────────────────────────────────
# ENDPOINT 1: RESUME TAILOR
# POST /api/tailor-resume
# ─────────────────────────────────────

@app.post("/api/tailor-resume")
async def tailor_resume(request: TailorRequest):
    """
    Tailors your resume to match a job description.

    Input:
    - job_description: the job posting text
    - resume_text: optional resume text (uses resume.pdf if not provided)

    Output:
    - tailored_resume: AI rewritten resume text
    """
    try:
        from agents.tailor_agent import tailor_resume as run_tailor

        # Use provided resume text or fall back to file
        if request.resume_text:
            # Write to temp file so tailor_agent can read it
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".txt",
                mode="w"
            ) as tmp:
                tmp.write(request.resume_text)
                tmp_path = tmp.name
            result = run_tailor(request.resume_text, request.job_description)
        else:
            from agents.tailor_agent import run_tailor_agent
            result, error = run_tailor_agent("resume.pdf", request.job_description)
            if error:
                raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "tailored_resume": result,
            "agent": "Resume Tailor",
            "model": "Llama 3 70B via Groq"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume tailoring failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 2: COVER LETTER
# POST /api/cover-letter
# ─────────────────────────────────────

@app.post("/api/cover-letter")
async def cover_letter(request: CoverLetterRequest):
    """
    Writes a personalized cover letter.

    Input:
    - job_description: the job posting text
    - company_name: name of the company
    - resume_text: optional resume text

    Output:
    - cover_letter: AI written cover letter
    """
    try:
        from agents.cover_letter_agent import (
            write_cover_letter,
            run_cover_letter_agent
        )

        if request.resume_text:
            result = write_cover_letter(
                request.resume_text,
                request.job_description,
                request.company_name
            )
        else:
            result, error = run_cover_letter_agent(
                "resume.pdf",
                request.job_description,
                request.company_name
            )
            if error:
                raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "cover_letter": result,
            "company": request.company_name,
            "agent": "Cover Letter Writer",
            "model": "Llama 3 70B via Groq"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Cover letter generation failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 3: JOB SCOUT
# POST /api/scout-jobs
# ─────────────────────────────────────

@app.post("/api/scout-jobs")
async def scout_jobs(request: ScoutRequest):
    """
    Searches Google Jobs and scores results against resume.

    Input:
    - job_role: e.g. "Machine Learning Engineer"
    - location: e.g. "Remote"
    - keywords: optional list of keywords to filter
    - show_new_only: show only new jobs not seen before

    Output:
    - jobs: list of scored and ranked job listings
    """
    try:
        from agents.scout_agent import run_scout_agent

        jobs, error = run_scout_agent(
            job_role=request.job_role,
            location=request.location,
            keywords=request.keywords,
            show_new_only=request.show_new_only,
            pdf_path="resume.pdf"
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "total_jobs": len(jobs),
            "jobs": jobs,
            "agent": "Smart Job Scout",
            "searches_run": 7
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job search failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 4: FOLLOW UP
# POST /api/follow-up
# ─────────────────────────────────────

@app.post("/api/follow-up")
async def follow_up(request: FollowUpRequest):
    """
    Finds old applications and drafts follow-up emails.

    Input:
    - days_threshold: check applications older than X days (default 7)

    Output:
    - results: list of applications with drafted emails
    """
    try:
        from agents.followup_agent import run_followup_agent

        results, error = run_followup_agent(
            days_threshold=request.days_threshold
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "applications_found": len(results),
            "results": results,
            "agent": "Follow-up Email Drafter",
            "model": "Llama 3 70B via Groq"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Follow-up generation failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 5: INTERVIEW PREP
# POST /api/interview-prep
# ─────────────────────────────────────

@app.post("/api/interview-prep")
async def interview_prep(request: InterviewPrepRequest):
    """
    Generates company-specific interview questions.

    Input:
    - company: e.g. "Google"
    - job_role: e.g. "ML Engineer"
    - job_description: optional job description for context

    Output:
    - technical: 5 technical questions with hints
    - behavioral: 5 behavioral questions with STAR tips
    - system_design: 3 system design questions
    - tips: 5 company-specific tips
    """
    try:
        from agents.interview_prep_agent import run_interview_prep_agent

        results, error = run_interview_prep_agent(
            company=request.company,
            job_role=request.job_role,
            job_description=request.job_description
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "company": request.company,
            "job_role": request.job_role,
            "technical": results["technical"],
            "behavioral": results["behavioral"],
            "system_design": results["system_design"],
            "tips": results["tips"],
            "agent": "Interview Prep Coach",
            "model": "Llama 3 70B via Groq"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Interview prep failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 6: SMART APPLY (LangGraph)
# POST /api/smart-apply
# ─────────────────────────────────────

@app.post("/api/smart-apply")
async def smart_apply(request: SmartApplyRequest):
    """
    Runs the complete LangGraph pipeline with one click.

    Automatically:
    1. Scores job match (Sentence Transformers)
    2. Tailors resume (Llama 3)
    3. Writes cover letter (Llama 3)
    4. Logs application to database

    Input:
    - job_description: the full job posting
    - company_name: e.g. "Google"
    - job_title: e.g. "ML Engineer"
    - job_url: optional link to job posting

    Output:
    - match_score: percentage match
    - tailored_resume: AI rewritten resume
    - cover_letter: personalized cover letter
    - application_logged: whether saved to tracker
    """
    try:
        from agents.job_application_graph import run_application_graph

        final_state, error = run_application_graph(
            job_description=request.job_description,
            company_name=request.company_name,
            job_title=request.job_title,
            job_url=request.job_url or "N/A",
            resume_path="resume.pdf"
        )

        if error:
            raise HTTPException(status_code=400, detail=error)

        return {
            "status": "success",
            "company": request.company_name,
            "job_title": request.job_title,
            "match_score": final_state.get("match_score", 0),
            "matching_keywords": final_state.get("matching_keywords", []),
            "missing_keywords": final_state.get("missing_keywords", []),
            "tailored_resume": final_state.get("tailored_resume"),
            "cover_letter": final_state.get("cover_letter"),
            "application_logged": final_state.get("application_logged", False),
            "pipeline": "LangGraph 4-node pipeline",
            "agents_used": [
                "Score Job (BERT)",
                "Tailor Resume (Llama 3)",
                "Write Cover Letter (Llama 3)",
                "Log Application (Supabase)"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Smart Apply failed: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 7: GET ALL APPLICATIONS
# GET /api/applications
# ─────────────────────────────────────

@app.get("/api/applications")
def get_applications():
    """
    Returns all job applications from database.
    Like reading your entire job tracker.
    """
    try:
        from database.models import get_db, JobApplication

        db = get_db()
        applications = db.query(JobApplication).all()
        db.close()

        result = []
        for app in applications:
            result.append({
                "id": app.id,
                "company": app.company,
                "job_title": app.job_title,
                "status": app.status,
                "location": app.location or "N/A",
                "salary": app.salary or "N/A",
                "date_applied": app.date_applied.strftime(
                    "%d %b %Y") if app.date_applied else "N/A",
                "notes": app.notes or "",
                "job_url": app.job_url or "N/A"
            })

        return {
            "status": "success",
            "total": len(result),
            "applications": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch applications: {str(e)}"
        )

# ─────────────────────────────────────
# ENDPOINT 8: DELETE APPLICATION
# DELETE /api/applications/{app_id}
# ─────────────────────────────────────

@app.delete("/api/applications/{app_id}")
def delete_application_endpoint(app_id: int):
    """
    Deletes a job application by ID.
    """
    try:
        from database.models import delete_application

        success = delete_application(app_id)

        if success:
            return {
                "status": "success",
                "message": f"Application {app_id} deleted"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Application {app_id} not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )

# ─────────────────────────────────────
# RUN THE SERVER
# ─────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )