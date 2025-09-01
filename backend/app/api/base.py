from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Optional
from sqlalchemy.orm import Session
from ..db.base import get_db

class BaseRouter:
    """
    Base router class with common dependencies and error handling.
    """
    def __init__(self, prefix: str = "", tags: Optional[list[str]] = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])
        self._add_common_dependencies()
        self._add_routes()
    
    def _add_common_dependencies(self) -> None:
        """Add common dependencies to the router."""
        self.router.dependencies = [Depends(self._get_current_user)]
    
    def _add_routes(self) -> None:
        """Add routes to the router. Override this in child classes."""
        pass
    
    async def _get_current_user(self, db: Session = Depends(get_db)) -> Any:
        """
        Get the current user from the database.
        For now, this is a placeholder that will be implemented with authentication.
        """
        # TODO: Implement actual user authentication
        return None

class CRUDRouter(BaseRouter):
    """
    CRUD router with common CRUD operations.
    """
    def __init__(
        self, 
        model: Any, 
        schema: Any, 
        create_schema: Any = None, 
        update_schema: Any = None,
        prefix: str = "", 
        tags: Optional[list[str]] = None
    ):
        self.model = model
        self.schema = schema
        self.create_schema = create_schema or schema
        self.update_schema = update_schema or schema
        
        super().__init__(prefix=prefix, tags=tags or [model.__name__])
    
    def _add_routes(self) -> None:
        @self.router.get("/", response_model=list[Any])
        async def read_items(
            skip: int = 0, 
            limit: int = 100, 
            db: Session = Depends(get_db)
        ) -> Any:
            """Read multiple items."""
            items = db.query(self.model).offset(skip).limit(limit).all()
            return items
        
        @self.router.post("/", response_model=self.schema, status_code=status.HTTP_201_CREATED)
        async def create_item(
            item: self.create_schema,  # type: ignore
            db: Session = Depends(get_db)
        ) -> Any:
            """Create a new item."""
            db_item = self.model(**item.dict())
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        
        @self.router.get("/{item_id}", response_model=self.schema)
        async def read_item(item_id: int, db: Session = Depends(get_db)) -> Any:
            """Read a single item by ID."""
            db_item = db.query(self.model).filter(self.model.id == item_id).first()
            if db_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return db_item
        
        @self.router.put("/{item_id}", response_model=self.schema)
        async def update_item(
            item_id: int, 
            item: self.update_schema,  # type: ignore
            db: Session = Depends(get_db)
        ) -> Any:
            """Update an item."""
            db_item = db.query(self.model).filter(self.model.id == item_id).first()
            if db_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            update_data = item.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_item, key, value)
            
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        
        @self.router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
            """Delete an item."""
            db_item = db.query(self.model).filter(self.model.id == item_id).first()
            if db_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            db.delete(db_item)
            db.commit()
