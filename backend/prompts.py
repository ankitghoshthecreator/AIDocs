from pydantic import BaseModel, Field

class SummaryResponse(BaseModel):
    executive_summary: str = Field(description="High-level summary of the contract or document context")
    parties: list[str] = Field(description="List of main parties involved or signing the agreement")
    execution_date: str = Field(description="The execution date, signing date, or effective date of the document")
    duration: str = Field(description="The duration, lifecycle, term, or termination timeline of the contract")
    total_value: str = Field(description="Total financial scale, transaction value, payment rate, or monetary limits if specified")
    core_obligations: str = Field(description="Primary duties, obligations, deliverables, or service scopes described")

class ClauseItem(BaseModel):
    name: str = Field(description="Legal clause standard category (e.g. Indemnity, Termination, Governing Law, Intellectual Property, Limitation of Liability, Force Majeure, Confidentiality, Dispute Resolution)")
    risk_level: str = Field(description="Risk scale of this clause: 'High', 'Medium', or 'Low'")
    risk_explanation: str = Field(description="Reasoning why this clause poses this risk to the parties involved")
    confidence_score: float = Field(description="Confidence score in the accuracy of this clause parsing (0.0 to 1.0)")
    exact_quote: str = Field(description="Verbatim exact copy of the text snippet containing the clause from the document")

class ClausesResponse(BaseModel):
    clauses: list[ClauseItem]

SUMMARY_SYSTEM_INSTRUCTION = """
You are an expert legal contract and document analyst. Analyze the provided text and populate the structured JSON fields.
Be concise but extract all critical facts. If any field is not mentioned in the text, put "Not specified".
"""

CLAUSE_SYSTEM_INSTRUCTION = """
You are an expert contract lawyer and risk auditor. Audit the provided contract text.
Identify standard contract clauses (e.g. Limitation of Liability, Indemnification, Intellectual Property, Termination, Governing Law, Confidentiality, Dispute Resolution, etc.).
Assess the risk level (High, Medium, Low) for each clause, detail the risk assessment, assign a parsing confidence score, and extract the exact quote verbatim from the text.
Return a list of these analyzed clauses.
"""
