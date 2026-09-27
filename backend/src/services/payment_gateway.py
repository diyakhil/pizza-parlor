import random

#this is to completely simulate a payment gateway - nothing is connected
class PaymentGateway:
    def charge(self, amount:float, idempotency_key:str) -> bool:
        if not idempotency_key or not amount or amount <= 0:
            return False

        random_number = random.randint(1, 10)
        return random_number != 1