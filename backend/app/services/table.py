from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from ..models.table import Table as TableModel
from ..schemas.table import TableCreate, TableUpdate

logger = logging.getLogger(__name__)

def get_tables(
    db: Session, 
    restaurant_id: int,
    skip: int = 0, 
    limit: int = 100,
    occupied: Optional[bool] = None,
    capacity: Optional[int] = None
) -> List[TableModel]:
    """
    Get a list of tables with optional filtering.
    """
    query = db.query(TableModel).filter(TableModel.restaurant_id == restaurant_id)
    
    if occupied is not None:
        query = query.filter(TableModel.is_occupied == occupied)
    
    if capacity is not None:
        query = query.filter(TableModel.capacity >= capacity)
    
    return query.offset(skip).limit(limit).all()

def get_table(db: Session, table_id: int, restaurant_id: Optional[int] = None) -> Optional[TableModel]:
    """
    Get a table by ID.
    """
    query = db.query(TableModel).filter(TableModel.id == table_id)
    if restaurant_id is not None:
        query = query.filter(TableModel.restaurant_id == restaurant_id)
    return query.first()

def get_table_by_number(db: Session, number: int, restaurant_id: int) -> Optional[TableModel]:
    """
    Get a table by its number.
    """
    return db.query(TableModel).filter(
        TableModel.number == number,
        TableModel.restaurant_id == restaurant_id
    ).first()

def create_table(
    db: Session, 
    table: TableCreate,
    restaurant_id: int
) -> TableModel:
    """
    Create a new table.
    """
    db_table = TableModel(**table.dict(), restaurant_id=restaurant_id)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def update_table(
    db: Session, 
    db_table: TableModel, 
    table: TableUpdate
) -> TableModel:
    """
    Update a table.
    """
    update_data = table.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_table, field, value)
    
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def delete_table(db: Session, db_table: TableModel) -> None:
    """
    Delete a table.
    """
    db.delete(db_table)
    db.commit()

def set_table_occupied(
    db: Session, 
    table_id: int, 
    occupied: bool = True
) -> Optional[TableModel]:
    """
    Set a table's occupied status.
    """
    db_table = get_table(db, table_id=table_id)
    if not db_table:
        return None
    
    db_table.is_occupied = occupied
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table
