"""
Validation and normalization functions for processing raw JSON data from scrapers.
"""

import json
from typing import List, Dict, Any
from dataclasses import dataclass
import sys
import os

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Company, Email, Recruiter, RecruiterEmail, Job


@dataclass
class CompanyBundle:
    """
    Container for all SQLAlchemy model instances related to a single company.
    Used to normalize JSON data before database insertion.
    """
    company: Company
    emails: List[Email]
    recruiters: List[Recruiter]
    recruiter_emails: List[RecruiterEmail]
    jobs: List[Job]


def validate_fields(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Performs simple JSON field checking based on business requirements.

    Does:
        - Filters out recruiters without email AND linkedin
        - Filters out companies missing required fields
        - Keeps only valid components per company
        - If company data is invalid, omits entire company object

    Given: Raw array of JSON objects from data.json

    Returns: Validated and cleaned array of company objects (in dict form)

    Errors:
        - Returns empty list if input is None or empty
        - Logs skipped items but continues processing
    """
    if not raw_data:
        return []

    validated_companies = []

    for idx, company_obj in enumerate(raw_data):
        # Validate company has all required fields
        if not _is_valid_company(company_obj.get('company', {})):
            print(f"Skipping company at index {idx}: missing required company fields")
            continue

        # Create cleaned company object
        cleaned_company = {
            'company': company_obj['company'],
            'emails': company_obj.get('emails', []),
            'recruiters': [],
            'jobs': company_obj.get('jobs', [])
        }

        # Filter recruiters - must have email OR linkedin
        for recruiter in company_obj.get('recruiters', []):
            if _is_valid_recruiter(recruiter):
                cleaned_company['recruiters'].append(recruiter)
            else:
                print(f"Skipping recruiter {recruiter.get('fname', 'Unknown')} {recruiter.get('lname', '')}: no email or linkedin")

        validated_companies.append(cleaned_company)

    return validated_companies


def _is_valid_company(company_data: Dict[str, Any]) -> bool:
    """Check if company has all required fields present and non-empty."""
    required_fields = ['cname', 'company_size', 'category', 'company_city', 'company_state', 'company_description']

    for field in required_fields:
        if field not in company_data or company_data[field] is None or company_data[field] == '':
            return False

    return True


def _is_valid_recruiter(recruiter_data: Dict[str, Any]) -> bool:
    """Check if recruiter has at least email OR linkedin."""
    has_email = bool(recruiter_data.get('recruiter_emails'))
    has_linkedin = recruiter_data.get('linkedin') and recruiter_data['linkedin'] != 'Unknown'

    # Must have fname and lname
    if not recruiter_data.get('fname') or not recruiter_data.get('lname'):
        return False

    # Must have at least one contact method
    return has_email or has_linkedin


def normalize_json(validated_data: List[Dict[str, Any]]) -> List[CompanyBundle]:
    """
    Normalizes validated JSON into SQLAlchemy model instances.

    Does:
        - Transforms validated dicts into SQLAlchemy model objects
        - Creates Email objects for both company emails AND recruiter emails
        - Creates RecruiterEmail junction objects
        - Bundles all related objects per company

    Given: Return value from validate_fields (cleaned dict array)

    Returns: List of CompanyBundle objects, each containing all SQLAlchemy instances for one company

    Errors:
        - Returns empty list if input is None or empty
        - Skips malformed objects and logs errors
    """
    if not validated_data:
        return []

    bundles = []

    for company_data in validated_data:
        try:
            bundle = _create_company_bundle(company_data)
            bundles.append(bundle)
        except Exception as e:
            print(f"Error normalizing company {company_data.get('company', {}).get('cname', 'Unknown')}: {e}")
            continue

    return bundles


def _create_company_bundle(company_data: Dict[str, Any]) -> CompanyBundle:
    """Create a CompanyBundle with all related SQLAlchemy model instances."""

    # Create Company object
    company_dict = company_data['company']
    company = Company(
        cname=company_dict['cname'],
        company_size=company_dict['company_size'],
        category=company_dict['category'],
        company_city=company_dict['company_city'],
        company_state=company_dict['company_state'],
        company_description=company_dict['company_description'],
        contact_status=company_dict.get('contact_status', 'N/A')
    )

    # Track all emails (company emails + recruiter emails)
    all_emails = []
    email_objects_map = {}  # Map email address -> Email object

    # Create Email objects for company emails
    for email_data in company_data.get('emails', []):
        email = Email(
            email=email_data['email'],
            num_sent=email_data.get('num_sent', 0),
            num_replied=email_data.get('num_replied', 0),
            template_id=email_data.get('template_id'),
            last_date_sent=email_data.get('last_date_sent'),
            contact_status=email_data.get('contact_status', 'N/A')
        )
        all_emails.append(email)
        email_objects_map[email.email] = email

    # Create Recruiter objects and their associated emails
    recruiters = []
    recruiter_emails = []

    for recruiter_data in company_data.get('recruiters', []):
        recruiter = Recruiter(
            fname=recruiter_data['fname'],
            lname=recruiter_data['lname'],
            linkedin=recruiter_data.get('linkedin', 'Unknown')
        )
        recruiters.append(recruiter)

        # Create Email and RecruiterEmail objects for each recruiter email
        for rec_email_data in recruiter_data.get('recruiter_emails', []):
            email_addr = rec_email_data['email']

            # Create Email object for recruiter email (will go in emails table)
            if email_addr not in email_objects_map:
                email = Email(
                    email=email_addr,
                    num_sent=0,
                    num_replied=0,
                    template_id=None,
                    last_date_sent=None,
                    contact_status='N/A'
                )
                all_emails.append(email)
                email_objects_map[email_addr] = email

            # Create RecruiterEmail junction object
            recruiter_email = RecruiterEmail(
                email=email_addr
                # recruiter_id will be set after recruiter is inserted
            )
            recruiter_emails.append(recruiter_email)

    # Create Job objects
    jobs = []
    for job_data in company_data.get('jobs', []):
        job = Job(
            role_name=job_data['role_name'],
            source_url=job_data['source_url'],
            is_open=job_data.get('is_open', True)
        )
        jobs.append(job)

    return CompanyBundle(
        company=company,
        emails=all_emails,
        recruiters=recruiters,
        recruiter_emails=recruiter_emails,
        jobs=jobs
    )


def 
