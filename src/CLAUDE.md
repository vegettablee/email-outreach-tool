# Current Requirement in Progress: Draft Workflow Agent Implementation 

Workflow classes/functions: 

Class: DraftEmailWorkflow 
Responsibility: Contains all of the relevant functions/services to complete the email draft workflow
Dependencies: Needs data inside of database first 

class DraftEmailWorkflow: 

  def query_database() -> tuple (list, list): # this only gets run once for a batch of emails 
    # get all of the emails that can be sent(use queries.py) 
    # use these emails and run find_recruiter_emails(), emails returned are recruiter emails, and those not part of the original
    -- COMPLETED -- 
  
  def find_valid_emails(emails : list) -> tuple(list, list, list, list): 
    # takes a list of emails to check, the first element in the tuple contains the company emails, and the second list contains the company ids from the actual email, the third list is recruiter emails, the idea is that when checking if an email exists inside of the recruiter_email table, since it is a binary operation, these can be easily separated, the fourth list is the company_ids tied to the recruiter emails. need to keep track of the ids for context injection later for email personalization and other purposes
    -- COMPLETED -- 
  
  def get_company_context(company_email : str, company_id : int) -> dict:
    # use the company_id to query the company table and then pull the relevant data 
    # return context where context is a dictionary with the same fields as the COMPANY entity in the DDL script 
    -- COMPLETED -- 

  def get_recruiter_context(recruiter_email : str, company_id : int) -> dict: 
    # use the company_id to query the company table then pull relevant data 
    -- COMPLETED -- 

# -- Current focus on implementations: 

class AgentManager: 
-- Purpose: lazy initializes different agents/tools when called and returns them, or if they already exist just return 
-- Currently, this just contains the different placeholder agent initializations.

Orchestrator class: 
  def run_draft_email_workflow(self, email_count : int):
  - right now, the orchestrator is intializing the agent manager class, which contains the the agents/tools that can be run, and 
    are passed down to run_draft_agent inside of /agents/email_personalization.py
  
email_personalization.py: this file handles formatting context into a prompt, possibly retrieving relevant resumes, and running the actual API call in order to select which type of resume is most relevant based on the company decscription 
- function: run_draft_agent(context, agent, is_recruiter)
- - NEEDS COMPLETION



