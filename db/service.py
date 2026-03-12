"""
Database service layer for inserting company data.
Handles all insertion logic with proper dependency ordering.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Company, Email, Recruiter, RecruiterEmail, Job
from src.validation import CompanyBundle


def check_company_exists(session: Session, cname: str) -> Optional[Company]:
    """
    Placeholder function to check if company exists by name.

    TODO: Implement actual query later after initial test runs.
    Currently returns None (always insert new company).

    Args:
        session: SQLAlchemy session
        cname: Company name to check

    Returns:
        Company object if exists, None otherwise
    """
    # Placeholder - always return None for now
    return None


def insert_emails_batch(
    session: Session,
    company_id: int,
    emails: List[Email]
) -> int:
    """
    Inserts a batch of emails for a company.

    Args:
        session: SQLAlchemy session
        company_id: ID of the company these emails belong to
        emails: List of Email objects to insert

    Returns:
        Number of emails successfully inserted
    """
    inserted_count = 0

    for email in emails:
        # Set foreign key
        email.company_id = company_id

        try:
            session.add(email)
            session.flush()  # Try to insert
            inserted_count += 1
        except IntegrityError as e:
            # Email already exists (unique constraint violation)
            session.rollback()
            print(f"Skipping duplicate email: {email.email}")
            # Continue to next email

    return inserted_count


def insert_recruiters_with_emails(
    session: Session,
    recruiters: List[Recruiter],
    recruiter_emails: List[RecruiterEmail]
) -> Dict[str, int]:
    """
    Inserts recruiters and their associated recruiter_email junction records.

    Args:
        session: SQLAlchemy session
        recruiters: List of Recruiter objects
        recruiter_emails: List of RecruiterEmail objects (not yet linked to recruiter_id)

    Returns:
        Dict with counts: {'recruiters': int, 'recruiter_emails': int}
    """
    recruiters_inserted = 0
    recruiter_emails_inserted = 0

    # Build mapping of recruiter emails by recruiter index
    # (since recruiter_id isn't set yet, we need to track by position)
    recruiter_email_map = {}  # recruiter_index -> list of RecruiterEmail objects

    # Group recruiter_emails by which recruiter they belong to
    # This assumes normalize_json maintains order
    recruiter_idx = 0
    for rec_email in recruiter_emails:
        if recruiter_idx not in recruiter_email_map:
            recruiter_email_map[recruiter_idx] = []
        recruiter_email_map[recruiter_idx].append(rec_email)
        # Note: This is a simplification - you may need better logic
        # to match recruiter_emails to recruiters based on email address

    for idx, recruiter in enumerate(recruiters):
        try:
            # Insert recruiter
            session.add(recruiter)
            session.flush()  # Get recruiter_id
            recruiters_inserted += 1

            # Insert associated recruiter_emails
            if idx in recruiter_email_map:
                for rec_email in recruiter_email_map[idx]:
                    rec_email.recruiter_id = recruiter.recruiter_id

                    try:
                        session.add(rec_email)
                        session.flush()
                        recruiter_emails_inserted += 1
                    except IntegrityError as e:
                        # RecruiterEmail already exists or email doesn't exist
                        session.rollback()
                        print(f"Skipping duplicate recruiter_email: {rec_email.email}")

        except IntegrityError as e:
            session.rollback()
            print(f"Error inserting recruiter {recruiter.fname} {recruiter.lname}: {e}")
            continue

    return {
        'recruiters': recruiters_inserted,
        'recruiter_emails': recruiter_emails_inserted
    }


def insert_company_bundle(
    bundle: CompanyBundle,
    session: Session
) -> Dict[str, Any]:
    """
    Inserts all entities for one company in correct dependency order.

    Insertion order:
    1. Company (get company_id)
    2. Emails (need company_id)
    3. Recruiters (independent)
    4. RecruiterEmails (need recruiter_id and email to exist)
    5. Jobs (need company_id)

    Args:
        bundle: CompanyBundle containing all related entities
        session: SQLAlchemy session (managed by caller)

    Returns:
        Dict with insertion results:
        {
            'success': bool,
            'company_id': int,
            'company_name': str,
            'emails_inserted': int,
            'recruiters_inserted': int,
            'recruiter_emails_inserted': int,
            'jobs_inserted': int,
            'error': str | None
        }
    """
    result = {
        'success': False,
        'company_id': None,
        'company_name': bundle.company.cname,
        'emails_inserted': 0,
        'recruiters_inserted': 0,
        'recruiter_emails_inserted': 0,
        'jobs_inserted': 0,
        'error': None
    }

    try:
        # Step 1: Check if company exists (placeholder - currently always None)
        existing_company = check_company_exists(session, bundle.company.cname)

        if existing_company:
            print(f"Company '{bundle.company.cname}' already exists. Skipping.")
            result['company_id'] = existing_company.company_id
            result['error'] = 'Company already exists'
            return result

        # Step 2: Insert company
        session.add(bundle.company)
        session.flush()  # Get company_id without committing
        company_id = bundle.company.company_id
        result['company_id'] = company_id
        print(f"Inserted company: {bundle.company.cname} (ID: {company_id})")

        # Step 3: Insert emails (batch)
        emails_inserted = insert_emails_batch(session, company_id, bundle.emails)
        result['emails_inserted'] = emails_inserted
        print(f"Inserted {emails_inserted} emails")

        # Step 4: Insert recruiters with their emails
        recruiter_results = insert_recruiters_with_emails(
            session,
            bundle.recruiters,
            bundle.recruiter_emails
        )
        result['recruiters_inserted'] = recruiter_results['recruiters']
        result['recruiter_emails_inserted'] = recruiter_results['recruiter_emails']
        print(f"Inserted {recruiter_results['recruiters']} recruiters with {recruiter_results['recruiter_emails']} recruiter emails")

        # Step 5: Insert jobs
        for job in bundle.jobs:
            job.company_id = company_id
            session.add(job)

        session.flush()
        result['jobs_inserted'] = len(bundle.jobs)
        print(f"Inserted {len(bundle.jobs)} jobs")

        # Mark as successful
        result['success'] = True

    except Exception as e:
        result['error'] = str(e)
        print(f"Error inserting company bundle for '{bundle.company.cname}': {e}")
        raise  # Re-raise so caller can handle rollback

    return result


def clear_database(session: Session) -> Dict[str, Any]:
    """
    Clear all data from the database.

    Deletes all records from all tables in the correct order to avoid
    foreign key constraint violations. Uses cascade deletes where configured.

    Args:
        session: SQLAlchemy session

    Returns:
        Dict with deletion counts:
        {
            'success': bool,
            'companies_deleted': int,
            'emails_deleted': int,
            'recruiters_deleted': int,
            'recruiter_emails_deleted': int,
            'jobs_deleted': int,
            'error': str | None
        }
    """
    result = {
        'success': False,
        'companies_deleted': 0,
        'emails_deleted': 0,
        'recruiters_deleted': 0,
        'recruiter_emails_deleted': 0,
        'jobs_deleted': 0,
        'error': None
    }

    try:
        # Delete in reverse dependency order to avoid FK violations
        # Note: Since companies have cascade delete, deleting companies
        # will also delete emails and jobs automatically

        # Delete recruiter_emails first (depends on recruiters and emails)
        recruiter_emails_count = session.query(RecruiterEmail).delete()
        result['recruiter_emails_deleted'] = recruiter_emails_count

        # Delete recruiters (no dependencies)
        recruiters_count = session.query(Recruiter).delete()
        result['recruiters_deleted'] = recruiters_count

        # Delete jobs (depends on companies, but will be cascade deleted anyway)
        jobs_count = session.query(Job).delete()
        result['jobs_deleted'] = jobs_count

        # Delete emails (depends on companies, but will be cascade deleted anyway)
        emails_count = session.query(Email).delete()
        result['emails_deleted'] = emails_count

        # Delete companies last (has cascade delete configured)
        companies_count = session.query(Company).delete()
        result['companies_deleted'] = companies_count

        session.flush()
        result['success'] = True

        return result

    except Exception as e:
        result['error'] = str(e)
        raise  # Re-raise so caller can handle rollback 
