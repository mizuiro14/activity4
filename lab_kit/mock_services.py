"""
mock_services.py
-----------------
Simulated EXTERNAL systems for the Integration Arena lab.

You do NOT need to modify this file. Treat these classes the way you would
treat a real third-party Payment Gateway and Notification Provider: you only
know their public methods (their "API"), not how they work inside.
"""

import time
import random


class PaymentGatewayError(Exception):
    """Raised when the external Payment Gateway fails or times out."""
    pass


class PaymentGateway:
    """
    Simulates an external, unreliable Payment Gateway (e.g., Stripe, PayMongo).

    - Every call takes `latency` seconds (simulates network delay).
    - Every call has a `failure_rate` chance of raising PaymentGatewayError
      (simulates a flaky/overloaded provider).
    - Supports idempotency: calling charge() twice with the SAME
      idempotency_key must return the SAME charge, not create a new one.
    """

    def __init__(self, failure_rate: float = 0.3, latency: float = 0.3):
        self.failure_rate = failure_rate
        self.latency = latency
        self._charged_keys = {}  # idempotency_key -> charge result

    def charge(self, order_id: str, amount: float, idempotency_key: str = None):
        time.sleep(self.latency)

        if idempotency_key and idempotency_key in self._charged_keys:
            return self._charged_keys[idempotency_key]

        if random.random() < self.failure_rate:
            raise PaymentGatewayError(f"Payment Gateway timed out for order {order_id}")

        result = {
            "status": "success",
            "order_id": order_id,
            "amount": amount,
            "charge_id": f"chg_{order_id}_{random.randint(1000, 9999)}",
        }

        if idempotency_key:
            self._charged_keys[idempotency_key] = result

        return result


class NotificationProvider:
    """
    Simulates an external SMS/Email provider that confirms an order.

    `send_delay` models a provider that is noticeably slow — slow enough
    that a caller waiting on it synchronously would feel it. A correct
    integration design does NOT block the customer's checkout response
    on this call (see Module 4, Lesson 1: Synchronous vs. Asynchronous
    Communication).
    """

    def __init__(self, send_delay: float = 0.6):
        self.send_delay = send_delay
        self.sent_log = []

    def send_confirmation(self, order_id: str, message: str):
        time.sleep(self.send_delay)
        self.sent_log.append({"order_id": order_id, "message": message})
        return True
