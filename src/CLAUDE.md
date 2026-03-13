# Current Requirement in Progress: First Commands/Workflows Integration and Basic rate Limiting 

Scope: The main focus for the commands/workflows that will be implemented is going to be the workflows for: 
- drafting emails, manully reviewing emails, and queueing emails to be sent via Gmail API 

Key CLI arguments for commands: 
- draft: number to draft
- review: number to review 
- queue: number to queue 

Orchestration Layer Architecture and Interaction Patterns: 

Orchestration Layer Implementation: 
- contains multiple classes that instantiate a workflow class, and simply call the relevant workflow classes with key fields that are required, one of these fields include a rate-limiting variable pulled from the config.json file. 

Orchestration layer data flow in more detail: 
1. Commands.py calls the orchestrator class with its relevant workflow(draft, review, queue) 
2. Orchestrator reads the config.json file and pulls the rate-limiting variables 
3. Orchestrator calls workflow function with relevant arguments, including the rate-limiting variables 
4. Workflow handles and return what was successfully completed: 
- Query database for data needed
- Coordinate multiple steps in sequence
- Call agents with prepared context
- Update session state
- Handle workflow-specific errors

Workflow classes/functions: 

Class: DraftEmailWorkflow 
Responsibility: Contains all of the relevant functions/services to complete the email draft workflow
Dependencies: Needs data inside of database first 

class DraftEmailWorkflow: 

  def query_database() -> tuple (list, list): # this only gets run once for a batch of emails 
    # get all of the emails that can be sent(use queries.py) 
    # use these emails and run find_recruiter_emails(), emails returned are recruiter emails, and those not part of the original
  
  def find_valid_emails(emails : list) -> tuple(list, list, list, list): 
    # takes a list of emails to check, the first element in the tuple contains the company emails, and the second list contains the company ids from the actual email, the third list is recruiter emails, the idea is that when checking if an email exists inside of the recruiter_email table, since it is a binary operation, these can be easily separated, the fourth list is the company_ids tied to the recruiter emails. need to keep track of the ids for context injection later for email personalization and other purposes
  
  def get_company_context(company_email : str, company_id : int) -> dict:
    # use the company_id to query the company table and then pull the relevant data 
    # return context where context is a dictionary with the same fields as the COMPANY entity in the DDL script 

  def get_recruiter_context(recruiter_email : str, company_id : int) -> dict: 
    # use the company_id to query the company table then pull relevant data 

  def draft_email(context, is_recruiter : bool) -> dict: # leave this blank for now until the logic is decided for the agent  
    # run a SQL query that uses company_id and pulls relevant company description fields for context(implement in queries.py and call here)
    # check if is_recruiter is True then run email personalization agent for company emails only, else run email personalization for recruiter emails only, do not worry about the

  







