<div align="center">

# AI Agentic Job Tracker

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-7F77DD?style=for-the-badge)](https://niharika-jobtrack-ai.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-nkandepu2003-black?style=for-the-badge&logo=github)](https://github.com/nkandepu2003/Agentic-Job-Tracker)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Deployed-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://niharika-jobtrack-ai.streamlit.app)

</div>

---
> **Note:** First load may take 30-60 seconds as the app wakes from sleep mode on free hosting. Subsequent loads are instant.

---
I built this while preparing for my job search as a final-semester Masters student. I kept running into the same problem — every application needed a tailored resume, a personalized cover letter, and then you have to remember to follow up, prepare for interviews, and somehow keep track of everything. It felt like the process itself was the problem, not the job hunting.

So I decided to automate it.

This is a multi-agent AI platform where six agents handle different parts of the job search. You paste a job description, and the agents do the rest — tailor your resume, write a cover letter, score how well the role matches your background, prep interview questions, and log everything to a tracker. The whole pipeline runs on LangGraph, which connects the agents together so they pass context between each other instead of working in isolation.

---

## What's inside

| Agent | Tech Used |
|---|---|
| Resume Tailor | Llama 3 70B + LangChain + RAG |
| Cover Letter | Llama 3 70B + LangChain |
| Job Scout | SerpAPI + BERT Embeddings |
| Follow Up | Llama 3 + SQLite |
| Interview Prep | Llama 3 + LangChain |
| Smart Apply | LangGraph 4-node pipeline |

**Resume Tailor** reads your resume and rewrites the bullet points to match the language and requirements of a specific job description. It uses a RAG pipeline so it actually works from your resume content rather than generating something generic.

**Cover Letter Agent** writes a full cover letter personalized to the company and role. I spent a lot of time on the prompt to avoid the usual template-sounding output. It references specific things from both the job description and your background.

**Job Scout** searches Google Jobs across seven different search variations at once — things like "ML Engineer remote", "AI Engineer entry level", "Machine Learning Engineer fresher" — then deduplicates the results and scores each one against your resume using BERT-based semantic embeddings. Jobs are sorted by how recently they were posted first, because applying early genuinely matters. It also remembers what you searched last time so you don't have to retype everything.

**Follow-up Agent** checks your application tracker for roles you applied to more than seven days ago with no response, then drafts a professional follow-up email for each one. You read it, edit if needed, and send it yourself. Nothing goes out automatically.

**Interview Prep Agent** generates company-specific interview questions across technical, behavioral, and system design categories. Give it a company name and role and it actually tailors the questions to that context rather than giving you a generic list.

**Smart Apply** is the piece I'm most proud of. It uses LangGraph to connect all the agents into a four-node state graph. You paste a job description, click one button, and it runs the scoring, resume tailoring, cover letter writing, and application logging in sequence — each node receiving the full state from the previous one.

---

## The LangGraph pipeline

```
Score Job  ->  Tailor Resume  ->  Cover Letter  ->  Log to Tracker
(BERT)         (Llama 3)          (Llama 3)          (SQLite)
```

Each node receives an ApplicationState TypedDict that carries everything — the job description, resume path, match score, tailored resume text, cover letter — and passes it forward. If one node fails it degrades gracefully rather than crashing the whole pipeline.

---

## Tech stack

| | |
|---|---|
| Agent orchestration | LangGraph, LangChain |
| Language model | Llama 3 70B via Groq |
| Semantic matching | Sentence Transformers all-MiniLM-L6-v2 |
| Vector store | ChromaDB |
| Job search | SerpAPI to Google Jobs |
| Frontend | Streamlit with custom dark theme |
| Database | SQLite via SQLAlchemy |
| Language | Python 3.11 |

---

## A few things worth knowing

- Jobs are sorted by posting date first, not just match score — applying in the first 24 hours matters more than most people realize
- The keyword analysis shows exactly which technical terms are present or missing from your resume compared to the job description, not just a percentage
- Upload your resume once in the sidebar and it stays loaded across all six pages for the entire session
- The follow-up agent never sends anything automatically — it drafts, you decide

---

## A few things I figured out along the way

The match scoring was trickier than expected. Sentence Transformers compare semantic meaning, so "built CNN models" and "deep learning experience required" scores lower than it should even though they mean the same thing. I added a keyword extraction layer on top that surfaces exactly which technical terms are present or missing, which makes the score much more useful in practice.

Loading the HuggingFace embedding model on every page load was causing ten-plus second delays. Fixed it with a global cache variable so the model loads once per session and reuses across all agent calls.

The LangGraph state management needed more thought than I expected. The TypedDict has to handle partial state gracefully — if resume tailoring fails for some reason, the cover letter step should still run with what it has.

Resume handling for the deployed version was an interesting problem. Locally it finds resume.pdf automatically. On Streamlit Cloud there is no local file, so I built a session-state based uploader in the sidebar. Upload once, works across all six agent pages for the entire session. Each user gets their own session so different people can use it with their own resumes at the same time without any overlap.

---

## Running it locally

```bash
git clone https://github.com/nkandepu2003/Agentic-Job-Tracker.git
cd Agentic-Job-Tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

You need three API keys, all free:

```
GROQ_API_KEY=your_key
HUGGINGFACEHUB_API_TOKEN=your_key
SERPAPI_KEY=your_key
```

Put them in a .env file in the project root, then:

```bash
streamlit run frontend/app.py
```

---

## Structure

```
agentic-job-tracker/
├── agents/
│   ├── tailor_agent.py
│   ├── cover_letter_agent.py
│   ├── scout_agent.py
│   ├── followup_agent.py
│   ├── interview_prep_agent.py
│   └── job_application_graph.py
├── database/
│   └── models.py
├── frontend/
│   ├── app.py
│   ├── theme.py
│   └── pages/
│       ├── 1_Resume_Tailor.py
│       ├── 2_Cover_Letter.py
│       ├── 3_Job_Scout.py
│       ├── 4_Follow_Up.py
│       ├── 5_Interview_Prep.py
│       └── 6_Smart_Apply.py
└── requirements.txt
```

---

