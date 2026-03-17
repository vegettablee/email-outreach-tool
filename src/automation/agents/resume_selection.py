# handles agent workflows related to resume selection based on company information
# this agent is responsible for choosing the most appropriate resume type given company context

from typing import Dict, Tuple, Optional

resume_options = ['Backend', 'Fullstack', 'AI Engineer', 'Solutions', 'Machine Learning']
resume_options_real = ['Backend', 'Fullstack', 'AI Engineer', 'Solutions', 'Machine Learning'] # default to fullstack for now, needs to be wired with the actual drafting agent 

def run_resume_selection_agent(context: dict, agent: any, is_recruiter: bool) -> Tuple[bool, Optional[str]]:
    """
    Run the resume selection agent to choose the most appropriate resume type.

    Args:
        context: Dictionary containing company/recruiter information
        agent: PydanticAI Agent instance for resume selection
        is_recruiter: True if context includes recruiter info, False if company only

    Returns:
        Tuple of (success: bool, resume_type: str or None)
        - success: True if the agent successfully selected a resume
        - resume_type: One of resume_options if successful, None otherwise
    """
    try:
        # Generate instruction prompt based on context
        instruction_prompt = generate_instruction_prompt(context, is_recruiter)

        # Make API call using PydanticAI's run_sync method
        result = agent.run_sync(instruction_prompt)

        # Extract the selected resume type from result
        # result.output is a ResumeSelection Pydantic model
        resume_type = result.output.resume_type
        reasoning = result.output.reasoning
        print(f"Selected resume: {resume_type}")
        print(f"Reasoning: {reasoning}")

        # The resume_type is already validated by the Pydantic model's Literal type
        return (True, resume_type)

    except Exception as e:
        print(f"Error in run_draft_agent: {str(e)}")
        return (False, None) 


def generate_instruction_prompt(context: dict, is_recruiter: bool) -> str:
    """
    Generate the instruction prompt for the resume selection agent.

    Args:
        context: Dictionary containing company/recruiter information
        is_recruiter: True if context includes recruiter info, False if company only

    Returns:
        Formatted instruction prompt string for the agent
    """
    # Get personal context (tech stack, experiences, projects) to help with resume selection
    personal_context = get_personal_context()

    # Extract company information from context
    company_name = context.get('cname', 'the company')
    company_description = context.get('company_description', 'N/A')
    company_size = context.get('company_size', 'N/A')
    company_category = context.get('category', 'N/A')
    company_location = f"{context.get('company_city', '')}, {context.get('company_state', '')}".strip(', ')

    # Build the prompt - for now, treat recruiter and company contexts the same
    # (as noted in original comments, recruiter-specific handling may be added later if LinkedIn context is useful)
    prompt = f"""You are selecting the most appropriate resume type for a cold email to a company.

# Your Background
{personal_context}

# Available Resume Types
{', '.join(resume_options)}

# Company Information
- Company Name: {company_name}
- Description: {company_description}
- Size: {company_size}
- Category: {company_category}
- Location: {company_location}

# Task
Based on the company information and your background, select the single most appropriate resume type that:
1. Best aligns with the company's description and category
2. Highlights your most relevant experience for this type of company
3. Maximizes your chances of getting a response

# Guidelines for Selection
- If company information is limited or unclear, choose a generally safe option (e.g., 'Fullstack' or 'Backend')
- Consider the company's category and size when making your decision
- Match the resume type to what the company likely needs based on their description

# Output Format
Provide your response in the following JSON format:
{{
    "resume_type": "One of: Backend, Fullstack, AI Engineer, Solutions, Machine Learning",
    "reasoning": "Brief 1-sentence explanation for your choice"
}}
"""

    return prompt 


def get_personal_context() -> str:
    """
    Returns personal context including tech stack, experiences, and projects.
    This helps the agent make informed decisions when selecting a resume type.
    Kept in a separate function for easy updates when experiences change.

    Returns:
        Formatted string containing personal background information
    """
    context = """## Education
University of Texas at Dallas, Computer Science, Expected Graduation: 2027

## Tech Stack
- Backend: Python, Node.js/Express.js, Spring Boot, SQL (PostgreSQL, SQLite, MongoDB)
- Frontend: React.js, React Native, SwiftUI, TypeScript, JavaScript
- ML/AI: PyTorch, Hugging Face Transformers, FAISS, Pydantic AI
- Cloud/Tools: AWS (S3, CloudFront), Docker, Git, CI/CD

## Experiences
- **OrbitalMentorship (Software Engineer Intern)**: Built analytics dashboard with Express.js/React.js aggregating user metrics; designed MongoDB schema (29+ entities); developed file processing system with AWS S3/CloudFront for resume/assignment management.
- **ACM Research (CTURC Selected Presenter)**: Implemented prompt compression pipeline for Llama-2-7b using truncated SVD; benchmarked 36.9% faster inference vs LLMLingua2; presented research to judging panel.

## Projects
- **Internship Email Automation Agent**: Python CLI tool that automates personalized cold email outreach to 200+ companies using multi-agent workflow system (draft → review → queue → send → track). Uses Pydantic AI agents to select appropriate resumes and personalize emails based on company context, with SQLite database tracking all contacts and Gmail API integration for sending.
- **iMessage RAG Query System**: Built a RAG chatbot with Chainlit interface that lets you query your iMessage history using natural language. Implemented conversation chunking pipeline with FAISS vector storage and trained a custom ML model (4-head self-attention) to reconstruct conversation threads with 74.2% F1 accuracy.
- **Skill Swap Social Media App**: Led system design for a React Native/Spring Boot/MongoDB social media platform enabling users to exchange skills through video sharing and messaging.
- **Thrift Store Discovery App**: Full-stack app that helps discover thrift stores based on style, inventory type, and community focus. Built Node.js/Express backend that uses GPT-4 to categorize stores from Google Places API, with iOS/MapKit frontend for browsing.
"""

    return context  