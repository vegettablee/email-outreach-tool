"""
Orchestration Layer for Cold Email Automation System

This module manages high-level workflows for the personalized cold-email internship automation tool.
It acts as the entry point for workflow requests and coordinates agents/services to complete tasks.

Responsibilities:
- Coordinate workflow execution
- Manage session state (DRAFT, REVIEW, QUEUED)
- Invoke appropriate agents and services
- Enforce rate limiting and boundaries(but how?)

Boundaries:
- Only knows which workflows can be used and when to use them
- Interacts with service layer and agents to complete tasks
- Does not directly call Gmail API or database operations
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enum import Enum
from typing import Dict, List, Any
from src.automation.workflows.draft_email import DraftEmailWorkflow
from src.automation.session_state import SessionState
from db.connection import get_session



class OrchestrationLayer:
  """
  Main orchestration class that manages all workflows for the cold email automation system.

  This class coordinates between agents, services, and the database to execute
  complete workflows such as company research, email drafting, sending, and follow-ups.

  Everything from this pulls directly from the 
  """

  def __init__(self):
    """
    Initialize the orchestration layer.
    """
    self.session = SessionState()
    # TODO later: 
    # read config.json for rate-limiting capabilities 

  def run_research_workflow(self): # might complete in future, depending on if its needed
    """
    Execute company research workflow.
    """
    pass

  def run_draft_email_workflow(self, email_count : int):
    db_session = get_session()
    if not db_session:
      return
    all_emails = DraftEmailWorkflow.query_database(db_session)
    company_emails = all_emails[0]
    company_email_ids = all_emails[1]
    recruiter_emails = all_emails[2]
    recruiter_email_company_ids = all_emails[3]

    num_to_draft = min(len(recruiter_emails) + len(company_emails), email_count)
    counter = 0 
    for c_idx, company_email in enumerate(company_emails):
      if counter == num_to_draft - 1: 
        break
      context = DraftEmailWorkflow.get_company_context(db_session, company_email, company_email_ids[c_idx])
      draft = DraftEmailWorkflow.draft_email(context=context, is_recruiter=False)
      self.session.add_draft(draft)
      counter += 1
    for r_idx, recruiter_email in enumerate(recruiter_emails):
      if counter == num_to_draft - 1: 
        break
      company_context = DraftEmailWorkflow.get_company_context(db_session, recruiter_email, recruiter_email_company_ids[r_idx])
      recruiter_context = DraftEmailWorkflow.get_recruiter_context(db_session, recruiter_email)
      context = {**company_context, **recruiter_context}
      draft = DraftEmailWorkflow.draft_email(context=context, is_recruiter=True)
      self.session.add_draft(draft)
      counter += 1

    db_session.close() 
  
  def run_review_email_workflow(self): 
    pass
  
  def run_queue_email_workflow(self):
    pass

  def run_cold_email_workflow(self):
    """
    Execute personalized cold email generation and sending workflow. This is for later, when the testing for the individual
    components work well such as the draft, review, and queue workflow are fully functional, then this will
    use an agent to execute the given tasks. 
    """
    pass

  def run_follow_up_email_workflow(self):
    """
    Execute follow-up email workflow for sent emails without replies.
    """
    pass

  def run_check_replies_workflow(self):
    """
    Execute workflow to check for email replies and update database.
    """
    pass 