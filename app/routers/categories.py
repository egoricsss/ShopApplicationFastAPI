from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category as CategoryModel, Product as ProductModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(session: AsyncSession = Depends(get_db)):
    stmt = select(CategoryModel).where(CategoryModel.is_active == True)
    results = await session.scalars(stmt)
    return results.all()


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_payload: CategoryCreate, db: AsyncSession = Depends(get_db)
):
    """
    Создаёт новую категорию.
    """
    if category_payload.parent_id is not None:
        stmt = select(CategoryModel).where(
            CategoryModel.id == category_payload.parent_id,
            CategoryModel.is_active == True,
        )
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found",
            )
    db_category = CategoryModel(**category_payload.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_payload: CategoryCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Обновляет категорию по её ID
    """
    # Check parent category
    if category_payload.parent_id is not None:
        stmt = (
            select(CategoryModel)
            .where(CategoryModel.id == category_payload.parent_id)
            .limit(1)
        )
        parent_category = await session.scalar(stmt)
        if parent_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent Category with ID: {category_payload.parent_id} not found",
            )
    stmt = (
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category_payload.model_dump())
        .returning(CategoryModel)
    )
    db_category = await session.scalar(stmt)
    return db_category


@router.delete("/{category_id}", response_model=CategorySchema)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_db)):
    """
    Удаляет категорию по её ID.
    """
    stmt = (
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
        .returning(CategoryModel)
    )
    db_category = await session.scalar(stmt)
    return db_category
