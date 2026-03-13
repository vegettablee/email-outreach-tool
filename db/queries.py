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

def get_company(session: Session, company_id: int) -> dict:
    """
    Get company information by company_id.

    Args:
        session: SQLAlchemy session
        company_id: Company ID to retrieve

    Returns:
        Dictionary containing company fields (excluding relationships):
        {
            'company_id': int,
            'cname': str,
            'company_website': str,
            'company_size': str,
            'category': str,
            'company_city': str,
            'company_state': str,
            'company_description': str,
            'contact_status': str
        }
        Returns None if company not found.
    """
    company = session.query(Company).filter_by(company_id=company_id).first()

    if not company:
        return None

    return {
        'company_id': company.company_id,
        'cname': company.cname,
        'company_website': company.company_website,
        'company_size': company.company_size,
        'category': company.category,
        'company_city': company.company_city,
        'company_state': company.company_state,
        'company_description': company.company_description,
        'contact_status': company.contact_status
    }

def get_recruiter_email(session: Session, recruiter_email: str) -> int:
    """
    Get recruiter_id from a recruiter email address.

    Args:
        session: SQLAlchemy session
        recruiter_email: Recruiter email address

    Returns:
        recruiter_id (int) if found, None otherwise
    """
    from src.models import RecruiterEmail

    result = session.query(RecruiterEmail).filter_by(email=recruiter_email).first()

    if not result:
        return None

    return result.recruiter_id 

def get_recruiter(session: Session, recruiter_id: int) -> dict:
    """
    Get recruiter information by recruiter_id.

    Args:
        session: SQLAlchemy session
        recruiter_id: Recruiter ID to retrieve

    Returns:
        Dictionary containing recruiter fields (excluding relationships):
        {
            'recruiter_id': int,
            'fname': str,
            'lname': str,
            'linkedin': str
        }
        Returns None if recruiter not found.
    """
    recruiter = session.query(Recruiter).filter_by(recruiter_id=recruiter_id).first()

    if not recruiter:
        return None

    return {
        'recruiter_id': recruiter.recruiter_id,
        'fname': recruiter.fname,
        'lname': recruiter.lname,
        'linkedin': recruiter.linkedin
    }


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

