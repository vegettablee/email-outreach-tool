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

Orchestration layer data flow in detail: 
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
  def query_database(): 
    # query database for company

  def  

def validate_fields() -> [dict]: 
  Does: [checks if all recruiters have an email AND/OR linkedin, checks that all company fields are filled as well]
  Given: [raw array of JSON objects inside of data.json]
  Returns: [validated raw JSON objects]
  Errors: [failure modes]