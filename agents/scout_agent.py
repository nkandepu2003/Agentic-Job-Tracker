# scout_agent.py
# Smart Job Scout Agent
# Searches multiple job variations
# Scores each job against your resume
# Shows matching and missing keywords
# Remembers your search history
# Sorts by recency first then match score

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
import os
import sys
import json
from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
import fitz

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ─────────────────────────────────────
# SETUP
# ─────────────────────────────────────

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

if not SERPAPI_KEY:
    raise ValueError(
        "SerpAPI key not found! "
        "Check your .env file has: "
        "SERPAPI_KEY=your_key_here"
    )

HISTORY_FILE = "seen_jobs.json"
PREFERENCES_FILE = "search_preferences.json"

# ─────────────────────────────────────
# FUNCTION 1: SAVE/LOAD HISTORY
# ─────────────────────────────────────

def load_seen_jobs():
    """
    Loads list of jobs you already saw.
    Like a memory of what you've seen before.
    """
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen_jobs):
    """
    Saves list of jobs you already saw.
    So next time we only show NEW jobs.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(seen_jobs), f)


# ─────────────────────────────────────
# FUNCTION 2: SAVE/LOAD PREFERENCES
# ─────────────────────────────────────

def save_search_preferences(job_role, location):
    """
    Saves your last search so next time
    the app remembers what you typed.
    Stores last 5 searches for each field.
    """
    try:
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, "r") as f:
                prefs = json.load(f)
        else:
            prefs = {
                "recent_roles": [],
                "recent_locations": []
            }

        if job_role and job_role not in prefs["recent_roles"]:
            prefs["recent_roles"].insert(0, job_role)
            prefs["recent_roles"] = prefs["recent_roles"][:5]

        if location and location not in prefs["recent_locations"]:
            prefs["recent_locations"].insert(0, location)
            prefs["recent_locations"] = prefs["recent_locations"][:5]

        with open(PREFERENCES_FILE, "w") as f:
            json.dump(prefs, f)

    except Exception as e:
        print(f"Could not save preferences: {str(e)}")


def load_search_preferences():
    """
    Loads your previous searches.
    Returns dict with recent roles and locations.
    """
    try:
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, "r") as f:
                return json.load(f)
        return {
            "recent_roles": [],
            "recent_locations": []
        }
    except Exception:
        return {
            "recent_roles": [],
            "recent_locations": []
        }


# ─────────────────────────────────────
# FUNCTION 3: FORMAT POSTED TIME
# ─────────────────────────────────────

def format_posted_time(posted_str):
    """
    Converts posted date to readable format.
    Examples:
    "3 hours ago" → "⏰ 3 hours ago"
    "2 days ago"  → "📅 2 days ago"
    """
    if not posted_str or posted_str == "N/A":
        return "📅 Recently posted"

    posted_lower = posted_str.lower()

    if "hour" in posted_lower:
        return f"⏰ {posted_str}"
    elif "day" in posted_lower:
        return f"📅 {posted_str}"
    elif "week" in posted_lower:
        return f"📆 {posted_str}"
    elif "month" in posted_lower:
        return f"🗓️ {posted_str}"
    else:
        return f"📅 {posted_str}"


# ─────────────────────────────────────
# FUNCTION 4: EXTRACT KEYWORDS
# ─────────────────────────────────────

def extract_keywords(text):
    """
    Extracts important technical keywords from text.
    These are words that matter for job matching.
    """

    tech_keywords = [
        # Programming Languages
        "Python", "Java", "Scala", "R", "SQL",
        "JavaScript", "TypeScript", "C++", "Go",

        # ML/AI Frameworks
        "TensorFlow", "PyTorch", "Keras", "scikit-learn",
        "XGBoost", "LightGBM", "Hugging Face", "BERT",
        "Transformers", "LangChain", "LangGraph",

        # Modern AI
        "LLM", "GPT", "RAG", "Vector Database",
        "ChromaDB", "Pinecone", "Embeddings",
        "Prompt Engineering", "Fine-tuning",
        "Agentic", "AI Agents", "MCP",

        # MLOps and Tools
        "MLOps", "Docker", "Kubernetes", "Git",
        "CI/CD", "FastAPI", "Flask", "Streamlit",
        "Airflow", "MLflow", "DVC",

        # Cloud
        "AWS", "GCP", "Azure", "S3", "EC2",
        "SageMaker", "Vertex AI",

        # Data
        "Pandas", "NumPy", "Spark", "Hadoop",
        "NoSQL", "MongoDB", "PostgreSQL",

        # Concepts
        "Deep Learning", "Machine Learning",
        "Neural Networks", "Computer Vision", "NLP",
        "Natural Language Processing", "CNN", "RNN",
        "LSTM", "Transformer", "Attention",
        "Reinforcement Learning", "Data Science",
        "Feature Engineering", "Model Deployment",
        "REST API", "Microservices",
    ]

    found_keywords = []
    text_lower = text.lower()

    for keyword in tech_keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)

    return found_keywords


def get_keyword_analysis(resume_text, job_text):
    """
    Compares keywords in resume vs job description.

    Returns:
    matching: keywords in BOTH resume and JD
    missing: keywords in JD but NOT in resume
    """
    resume_keywords = set(extract_keywords(resume_text))
    job_keywords = set(extract_keywords(job_text))

    matching = list(resume_keywords & job_keywords)
    missing = list(job_keywords - resume_keywords)

    return matching, missing


# ─────────────────────────────────────
# FUNCTION 5: SEARCH JOBS
# ─────────────────────────────────────

def search_jobs(search_term, location, num_results=10):
    """
    Searches Google Jobs for one search term.
    Returns list of job dictionaries.
    """
    try:
        params = {
            "engine": "google_jobs",
            "q": f"{search_term} {location}",
            "api_key": SERPAPI_KEY,
            "num": num_results
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        jobs_raw = results.get("jobs_results", [])

        jobs = []
        for job in jobs_raw:
            cleaned_job = {
                "title": job.get("title", "N/A"),
                "company": job.get("company_name", "N/A"),
                "location": job.get("location", "N/A"),
                "description": job.get(
                    "description", "N/A")[:500],
                "posted": job.get(
                    "detected_extensions", {}).get(
                    "posted_at", "N/A"),
                "salary": job.get(
                    "detected_extensions", {}).get(
                    "salary", "Not specified"),
                "apply_link": job.get(
                    "related_links", [{}])[0].get(
                    "link", "N/A") if job.get(
                    "related_links") else "N/A",
                "job_id": job.get("job_id", "N/A"),
                "match_score": 0,
                "matching_keywords": [],
                "missing_keywords": []
            }
            jobs.append(cleaned_job)
        return jobs

    except Exception as e:
        print(f"Search error for '{search_term}': {str(e)}")
        return []


# ─────────────────────────────────────
# FUNCTION 6: REMOVE DUPLICATES
# ─────────────────────────────────────

def remove_duplicates(jobs):
    """
    Removes duplicate job listings.
    Same job might appear in multiple searches.
    """
    seen = set()
    unique_jobs = []

    for job in jobs:
        key = (
            f"{job['title'].lower()}_"
            f"{job['company'].lower()}"
        )
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


# ─────────────────────────────────────
# FUNCTION 7: READ RESUME
# ─────────────────────────────────────

def read_resume(pdf_path):
    """
    Reads your resume PDF.
    Returns text content.
    """
    if not os.path.exists(pdf_path):
        return None
    try:
        pdf_document = fitz.open(pdf_path)
        full_text = ""
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            full_text += page.get_text()
        pdf_document.close()
        return full_text
    except Exception:
        return None


# ─────────────────────────────────────
# FUNCTION 8: SCORE JOBS AGAINST RESUME
# ─────────────────────────────────────

def score_jobs_against_resume(jobs, resume_text):
    """
    Scores each job against your resume.
    Also finds matching and missing keywords.
    Shows ALL jobs but ranks best matches first.
    """

    print("🧠 Scoring jobs against your resume...")

    try:
        embeddings_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        resume_vector = embeddings_model.embed_query(
            resume_text[:1000]
        )

        for job in jobs:
            job_text = (
                f"{job['title']} "
                f"{job['company']} "
                f"{job['description']}"
            )

            job_vector = embeddings_model.embed_query(job_text)
            resume_np = np.array(resume_vector)
            job_np = np.array(job_vector)

            similarity = np.dot(resume_np, job_np) / (
                np.linalg.norm(resume_np) *
                np.linalg.norm(job_np)
            )
            score = round(float(similarity) * 100, 1)
            job["match_score"] = score

            matching, missing = get_keyword_analysis(
                resume_text, job_text)
            job["matching_keywords"] = matching[:10]
            job["missing_keywords"] = missing[:10]

        print("✅ Scoring complete!")
        return jobs

    except Exception as e:
        print(f"Scoring error: {str(e)}")
        return jobs


# ─────────────────────────────────────
# FUNCTION 9: SORT BY RECENCY + SCORE
# ─────────────────────────────────────

def sort_jobs(jobs):
    """
    Sorts jobs by recency first then match score.

    Priority order:
    1. Jobs posted within 24 hours (hours ago)
    2. Jobs posted within 7 days (days ago)
    3. Jobs posted within a month (weeks ago)
    4. Older jobs (months ago)

    Within each group sorted by match score.
    Apply to fresh jobs before everyone else!
    """

    def get_sort_priority(job):
        posted = job.get("posted", "").lower()

        # Within 24 hours = highest priority
        if "hour" in posted:
            recency = 0

        # Within 7 days
        elif "day" in posted:
            try:
                days = int(''.join(
                    filter(str.isdigit, posted)))
                recency = days
            except Exception:
                recency = 7

        # Within a month
        elif "week" in posted:
            try:
                weeks = int(''.join(
                    filter(str.isdigit, posted)))
                recency = weeks * 7
            except Exception:
                recency = 30

        # Older than a month
        elif "month" in posted:
            recency = 90

        # Unknown = treat as recent
        else:
            recency = 7

        # Lower recency = shown first
        # Within same recency higher score = shown first
        return (recency, -job["match_score"])

    jobs.sort(key=get_sort_priority)
    return jobs


# ─────────────────────────────────────
# FUNCTION 10: MAIN FUNCTION
# ─────────────────────────────────────

def run_scout_agent(
    job_role,
    location,
    keywords=None,
    show_new_only=False,
    pdf_path="resume.pdf"
):
    """
    Main function - runs complete smart scout.

    Steps:
    1. Save search preferences
    2. Search 7 variations
    3. Remove duplicates
    4. Score against resume + keyword analysis
    5. Sort by recency then match score
    6. Mark new vs seen jobs
    7. Return ranked results
    """

    print(f"🚀 Starting Smart Job Scout...")
    print(f"Role: {job_role} | Location: {location}")

    # STEP 1: Save preferences for next session
    save_search_preferences(job_role, location)

    # STEP 2: Create 7 search variations
    search_terms = [
        job_role,
        f"{job_role} entry level",
        f"{job_role} fresher",
        f"ML Engineer {location}",
        f"AI Engineer {location}",
        f"Data Scientist {location}",
        f"Machine Learning {location}"
    ]

    # STEP 3: Search all variations
    all_jobs = []
    for term in search_terms:
        print(f"🔍 Searching: {term}...")
        jobs = search_jobs(term, location, num_results=10)
        all_jobs.extend(jobs)
        print(f"   Found {len(jobs)} jobs")

    print(f"📊 Total raw results: {len(all_jobs)}")

    if not all_jobs:
        return [], "No jobs found. Check your SerpAPI key."

    # STEP 4: Remove duplicates
    unique_jobs = remove_duplicates(all_jobs)
    print(
        f"✅ After removing duplicates: "
        f"{len(unique_jobs)} unique jobs"
    )

    # STEP 5: Filter by keywords if provided
    if keywords:
        filtered = []
        for job in unique_jobs:
            job_text = (
                job["title"] + " " +
                job["description"] + " " +
                job["company"]
            ).lower()
            for keyword in keywords:
                if keyword.lower() in job_text:
                    filtered.append(job)
                    break
        unique_jobs = filtered
        print(
            f"🔤 After keyword filter: "
            f"{len(unique_jobs)} jobs"
        )

    # STEP 6: Score against resume + keyword analysis
    resume_text = read_resume(pdf_path)
    if resume_text:
        unique_jobs = score_jobs_against_resume(
            unique_jobs, resume_text)
    else:
        print("⚠️ Resume not found. Skipping scoring.")

    # STEP 7: Sort by recency FIRST then match score
    unique_jobs = sort_jobs(unique_jobs)
    print("📅 Jobs sorted by recency then match score!")

    # STEP 8: Mark new vs seen jobs
    seen_jobs = load_seen_jobs()
    new_jobs = []
    existing_jobs = []

    for job in unique_jobs:
        job_key = f"{job['title']}_{job['company']}"
        if job_key in seen_jobs:
            job["is_new"] = False
            existing_jobs.append(job)
        else:
            job["is_new"] = True
            new_jobs.append(job)

    if show_new_only:
        final_jobs = new_jobs
    else:
        final_jobs = new_jobs + existing_jobs

    # STEP 9: Save all to history
    for job in final_jobs:
        job_key = f"{job['title']}_{job['company']}"
        seen_jobs.add(job_key)
    save_seen_jobs(seen_jobs)

    print(f"🆕 New jobs: {len(new_jobs)}")
    print(f"👀 Previously seen: {len(existing_jobs)}")
    print(
        f"✅ Scout complete! "
        f"Returning {len(final_jobs)} jobs"
    )

    return final_jobs, None


if __name__ == "__main__":
    print("Smart Scout Agent Ready!")
    print("Sorts by recency first, then match score.")
    print("Fresh jobs always appear at top!")