from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class TaxFilingStatus(str, Enum):
    SINGLE = "Single"
    MARRIED_JOINT = "Married Filing Jointly"
    MARRIED_SEPARATE = "Married Filing Separately"
    HEAD_HOUSEHOLD = "Head of Household"
    QUALIFYING_WIDOW = "Qualifying Widow(er)"


class TaxDocumentType(str, Enum):
    W2 = "W-2"
    TEN99 = "1099"
    TEN98 = "1098"
    FIVE_HUNDRED = "Schedule 500"
    TAX_RETURN = "Tax Return"
    EXTENSION = "Filing Extension"
    PROPERTY_TAX = "Property Tax"
    OTHER = "Other"


# Base schemas
class TaxBase(BaseModel):
    client_id: str = Field(..., description="ID of client tax record belongs to")
    tax_year: int = Field(..., description="Tax year")
    filing_status: str = Field(..., description="Filing status")
    adjusted_gross_income: float = Field(..., description="Adjusted gross income")
    taxable_income: float = Field(..., description="Taxable income")
    federal_tax: float = Field(..., description="Federal tax")
    state_tax: Optional[float] = Field(None, description="State tax")
    state: Optional[str] = Field(None, description="State")
    deductions: Dict[str, Any] = Field(..., description="Deductions")
    credits: Optional[Dict[str, Any]] = Field(None, description="Credits")
    payments: Dict[str, Any] = Field(..., description="Payments")
    refund_amount: Optional[float] = Field(None, description="Refund amount")
    amount_owed: Optional[float] = Field(None, description="Amount owed")
    filing_date: date = Field(..., description="Filing date")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the tax record")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the tax record")


class TaxDocumentBase(BaseModel):
    tax_id: str = Field(..., description="ID of tax record document belongs to")
    document_id: str = Field(..., description="ID of document")
    type: str = Field(..., description="Document type")
    name: str = Field(..., description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    tax_year: int = Field(..., description="Tax year")
    form_number: Optional[str] = Field(None, description="Form number")
    issuer: Optional[str] = Field(None, description="Issuer")
    recipient: Optional[str] = Field(None, description="Recipient")
    issue_date: Optional[date] = Field(None, description="Issue date")
    created_by: str = Field(..., description="ID of user who created the tax document")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the tax document")


class TaxPaymentBase(BaseModel):
    tax_id: str = Field(..., description="ID of tax record payment belongs to")
    payment_type: str = Field(..., description="Payment type")
    payment_date: date = Field(..., description="Payment date")
    amount: float = Field(..., description="Payment amount")
    reference_number: Optional[str] = Field(None, description="Reference number")
    description: Optional[str] = Field(None, description="Description")
    created_by: str = Field(..., description="ID of user who created the tax payment")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the tax payment")


class TaxDeductionBase(BaseModel):
    tax_id: str = Field(..., description="ID of tax record deduction belongs to")
    deduction_type: str = Field(..., description="Deduction type")
    category: str = Field(..., description="Deduction category")
    description: str = Field(..., description="Description")
    amount: float = Field(..., description="Deduction amount")
    created_by: str = Field(..., description="ID of user who created the tax deduction")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the tax deduction")


# Response models with ID and timestamps
class TaxResponse(BaseModel):
    id: str = Field(..., description="Tax ID")
    clientId: str = Field(..., description="ID of client tax record belongs to")
    taxYear: int = Field(..., description="Tax year")
    filingStatus: str = Field(..., description="Filing status")
    adjustedGrossIncome: float = Field(..., description="Adjusted gross income")
    taxableIncome: float = Field(..., description="Taxable income")
    federalTax: float = Field(..., description="Federal tax")
    stateTax: Optional[float] = Field(None, description="State tax")
    state: Optional[str] = Field(None, description="State")
    deductions: Dict[str, Any] = Field(..., description="Deductions")
    credits: Optional[Dict[str, Any]] = Field(None, description="Credits")
    payments: Dict[str, Any] = Field(..., description="Payments")
    refundAmount: Optional[float] = Field(None, description="Refund amount")
    amountOwed: Optional[float] = Field(None, description="Amount owed")
    filingDate: date = Field(..., description="Filing date")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the tax record")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the tax record")
    createdAt: datetime = Field(..., description="Timestamp when tax record was created")
    updatedAt: datetime = Field(..., description="Timestamp when tax record was last updated")
    
    model_config = {
        "from_attributes": True
    }


class TaxDocumentResponse(BaseModel):
    id: str = Field(..., description="Tax document ID")
    taxId: str = Field(..., description="ID of tax record document belongs to")
    documentId: str = Field(..., description="ID of document")
    type: str = Field(..., description="Document type")
    name: str = Field(..., description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    taxYear: int = Field(..., description="Tax year")
    formNumber: Optional[str] = Field(None, description="Form number")
    issuer: Optional[str] = Field(None, description="Issuer")
    recipient: Optional[str] = Field(None, description="Recipient")
    issueDate: Optional[date] = Field(None, description="Issue date")
    createdBy: str = Field(..., description="ID of user who created the tax document")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the tax document")
    createdAt: datetime = Field(..., description="Timestamp when tax document was created")
    updatedAt: datetime = Field(..., description="Timestamp when tax document was last updated")
    
    model_config = {
        "from_attributes": True
    }


class TaxPaymentResponse(BaseModel):
    id: str = Field(..., description="Tax payment ID")
    taxId: str = Field(..., description="ID of tax record payment belongs to")
    paymentType: str = Field(..., description="Payment type")
    paymentDate: date = Field(..., description="Payment date")
    amount: float = Field(..., description="Payment amount")
    referenceNumber: Optional[str] = Field(None, description="Reference number")
    description: Optional[str] = Field(None, description="Description")
    createdBy: str = Field(..., description="ID of user who created the tax payment")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the tax payment")
    createdAt: datetime = Field(..., description="Timestamp when tax payment was created")
    updatedAt: datetime = Field(..., description="Timestamp when tax payment was last updated")
    
    model_config = {
        "from_attributes": True
    }


class TaxDeductionResponse(BaseModel):
    id: str = Field(..., description="Tax deduction ID")
    taxId: str = Field(..., description="ID of tax record deduction belongs to")
    deductionType: str = Field(..., description="Deduction type")
    category: str = Field(..., description="Deduction category")
    description: str = Field(..., description="Description")
    amount: float = Field(..., description="Deduction amount")
    createdBy: str = Field(..., description="ID of user who created the tax deduction")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the tax deduction")
    createdAt: datetime = Field(..., description="Timestamp when tax deduction was created")
    updatedAt: datetime = Field(..., description="Timestamp when tax deduction was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class TaxListResponse(BaseModel):
    taxes: List[TaxResponse] = Field(..., description="List of tax records")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class TaxDocumentListResponse(BaseModel):
    taxDocuments: List[TaxDocumentResponse] = Field(..., description="List of tax documents")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class TaxPaymentListResponse(BaseModel):
    taxPayments: List[TaxPaymentResponse] = Field(..., description="List of tax payments")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class TaxDeductionListResponse(BaseModel):
    taxDeductions: List[TaxDeductionResponse] = Field(..., description="List of tax deductions")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class TaxFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    tax_year: Optional[int] = Field(None, description="Filter by tax year")
    filing_status: Optional[str] = Field(None, description="Filter by filing status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("tax_year", description="Sort field")
    count: bool = Field(False, description="Return count only")


class TaxDocumentFilterParams(BaseModel):
    tax_id: Optional[str] = Field(None, description="Filter by tax ID")
    type: Optional[str] = Field(None, description="Filter by document type")
    tax_year: Optional[int] = Field(None, description="Filter by tax year")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class TaxPaymentFilterParams(BaseModel):
    tax_id: Optional[str] = Field(None, description="Filter by tax ID")
    payment_type: Optional[str] = Field(None, description="Filter by payment type")
    payment_date_after: Optional[date] = Field(None, description="Filter by payment date after")
    payment_date_before: Optional[date] = Field(None, description="Filter by payment date before")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("payment_date", description="Sort field")
    count: bool = Field(False, description="Return count only")


class TaxDeductionFilterParams(BaseModel):
    tax_id: Optional[str] = Field(None, description="Filter by tax ID")
    deduction_type: Optional[str] = Field(None, description="Filter by deduction type")
    category: Optional[str] = Field(None, description="Filter by category")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("amount", description="Sort field")
    count: bool = Field(False, description="Return count only")