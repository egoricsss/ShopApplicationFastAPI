from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ProductCreate, Product as ProductSchema
from app.models import Product as ProductModel, Category as CategoryModel
from app.db_depends import get_db

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/")
async def get_all_products():
    """
    Возвращает список всех товаров.
    """
    return {"message": "Список всех товаров (заглушка)"}


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_payload: ProductCreate, session: AsyncSession = Depends(get_db)
):
    """
    Создаёт новый товар.
    """
    # check category id
    stmt = select(CategoryModel).where(CategoryModel.id == product_payload.id).limit(1)
    category = await session.scalar(stmt)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    db_product = ProductModel(**product_payload.model_dump())
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema])
async def get_products_by_category(
    category_id: int, session: AsyncSession = Depends(get_db)
):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt = (
        select(ProductModel)
        .where(ProductModel.category_id == category_id)
        .order_by(ProductModel.id)
    )
    result = await session.scalars(stmt)
    return result.all()


@router.get("/{product_id}", response_model=ProductModel)
async def get_product(product_id: int, session: AsyncSession = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt = select(ProductModel).where(ProductModel.id == product_id)
    db_product = await session.scalar(stmt)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with suc ID: {db_product.id} is not found",
        )
    return db_product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_payload: ProductCreate,
    session: AsyncSession = Depends(get_db),
):
    """
    Обновляет товар по его ID.
    """
    # check category existing
    stmt = (
        select(CategoryModel)
        .where(CategoryModel.id == product_payload.category_id)
        .limit(1)
    )
    db_category = await session.scalar(stmt)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with suc ID: {product_payload.id} not found",
        )
    stmt = (
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product_payload.model_dump())
        .returning(ProductModel)
    )
    db_product = await session.scalar(stmt)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with such ID: {product_payload.id} not found",
        )
    return db_product


@router.delete("/{product_id}", response_model=list[ProductModel])
async def delete_product(product_id: int, session: AsyncSession = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    stmt = (
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(is_active=False)
        .returning(ProductModel)
    )
    product_db = await session.scalar(stmt)
    if product_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product_db
