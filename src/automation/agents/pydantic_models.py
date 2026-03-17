from pydantic import BaseModel, Field
from typing import Literal


class ResumeSelection(BaseModel):
    """Model for resume selection agent output."""
    resume_type: Literal['Backend', 'Fullstack', 'AI Engineer', 'Solutions', 'Machine Learning'] = Field(
        description="The most appropriate resume type for the company"
    )
    reasoning: str
