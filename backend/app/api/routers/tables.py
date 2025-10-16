from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from ...db.base import get_db
from ...models.table import Table as TableModel
from ...schemas.table import Table, TableCreate, TableUpdate
from ...services import table as table_service
from ...models.user import User
from ...models.restaurant import Restaurant
from ...core.dependencies import get_current_restaurant
from ...services.user import get_current_active_user, UserRole
from ...core.exceptions import ResourceNotFoundError, ConflictError, ValidationError

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
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> List[Table]:
    """
    Retrieve tables with optional filtering.
    """
    return table_service.get_tables(
        db,
        restaurant_id=restaurant.id,
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
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> Table:
    """
    Create a new table.
    Requires admin privileges.
    """
    db_table = table_service.get_table_by_number(db, number=table.number, restaurant_id=restaurant.id)
    if db_table:
        raise ConflictError(
            f"Table number {table.number} already exists in this restaurant",
            resource="Table"
        )
    return table_service.create_table(db=db, table=table, restaurant_id=restaurant.id)

@router.get("/{table_id}", response_model=Table)
async def read_table(
    table_id: int, 
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> Table:
    """
    Get a specific table by ID.
    """
    db_table = table_service.get_table(db, table_id=table_id, restaurant_id=restaurant.id)
    if db_table is None:
        raise ResourceNotFoundError("Table", table_id)
    return db_table

class TableOccupancyUpdate(BaseModel):
    is_occupied: bool

@router.patch("/{table_id}/occupancy", response_model=Table)
async def update_table_occupancy(
    table_id: int,
    occupancy_data: TableOccupancyUpdate,
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> Table:
    """
    Update a table's occupancy status.
    """
    is_occupied = occupancy_data.is_occupied
    db_table = table_service.get_table(db, table_id=table_id, restaurant_id=restaurant.id)
    if db_table is None:
        raise ResourceNotFoundError("Table", table_id)
    
    # Update only the is_occupied field
    db_table.is_occupied = is_occupied
    db.commit()
    db.refresh(db_table)
    return db_table

@router.put("/{table_id}", response_model=Table)
async def update_table(
    table_id: int, 
    table: TableUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> Table:
    """
    Update a table.
    Requires admin privileges.
    """
    db_table = table_service.get_table(db, table_id=table_id, restaurant_id=restaurant.id)
    if db_table is None:
        raise ResourceNotFoundError("Table", table_id)
    
    if table.number and table.number != db_table.number:
        existing_table = table_service.get_table_by_number(db, number=table.number, restaurant_id=restaurant.id)
        if existing_table and existing_table.id != table_id:
            raise ConflictError(
                f"Table number {table.number} already exists in this restaurant",
                resource="Table"
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
    db: Session = Depends(get_db),
    restaurant: Restaurant = Depends(get_current_restaurant)
) -> None:
    """
    Delete a table.
    Requires admin privileges.
    """
    db_table = table_service.get_table(db, table_id=table_id)
    if db_table is None:
        raise ResourceNotFoundError("Table", table_id)
    
    # Check if table has active orders
    if db_table.orders:
        raise ConflictError(
            "Cannot delete a table with active orders. Please complete or cancel orders first.",
            resource="Table"
        )
    
    table_service.delete_table(db=db, db_table=db_table)
