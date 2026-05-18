# models.py
# This file defines the structure of our database
# Think of it like designing a form before filling it in

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# This creates the foundation of our database
# Think of it like buying an empty filing cabinet
Base = declarative_base()

# This is ONE job application record
# Like ONE form in your filing cabinet
class JobApplication(Base):
    
    # Name of the table in database
    # Like the label on your filing cabinet drawer
    __tablename__ = "job_applications"
    
    # Each field below is ONE piece of information
    # Like one blank line on a paper form
    
    # Unique number for each application
    # Like a ticket number
    id = Column(Integer, primary_key=True)
    
    # Company you applied to
    company = Column(String, nullable=False)
    
    # Job title you applied for
    job_title = Column(String, nullable=False)
    
    # Link to the job posting
    job_url = Column(String, nullable=True)
    
    # Current status of application
    # Applied, Interview, Rejected, Offer
    status = Column(String, default="Applied")
    
    # Date you applied
    date_applied = Column(DateTime, default=datetime.now)
    
    # Date to follow up
    follow_up_date = Column(DateTime, nullable=True)
    
    # Any notes about this application
    notes = Column(String, nullable=True)
    
    # Location of the job
    location = Column(String, nullable=True)
    
    # Salary range if mentioned
    salary = Column(String, nullable=True)

# This creates the actual database file on your laptop
# Like physically buying and placing the filing cabinet
engine = create_engine("sqlite:///job_tracker.db")

# This creates all the tables we defined above
# Like drawing all the lines on the form
Base.metadata.create_all(engine)

# This lets us talk to the database
# Like opening the filing cabinet drawer
SessionLocal = sessionmaker(bind=engine)

# This function gives us a connection to database
# We use this everywhere in our project
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

print("Database is ready!")

def delete_application(app_id):
    """
    Deletes a job application from database.
    Like removing a form from your filing cabinet.
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