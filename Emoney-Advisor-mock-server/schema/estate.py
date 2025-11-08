from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class EstateStatus(str, Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    ARCHIVED = "Archived"
    EXECUTED = "Executed"


# Base schemas
class EstateBase(BaseModel):
    client_id: str = Field(..., description="ID of client estate belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    financial_plan_id: Optional[str] = Field(None, description="ID of financial plan")
    status: str = Field(..., description="Estate status")
    complexity: str = Field(..., description="Estate complexity")
    marital_status: str = Field(..., description="Marital status")
    total_estate_value: float = Field(..., description="Total estate value")
    taxable_estate: Optional[float] = Field(None, description="Taxable estate value")
    estimated_tax: Optional[float] = Field(None, description="Estimated tax")
    tax_status: Optional[str] = Field(None, description="Tax status")
    asset_composition: Optional[Dict[str, Any]] = Field(None, description="Asset composition")
    state_of_residence: Optional[str] = Field(None, description="State of residence")
    has_will: bool = Field(False, description="Whether client has will")
    has_trust: bool = Field(False, description="Whether client has trust")
    has_power_of_attorney: bool = Field(False, description="Whether client has power of attorney")
    has_healthcare_directive: bool = Field(False, description="Whether client has healthcare directive")
    has_beneficiary_designations: bool = Field(False, description="Whether client has beneficiary designations")
    last_review_date: Optional[date] = Field(None, description="Last review date")
    next_review_date: Optional[date] = Field(None, description="Next review date")
    planning_objectives: Optional[Dict[str, Any]] = Field(None, description="Planning objectives")
    planning_strategies: Optional[Dict[str, Any]] = Field(None, description="Planning strategies")
    documents: Optional[Dict[str, Any]] = Field(None, description="Documents")
    advisors: Optional[Dict[str, Any]] = Field(None, description="Advisors")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the estate")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the estate")


class WillBase(BaseModel):
    estate_id: str = Field(..., description="ID of estate will belongs to")
    client_id: str = Field(..., description="ID of client will belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Will status")
    type: str = Field(..., description="Will type")
    execution_date: Optional[date] = Field(None, description="Execution date")
    last_updated: Optional[date] = Field(None, description="Last update date")
    location: Optional[str] = Field(None, description="Storage location")
    executor: Optional[Dict[str, Any]] = Field(None, description="Executor information")
    alternate_executor: Optional[Dict[str, Any]] = Field(None, description="Alternate executor information")
    guardian_for_minors: Optional[Dict[str, Any]] = Field(None, description="Guardian for minors")
    specific_bequests: Optional[Dict[str, Any]] = Field(None, description="Specific bequests")
    residuary_estate: Optional[Dict[str, Any]] = Field(None, description="Residuary estate")
    testamentary_trust: bool = Field(False, description="Whether will includes testamentary trust")
    no_contest_clause: bool = Field(False, description="Whether will includes no contest clause")
    digital_assets: bool = Field(False, description="Whether will includes digital assets")
    pet_provisions: bool = Field(False, description="Whether will includes pet provisions")
    charitable_provisions: bool = Field(False, description="Whether will includes charitable provisions")
    special_instructions: Optional[str] = Field(None, description="Special instructions")
    attorney: Optional[Dict[str, Any]] = Field(None, description="Attorney information")
    document_id: Optional[str] = Field(None, description="Document ID")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the will")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the will")


class TrustBase(BaseModel):
    estate_id: str = Field(..., description="ID of estate trust belongs to")
    client_id: str = Field(..., description="ID of client trust belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Trust name")
    status: str = Field(..., description="Trust status")
    trust_type: str = Field(..., description="Trust type")
    purpose: Optional[str] = Field(None, description="Trust purpose")
    execution_date: Optional[date] = Field(None, description="Execution date")
    amendment_date: Optional[date] = Field(None, description="Amendment date")
    location: Optional[str] = Field(None, description="Storage location")
    grantor: Optional[Dict[str, Any]] = Field(None, description="Grantor information")
    co_grantor: Optional[Dict[str, Any]] = Field(None, description="Co-grantor information")
    trustee: Optional[Dict[str, Any]] = Field(None, description="Trustee information")
    successor_trustee: Optional[Dict[str, Any]] = Field(None, description="Successor trustee information")
    is_funded: bool = Field(False, description="Whether trust is funded")
    trust_value: Optional[float] = Field(None, description="Trust value")
    funding_source: Optional[Dict[str, Any]] = Field(None, description="Funding source")
    distribution_provisions: Optional[Dict[str, Any]] = Field(None, description="Distribution provisions")
    spendthrift_provision: bool = Field(False, description="Whether trust includes spendthrift provision")
    generation_skipping: bool = Field(False, description="Whether trust includes generation skipping")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    tax_filing_requirements: Optional[Dict[str, Any]] = Field(None, description="Tax filing requirements")
    attorney: Optional[Dict[str, Any]] = Field(None, description="Attorney information")
    document_id: Optional[str] = Field(None, description="Document ID")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the trust")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the trust")


class BeneficiaryBase(BaseModel):
    estate_id: str = Field(..., description="ID of estate beneficiary belongs to")
    client_id: str = Field(..., description="ID of client beneficiary belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    will_id: Optional[str] = Field(None, description="ID of will beneficiary belongs to")
    trust_id: Optional[str] = Field(None, description="ID of trust beneficiary belongs to")
    name: str = Field(..., description="Beneficiary name")
    type: str = Field(..., description="Beneficiary type")
    relationship: str = Field(..., description="Relationship to client")
    status: str = Field(..., description="Beneficiary status")
    primary: bool = Field(True, description="Whether beneficiary is primary")
    contingent: bool = Field(False, description="Whether beneficiary is contingent")
    percentage: float = Field(..., description="Percentage of assets")
    priority: int = Field(..., description="Priority order")
    asset_types: Optional[Dict[str, Any]] = Field(None, description="Asset types")
    specific_assets: Optional[Dict[str, Any]] = Field(None, description="Specific assets")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the beneficiary")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the beneficiary")


# Response models with ID and timestamps
class EstateResponse(BaseModel):
    id: str = Field(..., description="Estate ID")
    clientId: str = Field(..., description="ID of client estate belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    financialPlanId: Optional[str] = Field(None, description="ID of financial plan")
    status: str = Field(..., description="Estate status")
    complexity: str = Field(..., description="Estate complexity")
    maritalStatus: str = Field(..., description="Marital status")
    totalEstateValue: float = Field(..., description="Total estate value")
    taxableEstate: Optional[float] = Field(None, description="Taxable estate value")
    estimatedTax: Optional[float] = Field(None, description="Estimated tax")
    taxStatus: Optional[str] = Field(None, description="Tax status")
    assetComposition: Optional[Dict[str, Any]] = Field(None, description="Asset composition")
    stateOfResidence: Optional[str] = Field(None, description="State of residence")
    hasWill: bool = Field(False, description="Whether client has will")
    hasTrust: bool = Field(False, description="Whether client has trust")
    hasPowerOfAttorney: bool = Field(False, description="Whether client has power of attorney")
    hasHealthcareDirective: bool = Field(False, description="Whether client has healthcare directive")
    hasBeneficiaryDesignations: bool = Field(False, description="Whether client has beneficiary designations")
    lastReviewDate: Optional[date] = Field(None, description="Last review date")
    nextReviewDate: Optional[date] = Field(None, description="Next review date")
    planningObjectives: Optional[Dict[str, Any]] = Field(None, description="Planning objectives")
    planningStrategies: Optional[Dict[str, Any]] = Field(None, description="Planning strategies")
    documents: Optional[Dict[str, Any]] = Field(None, description="Documents")
    advisors: Optional[Dict[str, Any]] = Field(None, description="Advisors")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the estate")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the estate")
    createdAt: datetime = Field(..., description="Timestamp when estate was created")
    updatedAt: datetime = Field(..., description="Timestamp when estate was last updated")
    
    model_config = {
        "from_attributes": True
    }


class WillResponse(BaseModel):
    id: str = Field(..., description="Will ID")
    estateId: str = Field(..., description="ID of estate will belongs to")
    clientId: str = Field(..., description="ID of client will belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Will status")
    type: str = Field(..., description="Will type")
    executionDate: Optional[date] = Field(None, description="Execution date")
    lastUpdated: Optional[date] = Field(None, description="Last update date")
    location: Optional[str] = Field(None, description="Storage location")
    executor: Optional[Dict[str, Any]] = Field(None, description="Executor information")
    alternateExecutor: Optional[Dict[str, Any]] = Field(None, description="Alternate executor information")
    guardianForMinors: Optional[Dict[str, Any]] = Field(None, description="Guardian for minors")
    specificBequests: Optional[Dict[str, Any]] = Field(None, description="Specific bequests")
    residuaryEstate: Optional[Dict[str, Any]] = Field(None, description="Residuary estate")
    testamentaryTrust: bool = Field(False, description="Whether will includes testamentary trust")
    noContestClause: bool = Field(False, description="Whether will includes no contest clause")
    digitalAssets: bool = Field(False, description="Whether will includes digital assets")
    petProvisions: bool = Field(False, description="Whether will includes pet provisions")
    charitableProvisions: bool = Field(False, description="Whether will includes charitable provisions")
    specialInstructions: Optional[str] = Field(None, description="Special instructions")
    attorney: Optional[Dict[str, Any]] = Field(None, description="Attorney information")
    documentId: Optional[str] = Field(None, description="Document ID")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the will")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the will")
    createdAt: datetime = Field(..., description="Timestamp when will was created")
    updatedAt: datetime = Field(..., description="Timestamp when will was last updated")
    
    model_config = {
        "from_attributes": True
    }


class TrustResponse(BaseModel):
    id: str = Field(..., description="Trust ID")
    estateId: str = Field(..., description="ID of estate trust belongs to")
    clientId: str = Field(..., description="ID of client trust belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Trust name")
    status: str = Field(..., description="Trust status")
    trustType: str = Field(..., description="Trust type")
    purpose: Optional[str] = Field(None, description="Trust purpose")
    executionDate: Optional[date] = Field(None, description="Execution date")
    amendmentDate: Optional[date] = Field(None, description="Amendment date")
    location: Optional[str] = Field(None, description="Storage location")
    grantor: Optional[Dict[str, Any]] = Field(None, description="Grantor information")
    coGrantor: Optional[Dict[str, Any]] = Field(None, description="Co-grantor information")
    trustee: Optional[Dict[str, Any]] = Field(None, description="Trustee information")
    successorTrustee: Optional[Dict[str, Any]] = Field(None, description="Successor trustee information")
    isFunded: bool = Field(False, description="Whether trust is funded")
    trustValue: Optional[float] = Field(None, description="Trust value")
    fundingSource: Optional[Dict[str, Any]] = Field(None, description="Funding source")
    distributionProvisions: Optional[Dict[str, Any]] = Field(None, description="Distribution provisions")
    spendthriftProvision: bool = Field(False, description="Whether trust includes spendthrift provision")
    generationSkipping: bool = Field(False, description="Whether trust includes generation skipping")
    taxId: Optional[str] = Field(None, description="Tax ID")
    taxFilingRequirements: Optional[Dict[str, Any]] = Field(None, description="Tax filing requirements")
    attorney: Optional[Dict[str, Any]] = Field(None, description="Attorney information")
    documentId: Optional[str] = Field(None, description="Document ID")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the trust")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the trust")
    createdAt: datetime = Field(..., description="Timestamp when trust was created")
    updatedAt: datetime = Field(..., description="Timestamp when trust was last updated")
    
    model_config = {
        "from_attributes": True
    }


class BeneficiaryResponse(BaseModel):
    id: str = Field(..., description="Beneficiary ID")
    estateId: str = Field(..., description="ID of estate beneficiary belongs to")
    clientId: str = Field(..., description="ID of client beneficiary belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    willId: Optional[str] = Field(None, description="ID of will beneficiary belongs to")
    trustId: Optional[str] = Field(None, description="ID of trust beneficiary belongs to")
    name: str = Field(..., description="Beneficiary name")
    type: str = Field(..., description="Beneficiary type")
    relationship: str = Field(..., description="Relationship to client")
    status: str = Field(..., description="Beneficiary status")
    primary: bool = Field(True, description="Whether beneficiary is primary")
    contingent: bool = Field(False, description="Whether beneficiary is contingent")
    percentage: float = Field(..., description="Percentage of assets")
    priority: int = Field(..., description="Priority order")
    assetTypes: Optional[Dict[str, Any]] = Field(None, description="Asset types")
    specificAssets: Optional[Dict[str, Any]] = Field(None, description="Specific assets")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the beneficiary")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the beneficiary")
    createdAt: datetime = Field(..., description="Timestamp when beneficiary was created")
    updatedAt: datetime = Field(..., description="Timestamp when beneficiary was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class EstateListResponse(BaseModel):
    estates: List[EstateResponse] = Field(..., description="List of estates")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class WillListResponse(BaseModel):
    wills: List[WillResponse] = Field(..., description="List of wills")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class TrustListResponse(BaseModel):
    trusts: List[TrustResponse] = Field(..., description="List of trusts")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class BeneficiaryListResponse(BaseModel):
    beneficiaries: List[BeneficiaryResponse] = Field(..., description="List of beneficiaries")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class EstateFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    status: Optional[str] = Field(None, description="Filter by estate status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class WillFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    estate_id: Optional[str] = Field(None, description="Filter by estate ID")
    status: Optional[str] = Field(None, description="Filter by will status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class TrustFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    estate_id: Optional[str] = Field(None, description="Filter by estate ID")
    status: Optional[str] = Field(None, description="Filter by trust status")
    trust_type: Optional[str] = Field(None, description="Filter by trust type")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class BeneficiaryFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    estate_id: Optional[str] = Field(None, description="Filter by estate ID")
    will_id: Optional[str] = Field(None, description="Filter by will ID")
    trust_id: Optional[str] = Field(None, description="Filter by trust ID")
    type: Optional[str] = Field(None, description="Filter by beneficiary type")
    primary: Optional[bool] = Field(None, description="Filter by primary status")
    contingent: Optional[bool] = Field(None, description="Filter by contingent status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("priority", description="Sort field")
    count: bool = Field(False, description="Return count only")