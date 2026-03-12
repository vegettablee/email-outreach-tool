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

def get_companies_not_contacted(session: Session) -> list[Company]:
    pass


def find_valid_emails(session: Session) -> tuple[list[str], list[int], list[str], list[int]]:
    """
    Find all contactable, unsent emails and separate them into company emails and recruiter emails.

    This function performs a LEFT JOIN between emails and recruiter_emails tables to identify
    which emails are tied directly to companies vs. tied to recruiters.

    Args:
        session: SQLAlchemy session

    Returns:
        Tuple containing:
        - company_emails: List of email addresses tied directly to companies
        - company_ids: List of company IDs corresponding to company_emails
        - recruiter_emails: List of email addresses tied to recruiters
        - recruiter_company_ids: List of company IDs corresponding to recruiter_emails
    """
    from src.models import RecruiterEmail
    from sqlalchemy import case

    # Single query with LEFT JOIN to get all emails and mark recruiter emails
    results = (
        session.query(
            Email.email,
            Email.company_id,
            case(
                (RecruiterEmail.email.isnot(None), 1),
                else_=0
            ).label('is_recruiter')
        )
        .outerjoin(RecruiterEmail, Email.email == RecruiterEmail.email)
        .filter(Email.contact_status == 'N/A')
        .filter(Email.num_sent == 0)
        .all()
    )

    # Separate into company emails and recruiter emails
    company_emails = []
    company_ids = []
    recruiter_emails = []
    recruiter_company_ids = []

    for row in results:
        if row.is_recruiter == 1:
            recruiter_emails.append(row.email)
            recruiter_company_ids.append(row.company_id)
        else:
            company_emails.append(row.email)
            company_ids.append(row.company_id)

    return (company_emails, company_ids, recruiter_emails, recruiter_company_ids) 

