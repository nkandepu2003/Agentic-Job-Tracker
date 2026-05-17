# cover_letter_agent.py
# This agent writes a personalized cover letter
# based on your resume and the job description

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
import os
import sys
import io
from dotenv import load_dotenv
import fitz

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Add main project folder to path
sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Load secret keys from .env file
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

# Same Llama 3 model we used before
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.7,
    max_tokens=1024
)

# ─────────────────────────────────────
# FUNCTION 1: READ RESUME PDF
# Same function as tailor_agent
# ─────────────────────────────────────

def read_resume(pdf_path):
    """
    Opens your resume PDF and extracts all text.
    Exact same function as in tailor_agent.
    """
    if not os.path.exists(pdf_path):
        return None, (
            "Resume file not found! "
            "Make sure resume.pdf is in "
            "your main project folder."
        )
    try:
        pdf_document = fitz.open(pdf_path)
        full_text = ""
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            full_text += page.get_text()
        pdf_document.close()
        if not full_text.strip():
            return None, (
                "Resume PDF appears to be empty "
                "or contains only images."
            )
        return full_text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"


# ─────────────────────────────────────
# FUNCTION 2: WRITE COVER LETTER
# This is the main difference from tailor_agent
# Different prompt = different output
# ─────────────────────────────────────

def write_cover_letter(resume_text, job_description, company_name):
    """
    Sends resume + job description to Llama 3.
    Llama 3 writes a personalized cover letter.
    """

    prompt_template = PromptTemplate(
        input_variables=["resume", "job_description", "company_name"],
        template="""
You are an expert cover letter writer and career coach.

I will give you:
1. A candidate's resume
2. A job description they want to apply for
3. The company name

Your task:
Write a compelling, personalized cover letter that:
- Opens with a strong attention-grabbing paragraph
- Shows genuine interest in THIS specific company
- Highlights 2-3 most relevant experiences from resume
- Uses keywords from the job description naturally
- Shows personality while staying professional
- Ends with a confident call to action
- Is 3-4 paragraphs long (not too short, not too long)
- Does NOT use generic phrases like "I am writing to apply"
- Does NOT sound like a template
- Sounds like a real human wrote it

CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

COMPANY NAME:
{company_name}

Write the cover letter now.
Start directly with "Dear Hiring Manager,"
Make it sound genuine and specific to this role.

COVER LETTER:
"""
    )

    chain = prompt_template | llm | StrOutputParser()

    result = chain.invoke({
        "resume": resume_text,
        "job_description": job_description,
        "company_name": company_name
    })

    return result


# ─────────────────────────────────────
# FUNCTION 3: MAIN FUNCTION
# ─────────────────────────────────────

def run_cover_letter_agent(pdf_path, job_description, company_name):
    """
    Main function that runs the complete agent.

    Steps:
    1. Read resume PDF
    2. Write cover letter with Llama 3
    3. Return cover letter
    """

    # STEP 1: Read resume
    print("📄 Step 1: Reading your resume PDF...")
    resume_text, error = read_resume(pdf_path)
    if error:
        return None, error

    # STEP 2: Write cover letter
    print("✍️  Step 2: Writing cover letter with Llama 3...")
    try:
        cover_letter = write_cover_letter(
            resume_text,
            job_description,
            company_name
        )
    except Exception as e:
        return None, f"AI Error: {str(e)}"

    print("✅ Done! Cover letter ready!")
    return cover_letter, None


if __name__ == "__main__":
    print("Cover Letter Agent Ready!")
    print("Connect this to your dashboard to use it.")