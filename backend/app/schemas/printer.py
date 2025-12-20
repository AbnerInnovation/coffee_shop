"""
Pydantic schemas for Printer model
"""
from pydantic import BaseModel, Field, validator, computed_field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PrinterType(str, Enum):
    """Printer types enum"""
    KITCHEN = "kitchen"
    BAR = "bar"
    CASHIER = "cashier"


class ConnectionType(str, Enum):
    """Connection types enum"""
    NETWORK = "network"
    USB = "usb"
    BLUETOOTH = "bluetooth"


class PrinterBase(BaseModel):
    """Base printer schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Printer name")
    printer_type: PrinterType = Field(..., description="Type of printer (kitchen, bar, cashier)")
    connection_type: ConnectionType = Field(default=ConnectionType.NETWORK, description="Connection type")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address for network printers")
    port: Optional[int] = Field(9100, ge=1, le=65535, description="Port for network printers")
    device_path: Optional[str] = Field(None, max_length=255, description="Device path for USB/Bluetooth")
    paper_width: int = Field(80, ge=58, le=80, description="Paper width in mm (58 or 80)")
    is_active: bool = Field(True, description="Whether printer is active")
    is_default: bool = Field(False, description="Default printer for its type")
    auto_print: bool = Field(True, description="Auto-print on new orders")
    print_copies: int = Field(1, ge=1, le=5, description="Number of copies to print")
    category_ids: List[int] = Field(default_factory=list, description="Categories assigned to this printer")


class PrinterCreate(PrinterBase):
    """Schema for creating a new printer"""
    
    @validator('ip_address')
    def validate_ip_for_network(cls, v, values):
        """Validate IP address is provided for network printers"""
        if values.get('connection_type') == ConnectionType.NETWORK and not v:
            raise ValueError('IP address is required for network printers')
        return v

    @validator('device_path')
    def validate_device_for_usb_bluetooth(cls, v, values):
        """Validate device path format for USB/Bluetooth printers"""
        # Device path is optional - can be configured later
        # Just validate format if provided
        return v

    @validator('paper_width')
    def validate_paper_width(cls, v):
        """Validate paper width is either 58mm or 80mm"""
        if v not in [58, 80]:
            raise ValueError('Paper width must be either 58mm or 80mm')
        return v


class PrinterUpdate(BaseModel):
    """Schema for updating a printer"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    printer_type: Optional[PrinterType] = None
    connection_type: Optional[ConnectionType] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    port: Optional[int] = Field(None, ge=1, le=65535)
    device_path: Optional[str] = Field(None, max_length=255)
    paper_width: Optional[int] = Field(None, ge=58, le=80)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    auto_print: Optional[bool] = None
    print_copies: Optional[int] = Field(None, ge=1, le=5)
    category_ids: Optional[List[int]] = None


class PrinterResponse(BaseModel):
    """Schema for printer response"""
    id: int
    restaurant_id: int
    name: str
    printer_type: PrinterType
    connection_type: ConnectionType
    ip_address: Optional[str]
    port: Optional[int]
    device_path: Optional[str]
    paper_width: int
    is_active: bool
    is_default: bool
    auto_print: bool
    print_copies: int
    category_ids: List[int] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @staticmethod
    def from_printer(printer) -> 'PrinterResponse':
        """Create PrinterResponse from Printer model with category_ids extracted"""
        return PrinterResponse(
            id=printer.id,
            restaurant_id=printer.restaurant_id,
            name=printer.name,
            printer_type=printer.printer_type,
            connection_type=printer.connection_type,
            ip_address=printer.ip_address,
            port=printer.port,
            device_path=printer.device_path,
            paper_width=printer.paper_width,
            is_active=printer.is_active,
            is_default=printer.is_default,
            auto_print=printer.auto_print,
            print_copies=printer.print_copies,
            category_ids=[cat.id for cat in printer.categories] if printer.categories else [],
            created_at=printer.created_at,
            updated_at=printer.updated_at
        )


class PrinterListResponse(BaseModel):
    """Schema for list of printers"""
    printers: List[PrinterResponse]
    total: int


class PrinterCategoryAssignment(BaseModel):
    """Schema for assigning categories to a printer"""
    category_ids: List[int] = Field(..., description="List of category IDs to assign")


class PrinterTestPrint(BaseModel):
    """Schema for test print request"""
    test_text: Optional[str] = Field("Test Print", description="Text to print for testing")
