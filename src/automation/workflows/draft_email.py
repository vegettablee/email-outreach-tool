"""
DraftEmailWorkflow - Handles the email drafting workflow.

Responsibilities:
- Query database for emails that can be sent
- Find valid emails (company vs recruiter emails)
- Get company/recruiter context for personalization
- Draft personalized emails using AI agents
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List, Tuple
from db.connection import get_session
from db.queries import find_valid_emails, get_company, get_recruiter, get_recruiter_email


class DraftEmailWorkflow:
    """
    Workflow class for helping draft personalized cold emails.

    This class coordinates the process of:
    1. Querying the database for valid emails
    2. Separating company emails from recruiter emails
    3. Getting context for personalization
    4. Structuring context for agent 
    """

    def __init__(self, rate_limit: int = 20):
        """
        Initialize the draft email workflow.

        Args:
            rate_limit: Number of emails to draft per batch (default: 20)
        """
        self.rate_limit = rate_limit

    @staticmethod
    def query_database(session) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Query database for all emails that can be sent.

        This only gets run once for a batch of emails.

        Args:
            session: SQLAlchemy session

        Returns:
            Tuple containing:
            - company_emails: List of company email addresses
            - company_ids: List of company IDs for company emails
            - recruiter_emails: List of recruiter email addresses
            - recruiter_company_ids: List of company IDs for recruiter emails
        """
        return find_valid_emails(session)

    @staticmethod
    def find_valid_emails(emails: List[str]) -> Tuple[List[str], List[int], List[str], List[int]]:
        """
        Takes a list of emails to check and separates them into company vs recruiter emails.

        Args:
            emails: List of email addresses to validate

        Returns:
            Tuple containing:
            - company_emails: List of email addresses tied directly to companies
            - company_ids: List of company IDs from the actual email (for context injection)
            - recruiter_emails: List of recruiter email addresses
            - recruiter_company_ids: List of company IDs tied to the recruiter emails

        Note:
            Since checking if an email exists in the recruiter_email table is a binary operation,
            these can be easily separated. Need to keep track of the IDs for context injection
            later for email personalization and other purposes.
        """
        # TODO: Implement logic to validate emails and separate them
        # This is a placeholder implementation
        pass

    @staticmethod
    def get_company_context(session, company_email: str, company_id: int) -> Dict:
        """
        Get company context for email personalization.

        Uses the company_id to query the company table and pull relevant data.

        Args:
            session: SQLAlchemy session
            company_email: The company email address
            company_id: The company ID to query

        Returns:
            Dictionary with the same fields as the COMPANY entity in the DDL script
        """
        return get_company(session, company_id)

    @staticmethod
    def get_recruiter_context(session, recruiter_email: str) -> Dict:
        """
        Get recruiter context for email personalization.

        Uses the recruiter_email on the recruiter_emails table to get the recruiter_id and then find the recruiter_id information

        Args:
            session: SQLAlchemy session
            recruiter_email: The recruiter email address

        Returns:
            Dictionary containing recruiter information
        """
        # First get the recruiter_id from the recruiter_email
        recruiter_id = get_recruiter_email(session, recruiter_email)

        if not recruiter_id:
            return None

        # Then get the full recruiter information
        return get_recruiter(session, recruiter_id)

    @staticmethod
    def draft_email(context: Dict, is_recruiter: bool) -> Dict:
        """
        Draft a personalized email using AI agent.

        Leave this blank for now until the logic is decided for the agent.

        Args:
            context: Context dictionary containing company/recruiter information
            is_recruiter: True if drafting for recruiter, False if for company

        Returns:
            Dictionary containing the drafted email details

        Note:
            - Run a SQL query that uses company_id and pulls relevant company description
              fields for context (implement in queries.py and call here)
            - If is_recruiter is True, run email personalization agent for recruiter emails
            - If is_recruiter is False, run email personalization agent for company emails
        """
        # TODO: Implement email drafting logic with AI agent
        pass

    def run(self, count: int = None) -> Dict:
        """
        Execute the draft email workflow.

        Args:
            count: Number of emails to draft (defaults to rate_limit if not specified)

        Returns:
            Dictionary with workflow results:
            {
                'success': bool,
                'drafts_created': int,
                'company_drafts': int,
                'recruiter_drafts': int,
                'error': str | None
            }
        """
        if count is None:
            count = self.rate_limit

        result = {
            'success': False,
            'drafts_created': 0,
            'company_drafts': 0,
            'recruiter_drafts': 0,
            'error': None
        }

        try:
            # TODO: Implement workflow execution
            # 1. Query database
            # 2. Get contexts
            # 3. Draft emails
            # 4. Save drafts to session state

            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result
