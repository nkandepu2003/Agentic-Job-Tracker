# interview_prep_agent.py
# This agent generates interview questions
# specific to a company and role
# Helps you prepare before every interview

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
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
    max_tokens=2048
)

# ─────────────────────────────────────
# FUNCTION 1: GENERATE TECHNICAL QUESTIONS
# ─────────────────────────────────────

def generate_technical_questions(company, job_role, job_description):
    """
    Generates technical interview questions
    specific to the company and role.

    Like having an insider who knows
    exactly what that company asks!
    """

    prompt_template = PromptTemplate(
        input_variables=["company", "job_role", "job_description"],
        template="""
You are an expert interview coach who knows
exactly what {company} asks in interviews
for {job_role} positions.

Generate 5 TECHNICAL interview questions
that {company} is likely to ask for this role.

Job Description Context:
{job_description}

Rules:
- Questions must be specific to {company} culture
- Focus on skills mentioned in job description
- Include ML/AI technical concepts
- Mix easy and hard questions
- For each question provide a brief hint
  on how to answer it

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
# FUNCTION 2: GENERATE BEHAVIORAL QUESTIONS
# ─────────────────────────────────────

def generate_behavioral_questions(company, job_role):
    """
    Generates behavioral interview questions.

    These are "Tell me about a time when..."
    type questions. Every company asks these!
    """

    prompt_template = PromptTemplate(
        input_variables=["company", "job_role"],
        template="""
You are an expert interview coach.

Generate 5 BEHAVIORAL interview questions
that {company} typically asks for {job_role}.

These should be STAR method questions:
Situation, Task, Action, Result

Rules:
- Make them specific to {company} values
- Focus on teamwork, leadership, problem solving
- Include real scenarios an ML engineer faces
- For each question explain what they are
  really looking for in the answer

Format each question like this:
Q1: [question]
They want to know: [what the interviewer is looking for]
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
# FUNCTION 3: GENERATE SYSTEM DESIGN QUESTIONS
# ─────────────────────────────────────

def generate_system_design_questions(company, job_role):
    """
    Generates system design questions.

    These test how you think about
    building large scale AI systems.
    """

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
- For each question provide a framework
  for how to approach the answer

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
# FUNCTION 4: GENERATE COMPANY TIPS
# ─────────────────────────────────────

def generate_company_tips(company, job_role):
    """
    Generates company specific interview tips.

    Like having a friend who works there
    giving you insider advice!
    """

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

    Steps:
    1. Generate technical questions
    2. Generate behavioral questions
    3. Generate system design questions
    4. Generate company specific tips
    5. Return everything organized

    Use this BEFORE every interview
    to prepare specifically for that company!
    """

    print(f"🎯 Starting Interview Prep Agent...")
    print(f"Company: {company} | Role: {job_role}")

    results = {}

    # STEP 1: Technical questions
    print("💻 Generating technical questions...")
    results["technical"] = generate_technical_questions(
        company, job_role, job_description)

    # STEP 2: Behavioral questions
    print("🤝 Generating behavioral questions...")
    results["behavioral"] = generate_behavioral_questions(
        company, job_role)

    # STEP 3: System design questions
    print("🏗️ Generating system design questions...")
    results["system_design"] = generate_system_design_questions(
        company, job_role)

    # STEP 4: Company tips
    print("💡 Generating company specific tips...")
    results["tips"] = generate_company_tips(
        company, job_role)

    print("✅ Interview prep complete!")
    return results, None


if __name__ == "__main__":
    print("Interview Prep Agent Ready!")
    print("Generates questions specific to company and role.")