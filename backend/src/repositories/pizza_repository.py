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
        # ingredients=[] marks the collection as loaded so create_pizza can append to it
        # after this flush without triggering a lazy load (MissingGreenlet under asyncio)
        pizza = Pizza(name=name, price=price, ingredients=[])
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

    # takes the Pizza itself, not pizza_id — same reason as CartRepository.add_cart_item:
    # appending through the relationship keeps pizza.ingredients correct in memory
    async def add_ingredient(
        self, pizza: Pizza, inventory_item_id: int, quantity_required: int
    ) -> PizzaIngredient:
        ingredient = PizzaIngredient(
            inventory_item_id=inventory_item_id,
            quantity_required=quantity_required,
        )
        pizza.ingredients.append(ingredient)
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

    # Pizza.ingredients has no delete-orphan cascade, so removing from the collection
    # alone would try to NULL pizza_ingredients.pizza_id and fail its NOT NULL constraint.
    # The explicit session.delete is what actually removes the row; the collection remove
    # is what keeps pizza.ingredients correct for the caller.
    async def remove_ingredient(self, pizza: Pizza, pizza_ingredient_id: int) -> bool:
        ingredient = next(
            (i for i in pizza.ingredients if i.pizza_ingredient_id == pizza_ingredient_id),
            None,
        )
        if ingredient is None:
            return False
        pizza.ingredients.remove(ingredient)
        await self.session.delete(ingredient)
        await self.session.flush()
        return True