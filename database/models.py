# models.py
# This file defines the structure of our database
# Updated to use Supabase (cloud) or SQLite (local)

import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


# ─────────────────────────────────────
# DATABASE CONNECTION
# Uses Supabase when deployed
# Uses SQLite when running locally
# ─────────────────────────────────────

def get_database_url():
    """
    Gets the correct database URL.
    Deployed: uses Supabase (cloud, persistent)
    Local: uses SQLite (file on laptop)
    """
    try:
        import streamlit as st
        db_url = st.secrets.get(
            "DATABASE_URL",
            os.getenv("DATABASE_URL")
        )
        if db_url:
            return db_url
    except Exception:
        pass

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # Fall back to SQLite for local development
    return "sqlite:///job_tracker.db"


DATABASE_URL = get_database_url()

# Create engine based on database type
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Supabase/PostgreSQL
    engine = create_engine(DATABASE_URL)

# ─────────────────────────────────────
# DATABASE MODELS
# ─────────────────────────────────────

Base = declarative_base()


class JobApplication(Base):
    """
    One job application record.
    Like one form in your filing cabinet.
    """
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_url = Column(String, nullable=True)
    status = Column(String, default="Applied")
    date_applied = Column(DateTime, default=datetime.now)
    follow_up_date = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    location = Column(String, nullable=True)
    salary = Column(String, nullable=True)


# Create all tables
Base.metadata.create_all(engine)

# Database session
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """
    Returns a database connection.
    Works with both SQLite and Supabase.
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass


def delete_application(app_id):
    """
    Deletes a job application from database.
    """
    db = SessionLocal()
    try:
        app = db.query(JobApplication).filter(
            JobApplication.id == app_id
        ).first()
        if app:
            db.delete(app)
            db.commit()
            return True
        return False
    finally:
        db.close()