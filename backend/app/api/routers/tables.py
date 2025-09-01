from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.base import get_db
from ...models.table import Table as TableModel
from ...schemas.table import Table, TableCreate, TableUpdate
from ...services import table as table_service
from ...services.user import get_current_active_user, UserRole

router = APIRouter(
    prefix="/tables",
    tags=["tables"],
    dependencies=[Depends(get_current_active_user)],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Table])
async def read_tables(
    skip: int = 0, 
    limit: int = 100,
    occupied: bool = None,
    capacity: int = None,
    db: Session = Depends(get_db)
) -> List[Table]:
    """
    Retrieve tables with optional filtering.
    """
    return table_service.get_tables(
        db, 
        skip=skip, 
        limit=limit, 
        occupied=occupied,
        capacity=capacity
    )

@router.post(
    "/", 
    response_model=Table, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_user)]
)
async def create_table(
    table: TableCreate, 
    db: Session = Depends(get_db)
) -> Table:
    """
    Create a new table.
    Requires admin privileges.
    """
    db_table = table_service.get_table_by_number(db, number=table.number)
    if db_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Table with this number already exists"
        )
    return table_service.create_table(db=db, table=table)

@router.get("/{table_id}", response_model=Table)
async def read_table(
    table_id: int, 
    db: Session = Depends(get_db)
) -> Table:
    """
    Get a specific table by ID.
    """
    db_table = table_service.get_table(db, table_id=table_id)
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    return db_table

@router.put("/{table_id}", response_model=Table)
async def update_table(
    table_id: int, 
    table: TableUpdate, 
    db: Session = Depends(get_db)
) -> Table:
    """
    Update a table.
    Requires admin privileges.
    """
    db_table = table_service.get_table(db, table_id=table_id)
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    if table.number and table.number != db_table.number:
        existing_table = table_service.get_table_by_number(db, number=table.number)
        if existing_table and existing_table.id != table_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table with this number already exists"
            )
    
    return table_service.update_table(
        db=db, 
        db_table=db_table, 
        table=table
    )

@router.delete(
    "/{table_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_user)]
)
async def delete_table(
    table_id: int, 
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a table.
    Requires admin privileges.
    """
    db_table = table_service.get_table(db, table_id=table_id)
    if db_table is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )
    
    # Check if table has active orders
    if db_table.orders:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a table with active orders"
        )
    
    table_service.delete_table(db=db, db_table=db_table)
