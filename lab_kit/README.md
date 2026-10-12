# Integration Arena — SE 3141 Activity 4 Starter Kit

This is the coding half of Activity 4 (Module 4: Integration & Business
Architectures). You are building the Order Service described in the
activity sheet, applying the integration patterns from Lesson 1.

## Setup

```bash
pip install -r requirements.txt
```

## Files

| File | What it is | Do you edit it? |
|---|---|---|
| `mock_services.py` | The simulated external Payment Gateway & Notification Provider | No |
| `app_template.py` | Your starting point | **Yes** — rename it to `app.py` and fill in the TODOs |
| `test_lab_autograder.py` | The autograder | No |
| `run_lab.py` | Runs the autograder and prints your scoreboard | No |

## Workflow

1. Rename `app_template.py` to `app.py`.
2. Implement Level 1, then run the scoreboard to check your progress:
   ```bash
   python run_lab.py
   ```
3. Keep going level by level — each one builds on the last. Don't skip ahead;
   Level 4 assumes Levels 1–3 already work.
4. Once you're passing everything (or as far as you get), try it live:
   ```bash
   python app.py
   ```
   then in another terminal:
   ```bash
   curl -X POST http://127.0.0.1:5000/orders \
        -H "Content-Type: application/json" \
        -H "Idempotency-Key: demo-1" \
        -d '{"order_id": "ORD1", "amount": 250}'
   ```
5. Bring your working `app.py` and your scoreboard output to your lab
   defense slot. See the activity sheet for the defense questions.

## Notes

- `mock_services.PaymentGateway` fails about 30% of the time and takes ~0.3s
  per call — that's intentional. It's standing in for a real unreliable
  external API.
- Do not modify `mock_services.py` or `test_lab_autograder.py`. Doing so
  invalidates your score during the lab defense — the instructor runs the
  autograder against the untouched files.
