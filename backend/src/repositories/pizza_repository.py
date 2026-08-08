from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.pizza import Pizza
from models.pizza_ingredient import PizzaIngredient

class PizzaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- Pizza CRUD ---

    async def get_by_id(self, pizza_id: int) -> Pizza | None:
        result = await self.session.execute(
            select(Pizza)
            .where(Pizza.pizza_id == pizza_id)
            .options(selectinload(Pizza.ingredients))
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Pizza | None:
        result = await self.session.execute(
            select(Pizza).where(Pizza.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Pizza]:
        result = await self.session.execute(
            select(Pizza).options(selectinload(Pizza.ingredients))
        )
        return list(result.scalars().all())

    async def create(self, name: str, price: Decimal) -> Pizza:
        pizza = Pizza(name=name, price=price)
        self.session.add(pizza)
        await self.session.flush()
        return pizza

    async def update(self, pizza_id: int, **kwargs) -> Pizza | None:
        pizza = await self.session.get(Pizza, pizza_id)
        if pizza is None:
            return None
        for key, value in kwargs.items():
            setattr(pizza, key, value)
        await self.session.flush()
        return pizza

    async def delete(self, pizza_id: int) -> bool:
        pizza = await self.session.get(Pizza, pizza_id)
        if pizza is None:
            return False
        await self.session.delete(pizza)
        await self.session.flush()
        return True

    # --- PizzaIngredient CRUD ---

    async def get_ingredient_by_id(self, pizza_ingredient_id: int) -> PizzaIngredient | None:
        return await self.session.get(PizzaIngredient, pizza_ingredient_id)

    async def list_ingredients_for_pizza(self, pizza_id: int) -> list[PizzaIngredient]:
        result = await self.session.execute(
            select(PizzaIngredient).where(PizzaIngredient.pizza_id == pizza_id)
        )
        return list(result.scalars().all())

    async def add_ingredient(
        self, pizza_id: int, inventory_item_id: int, quantity_required: int
    ) -> PizzaIngredient:
        ingredient = PizzaIngredient(
            pizza_id=pizza_id,
            inventory_item_id=inventory_item_id,
            quantity_required=quantity_required,
        )
        self.session.add(ingredient)
        await self.session.flush()
        return ingredient

    async def update_ingredient(
        self, pizza_ingredient_id: int, **kwargs
    ) -> PizzaIngredient | None:
        ingredient = await self.session.get(PizzaIngredient, pizza_ingredient_id)
        if ingredient is None:
            return None
        for key, value in kwargs.items():
            setattr(ingredient, key, value)
        await self.session.flush()
        return ingredient

    async def remove_ingredient(self, pizza_ingredient_id: int) -> bool:
        ingredient = await self.session.get(PizzaIngredient, pizza_ingredient_id)
        if ingredient is None:
            return False
        await self.session.delete(ingredient)
        await self.session.flush()
        return True