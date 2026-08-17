from typing import Literal, Optional
from pydantic import BaseModel, Field

class AppResearchRecord(BaseModel):
  app_name: str = Field(description="Name of the application or service")
  category: str = Field(description="Category from the seed list (e.g., CRM and Sales)")
    one_line_summary: str = Field(description="What the app does in one concise sentence")
    auth_method: Literal["OAuth2", "API Key", "Basic", "Token", "Other", "Unknown"] = Field(
        description="Primary authentication mechanism supported"
    )
    access_model: Literal["Self-Serve Free/Trial", "Paid Plan Required", "Admin/Partner Gated", "Contact Sales"] = Field(
        description="Whether a developer can get credentials independently or is blocked"
    )
    api_surface: str = Field(description="API type (REST, GraphQL, etc.), approximate scope, or MCP existence")
    buildability_verdict: Literal["Ready Today", "Blocked", "Needs Outreach"] = Field(
        description="Feasibility of building an agent toolkit immediately"
    )
    blocker_reason: Optional[str] = Field(
        default=None, 
        description="Main blocker if not ready today (e.g., gated behind enterprise contract)"
    )
    evidence_url: str = Field(description="Official developer doc or pricing URL confirming the verdict")
