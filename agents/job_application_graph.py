# job_application_graph.py
# This connects all agents together using LangGraph
# One click → all agents run automatically
# This is what makes the project truly AGENTIC

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
import os
import sys
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ─────────────────────────────────────
# STEP 1: DEFINE THE STATE
# ─────────────────────────────────────

class ApplicationState(TypedDict):
    """
    This is the memory of our agent graph.
    Like a shared notebook that all agents
    can read from and write to.

    Think of it like a job application folder:
    → Start with job description
    → Each agent adds their work to the folder
    → Final folder has everything ready
    """

    # Input - what you provide
    job_description: str
    company_name: str
    job_title: str
    job_url: str
    resume_path: str

    # What each agent adds
    match_score: Optional[float]
    matching_keywords: Optional[list]
    missing_keywords: Optional[list]
    tailored_resume: Optional[str]
    cover_letter: Optional[str]
    application_logged: Optional[bool]

    # Status tracking
    current_step: str
    errors: Optional[list]


# ─────────────────────────────────────
# STEP 2: DEFINE EACH NODE (AGENT STEP)
# ─────────────────────────────────────

def score_job_node(state: ApplicationState) -> ApplicationState:
    """
    Node 1: Score the job against your resume.

    Like a quick assessment:
    "Is this job worth applying to?"
    Shows match % and missing keywords.
    """
    print("🎯 Node 1: Scoring job against resume...")

    try:
        from agents.scout_agent import (
            read_resume,
            get_keyword_analysis,
            extract_keywords
        )
        from langchain_huggingface import HuggingFaceEmbeddings
        import numpy as np

        resume_text = read_resume(state["resume_path"])

        if not resume_text:
            state["match_score"] = 0.0
            state["matching_keywords"] = []
            state["missing_keywords"] = []
            state["current_step"] = "scored"
            return state

        # Score using sentence transformers
        embeddings_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        resume_vector = embeddings_model.embed_query(
            resume_text[:1000])
        job_vector = embeddings_model.embed_query(
            state["job_description"][:500])

        resume_np = np.array(resume_vector)
        job_np = np.array(job_vector)

        similarity = np.dot(resume_np, job_np) / (
            np.linalg.norm(resume_np) *
            np.linalg.norm(job_np)
        )
        score = round(float(similarity) * 100, 1)

        matching, missing = get_keyword_analysis(
            resume_text,
            state["job_description"]
        )

        state["match_score"] = score
        state["matching_keywords"] = matching[:8]
        state["missing_keywords"] = missing[:8]
        state["current_step"] = "scored"

        print(f"✅ Match score: {score}%")
        return state

    except Exception as e:
        print(f"⚠️ Scoring error: {str(e)}")
        state["match_score"] = 0.0
        state["matching_keywords"] = []
        state["missing_keywords"] = []
        state["current_step"] = "scored"
        return state


def tailor_resume_node(state: ApplicationState) -> ApplicationState:
    """
    Node 2: Tailor resume for this specific job.

    Takes your base resume and rewrites it
    to match the job description perfectly.
    """
    print("📄 Node 2: Tailoring resume...")

    try:
        from agents.tailor_agent import run_tailor_agent

        tailored_resume, error = run_tailor_agent(
            state["resume_path"],
            state["job_description"]
        )

        if error:
            print(f"⚠️ Tailor error: {error}")
            state["tailored_resume"] = None
        else:
            state["tailored_resume"] = tailored_resume
            print("✅ Resume tailored!")

        state["current_step"] = "resume_tailored"
        return state

    except Exception as e:
        print(f"⚠️ Tailor error: {str(e)}")
        state["tailored_resume"] = None
        state["current_step"] = "resume_tailored"
        return state


def write_cover_letter_node(state: ApplicationState) -> ApplicationState:
    """
    Node 3: Write cover letter for this job.

    Uses company name + job description
    to write a personalized cover letter.
    """
    print("✉️ Node 3: Writing cover letter...")

    try:
        from agents.cover_letter_agent import (
            run_cover_letter_agent)

        cover_letter, error = run_cover_letter_agent(
            state["resume_path"],
            state["job_description"],
            state["company_name"]
        )

        if error:
            print(f"⚠️ Cover letter error: {error}")
            state["cover_letter"] = None
        else:
            state["cover_letter"] = cover_letter
            print("✅ Cover letter written!")

        state["current_step"] = "cover_letter_written"
        return state

    except Exception as e:
        print(f"⚠️ Cover letter error: {str(e)}")
        state["cover_letter"] = None
        state["current_step"] = "cover_letter_written"
        return state


def log_application_node(state: ApplicationState) -> ApplicationState:
    """
    Node 4: Log this application to your tracker.

    Automatically saves the company, job title,
    URL, and status to your database.
    No manual entry needed!
    """
    print("📊 Node 4: Logging application to tracker...")

    try:
        from database.models import get_db, JobApplication
        from datetime import datetime

        db = get_db()
        new_application = JobApplication(
            company=state["company_name"],
            job_title=state["job_title"],
            job_url=state["job_url"],
            status="Applied",
            date_applied=datetime.now(),
            notes=f"Auto-logged | Match: {state.get('match_score', 0)}%"
        )
        db.add(new_application)
        db.commit()
        db.close()

        state["application_logged"] = True
        state["current_step"] = "completed"
        print("✅ Application logged to tracker!")
        return state

    except Exception as e:
        print(f"⚠️ Logging error: {str(e)}")
        state["application_logged"] = False
        state["current_step"] = "completed"
        return state


# ─────────────────────────────────────
# STEP 3: BUILD THE GRAPH
# ─────────────────────────────────────

def build_application_graph():
    """
    Builds the LangGraph workflow.

    Think of it like drawing a flowchart:
    Start → Score → Tailor → Cover Letter → Log → End

    Each arrow = automatic connection
    No human needed between steps!

    This is AGENTIC AI:
    Agent decides what to do next
    based on the current state.
    """

    # Create the graph
    graph = StateGraph(ApplicationState)

    # Add all nodes (agents)
    graph.add_node("score_job", score_job_node)
    graph.add_node("tailor_resume", tailor_resume_node)
    graph.add_node("write_cover_letter", write_cover_letter_node)
    graph.add_node("log_application", log_application_node)

    # Connect the nodes in order
    # This defines the flow:
    # score → tailor → cover letter → log → end
    graph.set_entry_point("score_job")
    graph.add_edge("score_job", "tailor_resume")
    graph.add_edge("tailor_resume", "write_cover_letter")
    graph.add_edge("write_cover_letter", "log_application")
    graph.add_edge("log_application", END)

    # Compile the graph
    app = graph.compile()
    return app


# ─────────────────────────────────────
# STEP 4: MAIN FUNCTION
# ─────────────────────────────────────

def run_application_graph(
    job_description,
    company_name,
    job_title,
    job_url="N/A",
    resume_path="resume.pdf"
):
    """
    Main function - runs the complete
    agentic application workflow.

    You provide:
    → job description
    → company name
    → job title

    Graph automatically:
    → Scores match
    → Tailors resume
    → Writes cover letter
    → Logs to tracker

    Returns everything ready to apply!
    """

    print("🚀 Starting Agentic Application Graph...")
    print(f"Company: {company_name} | Role: {job_title}")

    # Build the graph
    graph = build_application_graph()

    # Set initial state
    initial_state = {
        "job_description": job_description,
        "company_name": company_name,
        "job_title": job_title,
        "job_url": job_url,
        "resume_path": resume_path,
        "match_score": None,
        "matching_keywords": None,
        "missing_keywords": None,
        "tailored_resume": None,
        "cover_letter": None,
        "application_logged": None,
        "current_step": "starting",
        "errors": []
    }

    # Run the graph
    final_state = graph.invoke(initial_state)

    print("✅ Agentic graph complete!")
    return final_state, None


if __name__ == "__main__":
    print("LangGraph Application Agent Ready!")
    print("Connects all agents in automatic workflow.")