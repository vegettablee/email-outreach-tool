# System Overview for Personalized Cold-Email Internship Automation Tool 

Functional requirements: 
1. Must be able to send a personalized email given: 
- - personal information(name, school, year, major, expected graduation date)
- - experience/background info specific to the role 
- - email address 
- - resume file
2. Keep track of emails that are:
- - sent 
- - replied 
- - 
3. Extrapolate company info in the context of how I can contribute as an intern
- - separate into roles(backend, fullstack, data engineer, solutions engineer, ai engineer)
- - store company info as a context resource when sending cold emails
4. Multiple resumes based on their framing
- - backend, fullstack, data engineer, solutions engineer, ai engineer, mobile


Non-Functional requirements: 
1. Personalized emails can be framed based on different categories of roles.
2. Send follow up emails after x amount of days. 
3. Follow up email for normal internship application status updates.
4. Rate limiting for scraping company websites and sending emails(maybe like 20 every hour). 
5. Separate tool for tailoring resumes. 

Workflows required: 
- Company info research to gather useful information 
- Personalized email creator/sender 
--- Separating into two different workflows makes it easier when I need to focus on getting more leads to cold-email, and another one purely for how I want to personalize the email. So they can potentially run in parallel too.

Company-info Research Workflow: 
1. Agent scrapes company info, looks for:
- type of company(startup, mid-size, etc)
- open/past tech roles that match relevant experience 
- potential recruiter emails and/or linkedin profile links 
2. Insert relevant company info into SQL. 

Personalized Automation Email Generation Workflow: 
1. Pings the SQLite database for any emails that have not been sent yet. 
2. Put all emails into a queue and pull up company information tied with the emails. 
3. For each email in the queue, use company and personal info to draft a personalized email. 
4. Find most relevant resume and attach to the email.
5. Email gets sent to the recruiter/company.


Tech Stack: 
- SQLite
- Python
- Claude MCP

# Backend Architecture 

Main components
- tools
- - query the db and help make judgments 
- - google email tools  
- research workflow 
- - where it starts with a large json  
- rate limiting 


# Current Part in Progress

Instead of using an in-house scraper, use manual gemini pro thinking mode to return structured json based on a concentrated scraping scope/target(1-5 compannies at a time). 

JSON will mimic the fields in the DDL script look like for each separate entity and will always follow the same order: 

[
  {
  company : { Object }, 
  emails : [{ Object }], 
  recruiters : [{ Object }], 
  jobs : [{ Object }]
 }
]

Scraping rule guidelines: 
- IF company has information, find any non-recruiter company-tied emails first, these include: 
- 1. careers@ / hiring@ — most direct for job-related contact.
- 2. hr@ / people@ / talent@ — human gatekeepers who route internally.
- 3. Named leadership (CEO/Founder at smaller companies).
- 4. hello@ / info@ — catch-alls, lower deliverability but still valid.
- Continue to recruiters, look for emails tied to the 
- If a company lacks information, then look for at least one company-related email, but no emails/recruiters.


These rules apply to all entities besides company, and are the rules for returning JSON after scraping, in any case any of these rule are violated, return the entities affected as blank JSON with(ex. no recruiters found, return recruiters : [{ }]): 
- Recruiters must have an email or linkedin. 
- Open roles that qualify apply only to software related roles. 




Emails can be tied to the company directly or tied directly to a recruiter, who is then tied to the company. There are some important scenarios that should be considered to prevent collisions/invalid insertions, these include: 
- A company MUST exist before an email or recruiter is added to the DB 
- If a recruiter has an email, then the recruiter MUST be added to the database before inserting into the recruiter_emails table 
- If an email is found associated with an HR dept, then insert directly into the emails table 
- If a recruiter is found, but no email can be located, do not insert recruiter into the DB

Important checks before DB operations: 
- Check if an email exists within the emails table AND the recruiter_emails table before any kind of insertion/modification  
- Check status of both the email AND the recruiter, as they can be different depending on the company 

What all can happen that is based on what can be found based on the JSON information given? General flow:
- if Company email is found(ideally the HR dept): 
- Info about company is found(insert into DB)
- Recruiter is found without an email(recruiter does not get inserted)
- Recruiter is found with an email(insert recruiter/email)
- Job opening found(insert job for n amount of jobs if relevant)

Research needs to have a general flow, and if certain requirements are not met at certain steps, then drop the research for that company and mark as "NoInfo". But what counts as not enough information? The motivation for this, is if not enough information can be found within the first scrape, then drop it to save tokens/resources. 