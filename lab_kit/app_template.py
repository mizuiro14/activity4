"""
app_template.py
----------------
INTEGRATION ARENA — rename this file to app.py before you start.

You are the architect of an Order Service. It must integrate with two
external systems it does NOT control:

    1. PaymentGateway        (mock_services.py) — synchronous, unreliable
    2. NotificationProvider  (mock_services.py) — synchronous, slow

Your job is to build POST /orders so that it applies the integration
patterns from Module 4, Lesson 1. Work through the levels IN ORDER —
each one builds on the last. Do not edit mock_services.py.
"""

import time
import threading
from flask import Flask, request, jsonify

from mock_services import PaymentGateway, PaymentGatewayError, NotificationProvider

app = Flask(__name__)

payment_gateway = PaymentGateway(failure_rate=0.3, latency=0.3)
notifications = NotificationProvider(send_delay=0.6)

# Circuit breaker state for LEVEL 4 — feel free to change this structure.
circuit = {
    "open": False,
    "consecutive_failures": 0,
    "failure_threshold": 3,
}


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True)
    order_id = data.get("order_id")
    amount = data.get("amount")
    idempotency_key = request.headers.get("Idempotency-Key")

    # ------------------------------------------------------------------
    # LEVEL 1 (30 pts) — Basic synchronous integration
    #   Call payment_gateway.charge(order_id, amount) and return its
    #   result as JSON with a 200 status code.
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # LEVEL 2 (30 pts) — Make it reliable
    #   a) Pass idempotency_key through to charge() so a retried request
    #      with the same key never double-charges the customer.
    #   b) If PaymentGatewayError is raised, retry up to 3 times total
    #      before giving up (add a short backoff between attempts).
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # LEVEL 3 (20 pts) — Go asynchronous
    #   After a successful charge, send a confirmation via
    #   notifications.send_confirmation(order_id, ...) WITHOUT making
    #   the customer wait for it. The /orders response must return
    #   quickly even though the notification provider is slow.
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # LEVEL 4 — BOSS LEVEL (20 pts) — Circuit breaker
    #   Track consecutive Payment Gateway failures in `circuit`. Once
    #   failures reach circuit["failure_threshold"], "open" the circuit:
    #   stop calling the gateway and immediately return a 503 with a
    #   fallback message ("payment temporarily unavailable, order
    #   queued for retry") until you implement a reset strategy.
    # ------------------------------------------------------------------

    return jsonify({"error": "not implemented yet"}), 501


if __name__ == "__main__":
    # Run with: python app.py
    # Try it with curl, e.g.:
    #   curl -X POST http://127.0.0.1:5000/orders \
    #        -H "Content-Type: application/json" \
    #        -H "Idempotency-Key: demo-1" \
    #        -d '{"order_id": "ORD1", "amount": 250}'
    app.run(port=5000, debug=True)
