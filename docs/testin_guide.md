# Unit Testing for APIs — Practical Guide

> Simple, professional, example-driven. No fluff.

---

## Part 1: Types of Testing

| Type | What it tests | Speed | Example |
|------|--------------|-------|---------|
| **Unit** | One function / one piece of logic | ⚡ Very fast | `calculate_tax(100)` returns `15` |
| **Integration** | Multiple parts working together | 🔄 Medium | API + Database query works correctly |
| **Functional** | Feature works from the user's perspective | 🐢 Slower | "User can log in with correct credentials" |
| **End-to-End (E2E)** | Entire flow, like a real user | 🐌 Slowest | Open browser → sign up → checkout → done |

### الفرق ببساطة

- **Unit** — أنت بتاختبر وظيفة واحدة بشكل معزول تماماً
- **Integration** — بتاختبر إن قطعتين اتنين بيشتغلوا صح مع بعض
- **Functional** — بتاختبر إن الـ feature بتعمل صح من ناحية الـ business logic
- **E2E** — بتاختبر كل حاجة من أول وجديد زي ما المستخدم بيعمل

---

## Part 2: Unit Testing — Deep Dive

### What is Unit Testing?

A unit test checks **one small, isolated piece of logic** and verifies it returns the correct output for a given input. No database, no network, no external services.

```
Input → [Function] → Output
         ↑
    You test THIS
```

---

### Why It Matters

- Catches bugs **before** they reach production
- Makes refactoring **safe** — if tests pass, you didn't break anything
- Acts as **living documentation** — tests show exactly what a function is supposed to do
- Saves hours of manual testing in the long run

---

### Code that works vs. Code that is tested

```python
# Code that "works" — you ran it once and it seemed fine
def calculate_discount(price, percent):
    return price - (price * percent / 100)

# Code that is TESTED — you know it works for every case
def test_calculate_discount():
    assert calculate_discount(100, 10) == 90    # normal case
    assert calculate_discount(200, 50) == 100   # 50% off
    assert calculate_discount(0, 10)  == 0      # edge: zero price
    assert calculate_discount(100, 0) == 100    # edge: zero discount
```

> **The difference:** "works" means it ran once. "Tested" means you *proved* it works.

---

## Part 3: How to Write a Unit Test (AAA Pattern)

Every test follows three steps: **Arrange → Act → Assert**

```python
def test_get_user_by_id():
    # Arrange — prepare inputs and dependencies
    user_id = 5
    expected_name = "Youssef"

    # Act — call the function you're testing
    result = get_user(user_id)

    # Assert — verify the output is what you expected
    assert result["name"] == expected_name
```

---

## Part 4: Testing a Simple Function

### Python (pytest)

```python
# math_utils.py
def add(a, b):
    return a + b

# test_math_utils.py
import pytest
from math_utils import add

def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 5) == 5
```

Run with:
```bash
pytest test_math_utils.py
```

---

### JavaScript (Jest)

```javascript
// mathUtils.js
function add(a, b) { return a + b; }
module.exports = { add };

// mathUtils.test.js
const { add } = require('./mathUtils');

test('adds two positive numbers', () => {
  expect(add(2, 3)).toBe(5);
});

test('adds negative numbers', () => {
  expect(add(-1, -1)).toBe(-2);
});
```

Run with:
```bash
npx jest
```

---

## Part 5: Testing an API Endpoint

### Scenarios you must cover

| Scenario | Input | Expected |
|----------|-------|----------|
| ✅ Success | Valid ID | `200 OK` + correct data |
| ❌ Invalid input | Missing field | `400 Bad Request` |
| ❌ Not found | Non-existent ID | `404 Not Found` |
| ❌ Server error | DB crashes | `500 Internal Server Error` |

### Python — Testing a Flask/FastAPI endpoint

```python
# test_users_api.py
import pytest
from app import app  # your Flask/FastAPI app

client = app.test_client()

def test_get_user_success():
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json["name"] == "Youssef"

def test_get_user_not_found():
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert "not found" in response.json["error"].lower()

def test_create_user_missing_field():
    response = client.post("/users", json={"name": ""})  # missing job
    assert response.status_code == 400

def test_create_user_success():
    payload = {"name": "Youssef", "job": "Backend Engineer"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    assert "id" in response.json
```

---

## Part 6: Mocking — ببساطة

### ليه بنستخدم Mocking؟

Unit tests must be **isolated** — no real database, no real HTTP calls, no real payment gateway.
Mocking replaces real dependencies with **fake versions** that return controlled responses.

```
Real code:  get_user(id) → hits database → returns user
Mocked:     get_user(id) → fake function → returns {"id": 1, "name": "Youssef"}
```

بكده إنت بتاختبر الـ logic بتاعتك بس، مش الـ database.

### Example — Python (unittest.mock)

```python
from unittest.mock import patch
from users_service import get_user_profile

def test_get_user_profile():
    # Replace the real DB call with a fake one
    with patch("users_service.db.find_user") as mock_db:
        mock_db.return_value = {"id": 1, "name": "Youssef", "role": "admin"}

        result = get_user_profile(1)

        assert result["name"] == "Youssef"
        assert result["role"] == "admin"
        mock_db.assert_called_once_with(1)  # verify it was called correctly
```

### Example — JavaScript (Jest)

```javascript
const userService = require('./userService');
const db = require('./db');

jest.mock('./db');  // replace real db with fake

test('returns user profile', async () => {
  db.findUser.mockResolvedValue({ id: 1, name: 'Youssef' });

  const result = await userService.getUserProfile(1);

  expect(result.name).toBe('Youssef');
  expect(db.findUser).toHaveBeenCalledWith(1);
});
```

---

## Part 7: Best Practices

- **Fast** — each test should run in milliseconds. No sleeping, no real network calls.
- **Independent** — tests must not depend on each other. Order should not matter.
- **One assertion focus** — each test proves one thing. Don't cram 10 assertions in one test.
- **Clear names** — `test_get_user_returns_404_when_not_found` beats `test_case_3`.
- **Test edge cases** — empty strings, zero values, null, very large numbers.
- **Keep tests next to code** — `users.py` and `test_users.py` in the same folder.

---

## Part 8: Common Beginner Mistakes

| Mistake | Why it's a problem | Fix |
|---------|--------------------|-----|
| Testing only the happy path | Bugs live in edge cases | Always test invalid inputs and errors |
| Tests depend on each other | One failure breaks the whole suite | Each test sets up its own data |
| Mocking everything | Tests don't reflect real behavior | Mock only external dependencies |
| Tests are too slow | Developers stop running them | No real I/O in unit tests |
| Vague test names | Hard to know what failed | Name = what you test + what you expect |
| Never running tests | Code drifts from tests | Run tests on every commit (CI/CD) |

---

## Tools Summary

| Language | Unit Testing | Mocking | API Testing |
|----------|-------------|---------|-------------|
| Python | `pytest` / `unittest` | `unittest.mock` | `pytest` + `test_client` |
| JavaScript | `Jest` | `jest.mock()` | `Jest` + `supertest` |
| TypeScript | `Jest` / `Vitest` | `jest.fn()` | `supertest` |

---

## Quick Reference — AAA Cheat Sheet

```
Arrange  →  Set up inputs, mock dependencies
Act      →  Call the function you're testing
Assert   →  Verify the output matches expectations
```

---

*Guide covers: Testing types · Unit testing · AAA pattern · API test scenarios · Mocking · Best practices · Common mistakes*