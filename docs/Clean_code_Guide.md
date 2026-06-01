# Clean Code — Practical Guide

> How to know your code is good, and how to make it better.

---

## Part 1: How to Know Your Code is Good?

### Code that "just works" vs. Code that is scalable & clean

| | Code that "just works" | Clean & Scalable Code |
|---|---|---|
| **It runs?** | ✅ Yes | ✅ Yes |
| **Someone else can read it?** | ❌ Rarely | ✅ Easily |
| **Easy to change later?** | ❌ Risky | ✅ Safe |
| **Easy to test?** | ❌ Hard | ✅ Straightforward |
| **Breaks when it grows?** | ❌ Often | ✅ Handles growth |
| **You understand it 3 months later?** | ❌ "Who wrote this?" | ✅ Reads like English |

### The honest test

Ask yourself these three questions:

1. **Can a teammate understand this function in under 30 seconds?**
2. **If requirements change, how much do I need to rewrite?**
3. **Can I write a unit test for this without fighting the code?**

If the answer to any of these is "no" — the code works, but it isn't good.

> **"Any fool can write code that a computer can understand.**
> **Good programmers write code that humans can understand."**
> — Martin Fowler

---

## Part 2: The Difference — Side by Side

```python
# Code that "just works"
def p(u):
    d = db.get(u)
    if d[2] == 1:
        d[4] = d[4] * 0.9
    return d
```

What is `p`? What is `d[2]`? What does `0.9` mean? Nobody knows.

```python
# Clean & scalable code
PREMIUM_DISCOUNT = 0.10

def get_user_with_discount(user_id: int) -> dict:
    user = db.get_user(user_id)
    if user["is_premium"]:
        user["price"] = apply_discount(user["price"], PREMIUM_DISCOUNT)
    return user

def apply_discount(price: float, discount_rate: float) -> float:
    return price * (1 - discount_rate)
```

Same logic. Completely different readability, testability, and maintainability.

---

## Part 3: Clean Code Basics

### 1. Naming variables correctly

Names should answer: *what is this? what does it do?*

```python
# Bad
x = 86400
def calc(a, b):
    return a * b

# Good
SECONDS_IN_A_DAY = 86400
def calculate_total_price(quantity: int, unit_price: float) -> float:
    return quantity * unit_price
```

**Rules:**
- Variables → nouns: `user`, `invoice_total`, `is_active`
- Functions → verbs: `get_user()`, `send_email()`, `calculate_tax()`
- Booleans → questions: `is_valid`, `has_permission`, `can_retry`
- No single letters (`x`, `d`, `n`) except loop counters (`i`, `j`)

---

### 2. Avoid long functions

A function should do **one thing** and fit on one screen (~20 lines max).
If you need to scroll to read a function — it's doing too much.

```python
# Bad — one giant function doing everything
def process_order(order_id):
    order = db.get_order(order_id)
    if order["items"] == []:
        raise ValueError("Empty order")
    total = sum(item["price"] * item["qty"] for item in order["items"])
    if order["user"]["is_premium"]:
        total = total * 0.9
    payment = stripe.charge(order["user"]["card"], total)
    db.update_order(order_id, status="paid", payment_id=payment.id)
    send_email(order["user"]["email"], subject="Order confirmed", body=f"Total: {total}")
    return {"status": "success", "total": total}

# Good — each step is its own function
def process_order(order_id):
    order      = get_order(order_id)
    total      = calculate_order_total(order)
    payment    = charge_customer(order["user"], total)
    finalize_order(order_id, payment)
    notify_customer(order["user"], total)
    return {"status": "success", "total": total}
```

The second version reads like a checklist. You know exactly what happens at each step.

---

### 3. Single Responsibility Principle (SRP)

> Every function, class, or module should have **one reason to change**.

```python
# Bad — one class doing too much
class User:
    def get_user(self, user_id): ...
    def save_to_db(self): ...
    def send_welcome_email(self): ...
    def generate_pdf_report(self): ...

# Good — each class has one job
class UserRepository:
    def get_user(self, user_id): ...
    def save(self, user): ...

class EmailService:
    def send_welcome_email(self, user): ...

class ReportService:
    def generate_pdf(self, user): ...
```

**Why it matters:** if the email logic changes, you only touch `EmailService`.
Nothing else breaks.

---

### 4. Write readable code

Code is read far more than it is written. Optimize for the reader.

```python
# Bad — clever but unreadable
result = [u for u in users if u["a"] and not u["b"] and u["c"] > 2]

# Good — clear intent
def is_eligible_for_promotion(user: dict) -> bool:
    return user["is_active"] and not user["is_banned"] and user["order_count"] > 2

eligible_users = [u for u in users if is_eligible_for_promotion(u)]
```

**Rules:**
- Avoid clever one-liners that require decoding
- Use intermediate variables to name intent
- Magic numbers → named constants (`0.1` → `DISCOUNT_RATE = 0.1`)
- Comments explain *why*, not *what* (the code explains what)

```python
# Bad comment — states the obvious
# multiply price by 0.9
price = price * 0.9

# Good comment — explains the why
# Apply 10% loyalty discount for users who stayed more than 1 year
price = price * (1 - LOYALTY_DISCOUNT_RATE)
```

---

### 5. Avoid duplication (DRY — Don't Repeat Yourself)

If you copy-paste code, you now have two places to fix when something changes.

```python
# Bad — duplicated logic
def get_admin_greeting(name):
    name = name.strip().title()
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Welcome, Admin {name}!"

def get_user_greeting(name):
    name = name.strip().title()
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Welcome, {name}!"

# Good — shared logic extracted once
def format_name(name: str) -> str:
    name = name.strip().title()
    if not name:
        raise ValueError("Name cannot be empty")
    return name

def get_admin_greeting(name: str) -> str:
    return f"Welcome, Admin {format_name(name)}!"

def get_user_greeting(name: str) -> str:
    return f"Welcome, {format_name(name)}!"
```

---

## Part 4: Real Example — Bad vs. Clean

### Bad code

```python
def do_thing(uid, c):
    u = db.execute(f"SELECT * FROM users WHERE id = {uid}")
    if u is None:
        return None
    if c == "USD":
        bal = u[3] * 1.0
    elif c == "EGP":
        bal = u[3] * 30.5
    elif c == "EUR":
        bal = u[3] * 0.92
    print(f"User {u[1]} has {bal}")
    return bal
```

**Problems:**
- Name `do_thing` tells you nothing
- Raw SQL with string interpolation → SQL injection risk
- Magic numbers (`30.5`, `0.92`) with no explanation
- Mixes data fetching, conversion logic, and printing in one function
- Impossible to unit test cleanly

---

### Clean version

```python
EXCHANGE_RATES = {
    "USD": 1.0,
    "EGP": 30.5,
    "EUR": 0.92,
}

def get_user_balance_in_currency(user_id: int, currency: str) -> float:
    user = UserRepository.find_by_id(user_id)
    if user is None:
        raise UserNotFoundError(f"No user with id {user_id}")

    rate = get_exchange_rate(currency)
    converted_balance = user.balance * rate
    return converted_balance

def get_exchange_rate(currency: str) -> float:
    if currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {currency}")
    return EXCHANGE_RATES[currency]
```

**What improved:**
- Clear function name → you know exactly what it does
- Parameterized query via repository → no SQL injection
- Exchange rates in a named constant → one place to update
- Three separate concerns: fetch, convert, return
- Each piece is independently testable

---

## Quick Reference Checklist

Before you commit code, ask:

- [ ] Can a teammate read this function without asking me questions?
- [ ] Does each function do exactly one thing?
- [ ] Are all variable and function names meaningful?
- [ ] Is there any copy-pasted logic that should be extracted?
- [ ] Are magic numbers replaced with named constants?
- [ ] Can I write a unit test for this without restructuring it first?

---

*Guide covers: Code quality signals · Naming · Function length · SRP · Readability · DRY principle · Bad vs. clean real example*