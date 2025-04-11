from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime

# Base financial schemas
class FinancialProfileBase(BaseModel):
    annual_income: float = Field(..., gt=0)
    filing_status: str
    dependents: int = Field(0, ge=0)
    investments: Optional[Dict[str, Any]] = {}
    retirement_accounts: Optional[Dict[str, Any]] = {}

class FinancialProfileCreate(FinancialProfileBase):
    user_id: int
    
class FinancialProfileResponse(FinancialProfileBase):
    id: int
    user_id: int
    external_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True

# Tax document schemas
class TaxDocumentBase(BaseModel):
    document_type: str
    document_data: Dict[str, Any]
    year: int
    
    @validator('year')
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 1:
            raise ValueError(f'Year must be between 2000 and {current_year + 1}')
        return v

class TaxDocumentCreate(TaxDocumentBase):
    user_id: int
    
class TaxDocumentResponse(TaxDocumentBase):
    id: int
    user_id: int
    external_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True

# Financial recommendation schemas
class FinancialRecommendationBase(BaseModel):
    recommendation_type: str
    title: str
    description: str
    potential_impact: Optional[float]
    asl_video_id: Optional[str]

class FinancialRecommendationCreate(FinancialRecommendationBase):
    financial_profile_id: int
    
class FinancialRecommendationResponse(FinancialRecommendationBase):
    id: int
    financial_profile_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# April API request/response schemas
class AprilAuthRequest(BaseModel):
    grant_type: str = "client_credentials"
    client_id: str
    client_secret: str

class AprilAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class AprilTaxFilingRequest(BaseModel):
    user_id: str
    tax_year: int
    documents: List[Dict[str, Any]]

class AprilFinancialProfileRequest(BaseModel):
    user_id: str
    income_data: Dict[str, Any]
    filing_status: str
    dependents: int

class AprilProductEngagementRequest(BaseModel):
    user_id: str
    product_id: str
    interaction_data: Dict[str, Any]
