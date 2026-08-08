# services/pizza_service.py
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.pizza_repository import PizzaRepository
from models.pizza import Pizza
from dtos.pizza import PizzaIngredientCreate, PizzaUpdate


class PizzaNotFoundError(Exception):
    pass


class PizzaNameAlreadyExistsError(Exception):
    pass


class PizzaService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pizza_repo = PizzaRepository(session)

    async def create_pizza(
        self,
        name: str,
        price: Decimal,
        ingredients: list[PizzaIngredientCreate] | None = None,
    ) -> Pizza:
        existing = await self.pizza_repo.get_by_name(name)
        if existing is not None:
            raise PizzaNameAlreadyExistsError(f"A pizza named '{name}' already exists")

        pizza = await self.pizza_repo.create(name=name, price=price)

        if ingredients:
            for ingredient in ingredients:
                await self.pizza_repo.add_ingredient(
                    pizza_id=pizza.pizza_id,
                    inventory_item_id=ingredient.inventory_item_id,
                    quantity_required=ingredient.quantity_required,
                )

        return pizza

    async def get_pizza(self, pizza_id: int) -> Pizza:
        pizza = await self.pizza_repo.get_by_id(pizza_id)
        if pizza is None:
            raise PizzaNotFoundError(f"No pizza with id {pizza_id}")
        return pizza

    async def get_pizza_by_name(self, name: str) -> Pizza | None:
        return await self.pizza_repo.get_by_name(name)

    async def list_pizzas(self) -> list[Pizza]:
        return await self.pizza_repo.list_all()

    async def update_pizza(self, pizza_id: int, payload: PizzaUpdate) -> Pizza:
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data:
            existing = await self.pizza_repo.get_by_name(update_data["name"])
            if existing is not None and existing.pizza_id != pizza_id:
                raise PizzaNameAlreadyExistsError(f"A pizza named '{update_data['name']}' already exists")

        pizza = await self.pizza_repo.update(pizza_id, **update_data)
        if pizza is None:
            raise PizzaNotFoundError(f"No pizza with id {pizza_id}")
        return pizza

    async def delete_pizza(self, pizza_id: int) -> None:
        deleted = await self.pizza_repo.delete(pizza_id)
        if not deleted:
            raise PizzaNotFoundError(f"No pizza with id {pizza_id}")