import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_session
from db.queries import find_valid_emails


def get_stats() -> tuple[int, int, int]:
    """
    Get statistics about emails that can be sent.

    Returns:
        Tuple containing:
        - company_emails_count: Number of company emails that can be sent
        - recruiter_emails_count: Number of recruiter emails that can be sent
        - total_emails_count: Total number of emails that can be sent
    """
    with get_session() as session:
        # Get all valid emails from the database
        company_emails, company_ids, recruiter_emails, recruiter_company_ids = find_valid_emails(session)

        return (len(company_emails), len(recruiter_emails), len(company_emails) + len(recruiter_emails))
  