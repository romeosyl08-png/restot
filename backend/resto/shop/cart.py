from decimal import Decimal

from django.conf import settings
from .models import Meal


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = {}
            self.session[settings.CART_SESSION_ID] = cart
        self.cart = cart

    def add(self, meal, quantity=1, override_quantity=False):
        meal_id = str(meal.id)
        if meal_id not in self.cart:
            self.cart[meal_id] = {
                "quantity": 0,
                "price": str(meal.price),
            }

        if override_quantity:
            self.cart[meal_id]["quantity"] = quantity
        else:
            self.cart[meal_id]["quantity"] += quantity

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, meal):
        meal_id = str(meal.id)
        if meal_id in self.cart:
            del self.cart[meal_id]
            self.save()

    def __iter__(self):
        meal_ids = self.cart.keys()
        meals = Meal.objects.filter(id__in=meal_ids)
        cart = self.cart.copy()

        for meal in meals:
            item = cart[str(meal.id)]
            item["meal"] = meal
            item["quantity"] = int(item["quantity"])
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(int(item["quantity"]) for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item["price"]) * int(item["quantity"])
            for item in self.cart.values()
        )

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.session.modified = True
