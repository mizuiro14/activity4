"""
app.py
------
INTEGRATION ARENA — Order Service implementation.

External systems integrated:
    1. PaymentGateway        (mock_services.py) — synchronous, unreliable
    2. NotificationProvider  (mock_services.py) — synchronous, slow

Applies integration patterns:
    Level 1: Synchronous API call
    Level 2: Idempotency keys + Retry with exponential backoff
    Level 3: Asynchronous background dispatch for notifications
    Level 4: Circuit breaker pattern (fail-fast on consecutive failures)
"""

import time
import threading
from flask import Flask, request, jsonify

from mock_services import PaymentGateway, PaymentGatewayError, NotificationProvider

app = Flask(__name__)

payment_gateway = PaymentGateway(failure_rate=0.3, latency=0.3)
notifications = NotificationProvider(send_delay=0.6)

# Circuit breaker state for LEVEL 4
circuit = {
    "open": False,
    "consecutive_failures": 0,
    "failure_threshold": 3,
    "reset_timeout": 30.0,
    "last_failure_time": None,
}

circuit_lock = threading.Lock()


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True) or {}
    order_id = data.get("order_id")
    amount = data.get("amount")
    idempotency_key = request.headers.get("Idempotency-Key")

    # ------------------------------------------------------------------
    # LEVEL 4 (20 pts) — Circuit breaker (Fail-fast check)
    #   If the circuit is open, fail fast immediately without calling
    #   the external Payment Gateway.
    # ------------------------------------------------------------------
    with circuit_lock:
        if circuit["open"]:
            # Check for reset strategy (half-open trial after timeout)
            last_fail = circuit.get("last_failure_time")
            if last_fail and (time.time() - last_fail > circuit.get("reset_timeout", 30.0)):
                # Half-open: allow this trial request to attempt recovery
                pass
            else:
                return jsonify({
                    "error": "payment temporarily unavailable, order queued for retry"
                }), 503

    # ------------------------------------------------------------------
    # LEVEL 1 & 2 (30 + 30 pts) — Synchronous Payment with Idempotency & Retry
    #   - Call payment_gateway.charge(order_id, amount, idempotency_key=idempotency_key)
    #   - Retry up to 3 times total with backoff on PaymentGatewayError
    # ------------------------------------------------------------------
    max_attempts = 3
    backoff = 0.02
    charge_result = None
    last_error = None

    for attempt in range(max_attempts):
        try:
            charge_result = payment_gateway.charge(
                order_id=order_id,
                amount=amount,
                idempotency_key=idempotency_key,
            )
            break
        except PaymentGatewayError as err:
            last_error = err
            if attempt < max_attempts - 1:
                time.sleep(backoff * (2 ** attempt))

    # Handle payment failure across all retries
    if charge_result is None:
        with circuit_lock:
            circuit["consecutive_failures"] += 1
            circuit["last_failure_time"] = time.time()
            if circuit["consecutive_failures"] >= circuit["failure_threshold"]:
                circuit["open"] = True
                return jsonify({
                    "error": "payment temporarily unavailable, order queued for retry"
                }), 503

        return jsonify({
            "error": "payment failed after retries",
            "details": str(last_error),
        }), 502

    # ------------------------------------------------------------------
    # Successful Payment:
    #   - Reset circuit breaker failure count
    #   - LEVEL 3 (20 pts): Asynchronous Notification
    #     Dispatch confirmation in a background thread without blocking
    #     the checkout response.
    # ------------------------------------------------------------------
    with circuit_lock:
        circuit["consecutive_failures"] = 0
        circuit["open"] = False

    notification_thread = threading.Thread(
        target=notifications.send_confirmation,
        args=(order_id, f"Order {order_id} confirmed for amount {amount}"),
        daemon=True,
    )
    notification_thread.start()

    return jsonify(charge_result), 200


if __name__ == "__main__":
    # Run with: python app.py
    # Try it with curl, e.g.:
    #   curl -X POST http://127.0.0.1:5000/orders \
    #        -H "Content-Type: application/json" \
    #        -H "Idempotency-Key: demo-1" \
    #        -d '{"order_id": "ORD1", "amount": 250}'
    app.run(port=5000, debug=True)
