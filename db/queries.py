# data abstraction layer for queries with conn and cursor

import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.models import Company, Email, Recruiter, Job


def check_email_exists(session: Session, email_address: str) -> Optional[Email]:
    """
    Check if an email exists in the database.

    Args:
        session: SQLAlchemy session
        email_address: Email address to check

    Returns:
        Email object if exists, None otherwise
    """
    return session.query(Email).filter_by(email=email_address).first()


def check_company_exists(session: Session, company_name: str) -> Optional[Company]:
    """
    Check if a company exists in the database by name.

    Args:
        session: SQLAlchemy session
        company_name: Company name to check

    Returns:
        Company object if exists, None otherwise
    """
    return session.query(Company).filter_by(cname=company_name).first()


def check_recruiter_exists(session: Session, fname: str, lname: str) -> Optional[Recruiter]:
    """
    Check if a recruiter exists in the database by first and last name.

    Args:
        session: SQLAlchemy session
        fname: First name
        lname: Last name

    Returns:
        Recruiter object if exists, None otherwise
    """
    return session.query(Recruiter).filter_by(fname=fname, lname=lname).first()


def check_job_exists(session: Session, source_url: str) -> Optional[Job]:
    """
    Check if a job exists in the database by source URL.

    Args:
        session: SQLAlchemy session
        source_url: Job posting URL to check

    Returns:
        Job object if exists, None otherwise
    """
    return session.query(Job).filter_by(source_url=source_url).first()


def get_unsent_emails_count(session: Session) -> int:
    """
    Get the count of emails where num_sent = 0.

    Args:
        session: SQLAlchemy session

    Returns:
        Count of unsent emails
    """
    return session.query(Email).filter_by(num_sent=0).count()


def get_recruiters_with_unsent_emails(session: Session) -> list[Recruiter]:
    """
    Query recruiter_emails table and find recruiters whose emails have num_sent = 0.

    Args:
        session: SQLAlchemy session

    Returns:
        List of Recruiter objects that have at least one unsent email
    """
    from src.models import RecruiterEmail

    # Join recruiter_emails -> emails -> filter by num_sent = 0
    # Then get the associated recruiters
    results = (
        session.query(Recruiter)
        .join(RecruiterEmail, Recruiter.recruiter_id == RecruiterEmail.recruiter_id)
        .join(Email, RecruiterEmail.email == Email.email)
        .filter(Email.num_sent == 0)
        .distinct()
        .all()
    )

    return results