# tailor_agent.py
# This agent reads your resume and tailors it
# to match any job description you paste

# ─────────────────────────────────────
# ALL IMPORTS AT THE TOP
# ─────────────────────────────────────
import os
import sys
import shutil
from dotenv import load_dotenv
import fitz
import chromadb

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=GROQ_API_KEY,
    temperature=0.7,
    max_tokens=1024
)

# ─────────────────────────────────────
# FUNCTION 1: READ RESUME PDF
# ─────────────────────────────────────

def read_resume(pdf_path):
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
                "or contains only images. "
                "Please use a text-based PDF."
            )
        return full_text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"


# ─────────────────────────────────────
# FUNCTION 2: STORE RESUME IN CHROMADB
# ─────────────────────────────────────

def store_resume_in_chromadb(resume_text):
    chroma_path = "chroma_db/resume"
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_text(resume_text)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=chroma_path)
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        client=client
    )
    return vectorstore


# ─────────────────────────────────────
# FUNCTION 3: TAILOR RESUME WITH LLAMA 3
# ─────────────────────────────────────

def tailor_resume(resume_text, job_description):
    prompt_template = PromptTemplate(
        input_variables=["resume", "job_description"],
        template="""
You are an expert resume writer and ATS optimization specialist.

TASK: Rewrite the candidate's resume to PERFECTLY match the job description.

RULES:
1. Replace weak bullet points with powerful action verbs
2. Add EXACT keywords from the job description
3. Quantify achievements wherever possible
4. Restructure experience to highlight relevant skills
5. Make SIGNIFICANT visible changes not subtle ones
6. Mirror the exact language used in job description
7. Do NOT add fake experience
8. Make it obvious this resume was written FOR this specific job

ORIGINAL RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

IMPORTANT: Make CLEAR and VISIBLE changes.
The tailored resume should look noticeably
different from the original.
Use keywords from the job description throughout.

TAILORED RESUME:
"""
    )
    chain = prompt_template | llm | StrOutputParser()
    result = chain.invoke({
        "resume": resume_text,
        "job_description": job_description
    })
    return result


# ─────────────────────────────────────
# FUNCTION 4: MAIN FUNCTION
# ─────────────────────────────────────

def run_tailor_agent(pdf_path, job_description):
    print("📄 Step 1: Reading your resume PDF...")
    resume_text, error = read_resume(pdf_path)
    if error:
        return None, error

    print("🧠 Step 2: Storing resume in ChromaDB...")
    try:
        store_resume_in_chromadb(resume_text)
    except Exception as e:
        print(f"ChromaDB warning: {str(e)}")
        print("Continuing without ChromaDB storage...")

    print("✍️  Step 3: Tailoring resume with Llama 3 AI...")
    try:
        tailored_resume = tailor_resume(
            resume_text,
            job_description
        )
    except Exception as e:
        return None, f"AI Error: {str(e)}"

    print("✅ Done! Tailored resume ready!")
    return tailored_resume, None


if __name__ == "__main__":
    print("Resume Tailor Agent Ready!")
    print("Connect this to your dashboard to use it.")