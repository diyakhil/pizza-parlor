# db/seed.py
import asyncio
from decimal import Decimal

from db.session import AsyncSessionLocal
from models import User, Pizza, InventoryItem, PizzaIngredient


async def seed():
    async with AsyncSessionLocal() as session:
        # --- Inventory items ---
        inventory_data = {
            "dough": 50,
            "tomato_sauce": 50,
            "mozzarella": 60,
            "basil": 20,
            "ricotta": 20,
            "onion": 40,
            "sausage": 30,
            "pepperoni": 30,
            "peppers": 40,
            "mushroom": 30,
        }
        inventory_items = {
            name: InventoryItem(name=name, qty_available=qty)
            for name, qty in inventory_data.items()
        }
        session.add_all(inventory_items.values())
        await session.flush()

        # --- Admin user ---
        admin = User(
            email="admin@pizzaparlor.com",
            first_name="Admin",
            last_name="User",
        )
        session.add(admin)

        # --- Pizzas ---
        pizzas = {
            "margherita": Pizza(name="margherita", price=Decimal("12.99")),
            "white": Pizza(name="white", price=Decimal("13.99")),
            "pepperoni": Pizza(name="pepperoni", price=Decimal("13.99")),
            "supreme": Pizza(name="supreme", price=Decimal("16.99")),
            "veggie": Pizza(name="veggie", price=Decimal("14.99")),
        }
        session.add_all(pizzas.values())
        await session.flush()

        # --- Pizza ingredients (recipe) ---
        recipes = {
            "margherita": [
                ("dough", 1), ("tomato_sauce", 1), ("mozzarella", 1), ("basil", 1),
            ],
            "white": [
                ("dough", 1), ("mozzarella", 1), ("ricotta", 1), ("onion", 1), ("sausage", 1),
            ],
            "pepperoni": [
                ("dough", 1), ("mozzarella", 1), ("tomato_sauce", 1), ("pepperoni", 1),
            ],
            "supreme": [
                ("dough", 1), ("tomato_sauce", 1), ("mozzarella", 2), ("pepperoni", 1),
                ("sausage", 1), ("onion", 1), ("peppers", 1), ("mushroom", 1),
            ],
            "veggie": [
                ("dough", 1), ("tomato_sauce", 1), ("onion", 2), ("peppers", 2),
                ("mushroom", 1), ("mozzarella", 1),
            ],
        }

        pizza_ingredients = []
        for pizza_name, ingredients in recipes.items():
            for ingredient_name, qty in ingredients:
                pizza_ingredients.append(
                    PizzaIngredient(
                        pizza_id=pizzas[pizza_name].pizza_id,
                        inventory_item_id=inventory_items[ingredient_name].inventory_item_id,
                        quantity_required=qty,
                    )
                )
        session.add_all(pizza_ingredients)

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())