"""
Printer model for managing multiple printers in restaurants
"""
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.db.base import Base
import enum


class PrinterType(str, enum.Enum):
    """Printer types for different stations"""
    KITCHEN = "kitchen"
    BAR = "bar"
    CASHIER = "cashier"


# Association table for many-to-many relationship between categories and printers
category_printer = Table(
    'category_printer',
    Base.metadata,
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
    Column('printer_id', Integer, ForeignKey('printers.id', ondelete='CASCADE'), primary_key=True)
)


class Printer(BaseModel):
    """
    Printer model for managing restaurant printers
    Each printer can be assigned to specific categories
    """
    __tablename__ = 'printers'

    restaurant_id = Column(Integer, ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Printer identification
    name = Column(String(100), nullable=False)  # e.g., "Cocina Principal", "Barra 1"
    printer_type = Column(SQLEnum(PrinterType, values_callable=lambda x: [e.value for e in x]), nullable=False, index=True)
    
    # Printer connection details
    connection_type = Column(String(20), nullable=False, default='network')  # network, usb, bluetooth
    ip_address = Column(String(45), nullable=True)  # For network printers
    port = Column(Integer, nullable=True, default=9100)  # For network printers
    device_path = Column(String(255), nullable=True)  # For USB/Bluetooth printers
    
    # Printer settings
    paper_width = Column(Integer, nullable=False, default=80)  # 58mm or 80mm
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Default printer for its type
    
    # Print settings
    auto_print = Column(Boolean, default=True, nullable=False)  # Auto-print on new orders
    print_copies = Column(Integer, default=1, nullable=False)  # Number of copies to print
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="printers")
    categories = relationship(
        "Category",
        secondary=category_printer,
        back_populates="printers"
    )

    def __repr__(self):
        return f"<Printer(id={self.id}, name='{self.name}', type='{self.printer_type}', restaurant_id={self.restaurant_id})>"

    def to_dict(self):
        """Convert printer to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'printer_type': self.printer_type.value if self.printer_type else None,
            'connection_type': self.connection_type,
            'ip_address': self.ip_address,
            'port': self.port,
            'device_path': self.device_path,
            'paper_width': self.paper_width,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'auto_print': self.auto_print,
            'print_copies': self.print_copies,
            'category_ids': [cat.id for cat in self.categories] if self.categories else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
