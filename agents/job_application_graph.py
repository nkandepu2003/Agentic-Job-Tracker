# job_application_graph.py
# This connects all agents together using LangGraph
# One click - all agents run automatically
# This is what makes the project truly AGENTIC

import os
import sys
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import numpy as np

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class ApplicationState(TypedDict):
    job_description: str
    company_name: str
    job_title: str
    job_url: str
    resume_path: str
    match_score: Optional[float]
    matching_keywords: Optional[list]
    missing_keywords: Optional[list]
    tailored_resume: Optional[str]
    cover_letter: Optional[str]
    application_logged: Optional[bool]
    current_step: str
    errors: Optional[list]


def score_job_node(state: ApplicationState) -> ApplicationState:
    print("Node 1: Scoring job against resume...")
    try:
        from agents.scout_agent import (
            read_resume,
            get_keyword_analysis,
            load_embedding_model
        )

        resume_text = read_resume(state["resume_path"])

        if not resume_text:
            state["match_score"] = 0.0
            state["matching_keywords"] = []
            state["missing_keywords"] = []
            state["current_step"] = "scored"
            return state

        embeddings_model = load_embedding_model()

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

        print(f"Match score: {score}%")
        return state

    except Exception as e:
        print(f"Scoring error: {str(e)}")
        state["match_score"] = 0.0
        state["matching_keywords"] = []
        state["missing_keywords"] = []
        state["current_step"] = "scored"
        return state


def tailor_resume_node(state: ApplicationState) -> ApplicationState:
    print("Node 2: Tailoring resume...")
    try:
        from agents.tailor_agent import run_tailor_agent

        tailored_resume, error = run_tailor_agent(
            state["resume_path"],
            state["job_description"]
        )

        if error:
            print(f"Tailor error: {error}")
            state["tailored_resume"] = None
        else:
            state["tailored_resume"] = tailored_resume
            print("Resume tailored!")

        state["current_step"] = "resume_tailored"
        return state

    except Exception as e:
        print(f"Tailor error: {str(e)}")
        state["tailored_resume"] = None
        state["current_step"] = "resume_tailored"
        return state


def write_cover_letter_node(state: ApplicationState) -> ApplicationState:
    print("Node 3: Writing cover letter...")
    try:
        from agents.cover_letter_agent import (
            run_cover_letter_agent)

        cover_letter, error = run_cover_letter_agent(
            state["resume_path"],
            state["job_description"],
            state["company_name"]
        )

        if error:
            print(f"Cover letter error: {error}")
            state["cover_letter"] = None
        else:
            state["cover_letter"] = cover_letter
            print("Cover letter written!")

        state["current_step"] = "cover_letter_written"
        return state

    except Exception as e:
        print(f"Cover letter error: {str(e)}")
        state["cover_letter"] = None
        state["current_step"] = "cover_letter_written"
        return state


def log_application_node(state: ApplicationState) -> ApplicationState:
    print("Node 4: Logging application to tracker...")
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
        print("Application logged to tracker!")
        return state

    except Exception as e:
        print(f"Logging error: {str(e)}")
        state["application_logged"] = False
        state["current_step"] = "completed"
        return state


def build_application_graph():
    graph = StateGraph(ApplicationState)

    graph.add_node("score_job", score_job_node)
    graph.add_node("tailor_resume", tailor_resume_node)
    graph.add_node("write_cover_letter", write_cover_letter_node)
    graph.add_node("log_application", log_application_node)

    graph.set_entry_point("score_job")
    graph.add_edge("score_job", "tailor_resume")
    graph.add_edge("tailor_resume", "write_cover_letter")
    graph.add_edge("write_cover_letter", "log_application")
    graph.add_edge("log_application", END)

    app = graph.compile()
    return app


def run_application_graph(
    job_description,
    company_name,
    job_title,
    job_url="N/A",
    resume_path="resume.pdf"
):
    print("Starting Agentic Application Graph...")
    print(f"Company: {company_name} | Role: {job_title}")

    graph = build_application_graph()

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

    final_state = graph.invoke(initial_state)

    print("Agentic graph complete!")
    return final_state, None


if __name__ == "__main__":
    print("LangGraph Application Agent Ready!")