What all can happen that is based on what can be found based on the JSON information given? 
- Company email is found(ideally the HR dept)
- Info about company is found(insert into DB)
- Recruiter is found without an email(recruiter does not get inserted)
- Recruiter is found with an email(insert recruiter/email)
- Job opening found(insert job for n amount of jobs if relevant)

If no emails or recruiters can be located 

- A company MUST exist before an email or recruiter is added to the DB 
- If a recruiter has an email, then the recruiter MUST be added to the database before inserting into the recruiter_emails table 
- If an email is found associated with an HR dept, then insert directly into the emails table 
- If a recruiter is found, but no email can be located, do not insert recruiter into the DB