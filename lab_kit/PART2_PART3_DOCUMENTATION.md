# SE 3141: Software Architecture — Activity 4
## Integration Arena: Deliverables for Part 2 & Part 3

---

### PART 2 — BUSINESS CAPABILITY MAP & TRACEABILITY

#### 1. Business Capability Map (Grid grouped by domain)

```
+----------------------------------------------------------------------------------------------------+
|                                    ENTERPRISE CAPABILITY MAP                                       |
+------------------------------------+------------------------------------+--------------------------+
| 1. SALES & ORDERING DOMAIN         | 2. FINANCIAL & PAYMENT DOMAIN      | 3. ENGAGEMENT & COMMS    |
+------------------------------------+------------------------------------+--------------------------+
| - Product Catalog & Pricing        | - Payment Authorization & Capture  | - Order Confirmations    |
| - Shopping Cart Management         | - Idempotency & Duplicate Check    | - Delivery Notifications |
| - Order Placement & Checkout       | - Settlement & Invoicing           | - Customer Support Comms |
| - Order Status Tracking            | - Refunds & Dispute Handling       | - Promotions & Loyalty   |
+------------------------------------+------------------------------------+--------------------------+
| 4. FULFILLMENT & INVENTORY DOMAIN  | 5. RISK, RELIABILITY & GOVERNANCE  | 6. INTEGRATION GATEWAY   |
+------------------------------------+------------------------------------+--------------------------+
| - Real-time Stock Reservation      | - Circuit Breaking & Fail-Fast     | - External Gateway Proxy |
| - Warehouse Dispatching            | - Retry & Transient Fault Handling | - Protocol Translation   |
| - Carrier & Shipment Tracking      | - Audit Logging & Accounting       | - Rate Limiting & Auth   |
+------------------------------------+------------------------------------+--------------------------+
```

#### 2. Goal-to-Service Traceability Paragraph (128 words)

> **Business Goal**: Maximize revenue and customer retention through fast, zero-duplicate, high-availability digital checkout.
>
> **Traceability Chain**: This overarching enterprise goal is realized by the **Order Placement & Payment Processing** business capability. That capability is operationalized through the **Digital Checkout Process** (Capture Order $\rightarrow$ Authorize Payment $\rightarrow$ Dispatch Notification). In Part 1, we implemented the **Order Service (`POST /orders`)** to execute this process.
>
> **Why does this service exist?** The Order Service exists to orchestrate customer purchases against unreliable third-party providers. By combining synchronous payment verification with idempotency keys, it prevents costly double-billing. By isolating slow notifications asynchronously and applying circuit breakers to fail fast during payment outages, it protects system responsiveness and prevents cascading failures across the enterprise architecture.

---

### PART 3 — LAB DEFENSE PREPARATION GUIDE

Use these key points during the 5–7 minute defense slot:

#### 1. Why is the payment call synchronous but the confirmation asynchronous?
* **Payment is on the Critical Path:** An order cannot be confirmed or fulfilled unless payment authorization succeeds. The caller (and merchant) requires an immediate, deterministic answer before finalizing the transaction.
* **Confirmation is an Event-Driven Side Effect:** Sending an SMS or email via `NotificationProvider` is slow (0.6s latency) and non-blocking for checkout completion. Running it asynchronously in a background thread decouples the user-facing response time from external network latency, ensuring the customer receives an immediate response while the confirmation is delivered with eventual consistency.

#### 2. What would break if you removed the idempotency key check?
* **Risk of Double-Charging:** External networks are inherently unreliable. If a payment succeeds at the gateway but the network times out before the client receives the response, the client or retry logic will re-send the charge request.
* **Financial Inconsistency:** Without the `Idempotency-Key`, the Payment Gateway would treat the retry as a brand-new transaction, charging the customer's account multiple times for a single order. Idempotency guarantees that executing the identical request multiple times produces the exact same outcome without duplicate side effects.

#### 3. How does your circuit breaker relate to the availability tactics?
* **Fault Detection & Prevention:** The circuit breaker monitors consecutive failures (threshold = 3). Once reached, it trips to the **Open** state.
* **Preventing Cascading Failures & Resource Exhaustion:** Rather than having threads hang and wait on a failing downstream service (wasting socket pools and worker threads), the circuit breaker **fails fast** by immediately returning an HTTP 503 fallback response in under 0.05 seconds.
* **Self-Healing (Half-Open Recovery):** After a reset timeout, the circuit allows trial traffic to determine whether the remote gateway has recovered, restoring normal operation automatically without manual intervention.

#### 4. How does your Part 1 service trace back to the business capability in Part 2?
* The `POST /orders` endpoint directly implements the **Order Placement & Payment Processing** capability within the Sales and Financial domains.
* Tracing upward: The service executes the automated checkout workflow, which fulfills the payment settlement capability, which ultimately drives the core business goal of reliable, high-volume e-commerce revenue capture while maintaining customer trust through zero double-charges.
