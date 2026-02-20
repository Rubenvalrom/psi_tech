#!/usr/bin/env python3
"""
scaffold_module.py - Generate modular FastAPI module structure
"""

import os
import sys
from pathlib import Path
from typing import Optional

ROUTES_TEMPLATE = '''"""
{module_name} routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.security import get_current_user

from . import schemas, crud

router = APIRouter(
    prefix="/{module_name}",
    tags=["{module_name}"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[schemas.{ModelClass}])
async def list_{module_name}(
    skip: int = 0, 
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """List all {module_name} records"""
    return await crud.list_{module_name}(db, skip=skip, limit=limit)


@router.get("/{{id}}", response_model=schemas.{ModelClass})
async def get_{module_name}(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get {module_name} by ID"""
    record = await crud.get_{module_name}(db, id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{module_name} not found"
        )
    return record


@router.post("/", response_model=schemas.{ModelClass})
async def create_{module_name}(
    obj: schemas.{ModelClass}Create,
    db: AsyncSession = Depends(get_db)
):
    """Create {module_name}"""
    return await crud.create_{module_name}(db, obj)


@router.put("/{{id}}", response_model=schemas.{ModelClass})
async def update_{module_name}(
    id: int,
    obj: schemas.{ModelClass}Update,
    db: AsyncSession = Depends(get_db)
):
    """Update {module_name}"""
    record = await crud.update_{module_name}(db, id, obj)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{module_name} not found"
        )
    return record


@router.delete("/{{id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{module_name}(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete {module_name}"""
    success = await crud.delete_{module_name}(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{module_name} not found"
        )
'''

SCHEMAS_TEMPLATE = '''"""
{module_name} Pydantic schemas
"""

from datetime import datetime
from pydantic import BaseModel, Field


class {ModelClass}Base(BaseModel):
    """Base schema for {module_name}"""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class {ModelClass}Create({ModelClass}Base):
    """Schema for creating {module_name}"""
    pass


class {ModelClass}Update({ModelClass}Base):
    """Schema for updating {module_name}"""
    name: str | None = None


class {ModelClass}(BaseModel):
    """Schema for reading {module_name}"""
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
'''

CRUD_TEMPLATE = '''"""
{module_name} CRUD operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def list_{module_name}(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10
):
    """List {module_name} with pagination"""
    from app.models import {ModelClass}
    
    result = await db.execute(
        select({ModelClass})
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_{module_name}(db: AsyncSession, id: int):
    """Get {module_name} by ID"""
    from app.models import {ModelClass}
    
    result = await db.execute(
        select({ModelClass}).where({ModelClass}.id == id)
    )
    return result.scalar_one_or_none()


async def create_{module_name}(db: AsyncSession, obj):
    """Create {module_name}"""
    from app.models import {ModelClass}
    
    db_obj = {ModelClass}(**obj.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_{module_name}(db: AsyncSession, id: int, obj):
    """Update {module_name}"""
    db_obj = await get_{module_name}(db, id)
    if not db_obj:
        return None
    
    for key, value in obj.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_{module_name}(db: AsyncSession, id: int):
    """Delete {module_name}"""
    db_obj = await get_{module_name}(db, id)
    if not db_obj:
        return False
    
    await db.delete(db_obj)
    await db.commit()
    return True
'''

INIT_TEMPLATE = '''"""
{module_name} module
"""

from . import routes

__all__ = ["routes"]
'''


def scaff old_module(
    app_dir: str = "app",
    module_name: str = None,
    model_class: str = None
) -> int:
    """Generate module structure"""
    
    if not module_name:
        print("Error: --module name required")
        return 1
    
    if not model_class:
        model_class = "".join(word.capitalize() for word in module_name.split("_"))
    
    module_path = Path(app_dir) / module_name
    
    if module_path.exists():
        print(f"Error: Module '{module_name}' already exists")
        return 1
    
    try:
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        (module_path / "__init__.py").write_text(
            INIT_TEMPLATE.format(module_name=module_name)
        )
        
        # Create routes.py
        (module_path / "routes.py").write_text(
            ROUTES_TEMPLATE.format(
                module_name=module_name,
                ModelClass=model_class
            )
        )
        
        # Create schemas.py
        (module_path / "schemas.py").write_text(
            SCHEMAS_TEMPLATE.format(
                module_name=module_name,
                ModelClass=model_class
            )
        )
        
        # Create crud.py
        (module_path / "crud.py").write_text(
            CRUD_TEMPLATE.format(
                module_name=module_name,
                ModelClass=model_class
            )
        )
        
        print(f"✅ Module '{module_name}' scaffolded successfully")
        print(f"   Location: {module_path}")
        print(f"   Generated: __init__.py, routes.py, schemas.py, crud.py")
        print(f"\n📝 Next steps:")
        print(f"   1. Define {model_class} model in app/models.py")
        print(f"   2. Import routes: from app.{module_name} import routes")
        print(f"   3. Include router: app.include_router(routes.router)")
        
        return 0
    except Exception as e:
        print(f"Error scaffolding module: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate FastAPI module scaffold")
    parser.add_argument("--app-dir", default="app", help="App directory (default: app)")
    parser.add_argument("--module", required=True, help="Module name (snake_case)")
    parser.add_argument("--model", help="Model class name (default: CamelCase of module)")
    
    args = parser.parse_args()
    sys.exit(scaffold_module(args.app_dir, args.module, args.model))
