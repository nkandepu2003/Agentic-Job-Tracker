# interview_prep_agent.py
# Generates interview questions specific
# to a company and role

import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# ─────────────────────────────────────
# SETUP GROQ
# ─────────────────────────────────────

try:
    import streamlit as st
    GROQ_API_KEY = st.secrets.get(
        "GROQ_API_KEY",
        os.getenv("GROQ_API_KEY")
    )
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "Groq API key not found! "
        "Check your .env file."
    )

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.7,
    max_tokens=2048
)

# ─────────────────────────────────────
# FUNCTION 1: TECHNICAL QUESTIONS
# ─────────────────────────────────────

def generate_technical_questions(
    company, job_role, job_description):

    prompt_template = PromptTemplate(
        input_variables=[
            "company", "job_role", "job_description"],
        template="""
You are an expert interview coach who knows
exactly what {company} asks in interviews
for {job_role} positions.

Generate 5 TECHNICAL interview questions
that {company} is likely to ask for this role.

Job Description Context:
{job_description}

Rules:
- Questions must be specific to {company}
- Focus on skills in job description
- Include ML/AI technical concepts
- Mix easy and hard questions
- For each question provide a brief hint

Format each question like this:
Q1: [question]
Hint: [brief answer hint]

Generate 5 technical questions now:
"""
    )

    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "company": company,
        "job_role": job_role,
        "job_description": job_description
    })
    return result


# ─────────────────────────────────────
# FUNCTION 2: BEHAVIORAL QUESTIONS
# ─────────────────────────────────────

def generate_behavioral_questions(company, job_role):

    prompt_template = PromptTemplate(
        input_variables=["company", "job_role"],
        template="""
You are an expert interview coach.

Generate 5 BEHAVIORAL interview questions
that {company} typically asks for {job_role}.

These should be STAR method questions.

Rules:
- Make them specific to {company} values
- Focus on teamwork, leadership, problem solving
- For each question explain what they want

Format each question like this:
Q1: [question]
They want to know: [what interviewer is looking for]
STAR tip: [how to structure your answer]

Generate 5 behavioral questions now:
"""
    )

    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "company": company,
        "job_role": job_role
    })
    return result


# ─────────────────────────────────────
# FUNCTION 3: SYSTEM DESIGN QUESTIONS
# ─────────────────────────────────────

def generate_system_design_questions(company, job_role):

    prompt_template = PromptTemplate(
        input_variables=["company", "job_role"],
        template="""
You are an expert interview coach specializing
in ML system design interviews.

Generate 3 SYSTEM DESIGN interview questions
that {company} might ask for {job_role}.

Rules:
- Focus on ML/AI system design
- Think about scale and production
- Include real problems {company} faces

Format each question like this:
Q1: [question]
How to approach: [framework for answering]
Key points to cover: [3-4 bullet points]

Generate 3 system design questions now:
"""
    )

    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "company": company,
        "job_role": job_role
    })
    return result


# ─────────────────────────────────────
# FUNCTION 4: COMPANY TIPS
# ─────────────────────────────────────

def generate_company_tips(company, job_role):

    prompt_template = PromptTemplate(
        input_variables=["company", "job_role"],
        template="""
You are an expert career coach with deep
knowledge of {company} interview process.

Give 5 SPECIFIC tips for interviewing at
{company} for a {job_role} position.

Include:
- What {company} values most in candidates
- Common mistakes to avoid
- What to research before the interview
- How to stand out from other candidates
- Questions to ask the interviewer

Format as numbered tips:
Tip 1: [tip title]
Details: [explanation]

Generate 5 company specific tips now:
"""
    )

    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "company": company,
        "job_role": job_role
    })
    return result


# ─────────────────────────────────────
# FUNCTION 5: MAIN FUNCTION
# ─────────────────────────────────────

def run_interview_prep_agent(
    company,
    job_role,
    job_description=""
):
    """
    Main function that runs the complete
    interview prep agent.

    Returns dict with:
    - technical questions
    - behavioral questions
    - system design questions
    - company tips
    """

    print(f"Starting Interview Prep Agent...")
    print(f"Company: {company} | Role: {job_role}")

    results = {}

    print("Generating technical questions...")
    results["technical"] = generate_technical_questions(
        company, job_role, job_description)

    print("Generating behavioral questions...")
    results["behavioral"] = generate_behavioral_questions(
        company, job_role)

    print("Generating system design questions...")
    results["system_design"] = generate_system_design_questions(
        company, job_role)

    print("Generating company tips...")
    results["tips"] = generate_company_tips(
        company, job_role)

    print("Interview prep complete!")
    return results, None


if __name__ == "__main__":
    print("Interview Prep Agent Ready!")