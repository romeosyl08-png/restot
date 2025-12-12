from decimal import Decimal
from .models import Meal

CART_SESSION_ID = 'cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, meal_id, quantity=1):
        meal_id = str(meal_id)
        if meal_id not in self.cart:
            self.cart[meal_id] = {'quantity': 0}

        self.cart[meal_id]['quantity'] = max(1, self.cart[meal_id]['quantity'] + int(quantity))
        self.save()


    def remove(self, meal_id):
        meal_id = str(meal_id)
        if meal_id in self.cart:
            del self.cart[meal_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        meal_ids = self.cart.keys()
        meals = Meal.objects.filter(id__in=meal_ids)
        meal_map = {str(m.id): m for m in meals}

        for meal_id, item in self.cart.items():
            meal = meal_map.get(meal_id)
            if meal:
                quantity = item['quantity']
                total_price = meal.price * quantity
                yield {
                    'meal': meal,
                    'quantity': quantity,
                    'price': meal.price,
                    'total_price': total_price
                }

    def get_total_price(self):
        total = Decimal('0')
        for item in self:
            total += item['total_price']
        return total
    
    def __len__(self):
        
        return sum(item['quantity'] for item in self.cart.values())

