# 🐛 DEBUGGING GUIDE
### A Practical Guide for Real-World Software Development

> *"Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it."* — Brian W. Kernighan

---

## Table of Contents

1. [🔍 Debugging Mindset](#-debugging-mindset)
2. [🚦 General Debugging Checklist](#-general-debugging-checklist)
3. [🧪 Isolation Strategy](#-isolation-strategy)
4. [🌐 API & Fetch Debugging](#-api--fetch-debugging)
5. [🗄️ Database Debugging](#️-database-debugging)
6. [🖥️ Frontend / UI Debugging](#️-frontend--ui-debugging)
7. [⚠️ Async & Race Conditions](#️-async--race-conditions)
8. [🧾 Logging Strategy](#-logging-strategy)
9. [🧨 Common Bug Patterns](#-common-bug-patterns)
10. [🛠️ Debugging Tools](#️-debugging-tools)
11. [🧭 Step-by-Step Debugging Flow](#-step-by-step-debugging-flow)
12. [💡 Real Examples](#-real-examples)
13. [🆘 Quick Checklist Before Panic](#-quick-checklist-before-panic)
14. [📋 Debugging Questions Cheat Sheet](#-debugging-questions-cheat-sheet)

---

## 🔍 Debugging Mindset

Before touching a single line of code, get your head in the right place. Most bugs are solved with the right thinking, not the most frantic typing.

### Think Like a Detective, Not a Guesser

> Your job is to **find evidence**, build a theory, then **prove it** — not guess randomly until something works.

- **Stop guessing.** Every "let me just try this" without evidence wastes time and can introduce new bugs.
- **Trust the machine.** The computer is doing exactly what you told it to do. The bug is in your instructions, not in its execution.
- **One change at a time.** Changing multiple things simultaneously makes it impossible to know what actually fixed the problem.
- **Read the error message fully.** The answer is often right there. Most developers read the first line and stop — don't.

### The Core Debugging Questions

Always start here. Before doing anything else, answer these:

```
1. What did I EXPECT to happen?
2. What ACTUALLY happened?
3. WHERE exactly in the system did it go wrong?
4. WHEN did this start happening?
5. WHAT changed recently?
```

### Break It Down

A system is a chain of components. A bug lives in **one specific link** of that chain.

```
User Action → UI Event → API Call → Backend Logic → Database Query → Response → UI Update
```

Your job is to walk this chain and find **where the data or behavior breaks down**. Think of it as a pipeline — find the first stage where output looks wrong.

### The Right Attitude

- **Don't panic.** Panicked debugging is just expensive guessing.
- **Stay curious.** Treat bugs as puzzles, not catastrophes.
- **Be humble.** The bug is almost always your fault. Blaming the framework is a trap.
- **Take breaks.** A 10-minute walk has fixed more bugs than 2 hours of staring at a screen.

---

## 🚦 General Debugging Checklist

Use this checklist for **any** bug, regardless of type or layer.

### Step 1 — Define the Problem Clearly

- [ ] What is the **expected** behavior?
- [ ] What is the **actual** behavior?
- [ ] Is there an error message? Copy it **exactly** — don't paraphrase.
- [ ] Is this happening for **all users** or just one? All browsers or just one?
- [ ] Is this happening in **production**, staging, or local dev?

### Step 2 — Reproduce the Bug

- [ ] Can you reproduce it **consistently**? (Same steps, same result?)
- [ ] What are the **exact steps** to reproduce it?
- [ ] Does it happen every time or only **sometimes**? (Intermittent = likely async or race condition)
- [ ] Can you reproduce it in a **simpler, isolated environment**?

### Step 3 — Understand the Timeline

- [ ] When did this **first start** happening?
- [ ] What **changed** around that time? (Deployment? New dependency? Config change?)
- [ ] Check your **git log** — what was the last commit before this broke?

```bash
# Find what changed recently
git log --oneline -20

# Compare current code to last working version
git diff HEAD~1 HEAD -- src/
```

### Step 4 — Gather Evidence

- [ ] Check **server logs** (not just the browser console)
- [ ] Check **network requests** in the browser DevTools Network tab
- [ ] Check the **database** — is the data actually there?
- [ ] Add **temporary log statements** to trace execution flow

### Step 5 — Form a Hypothesis

- [ ] Based on evidence, write down your **best guess** as to the cause
- [ ] What would you expect to see if your hypothesis is correct?
- [ ] How can you **test** your hypothesis without changing production?

### Step 6 — Fix, Verify, Clean Up

- [ ] Make **one specific change** to address the root cause
- [ ] Test the **exact scenario** that was failing
- [ ] Test **related scenarios** to make sure you didn't break something else
- [ ] Remove any **temporary log statements** or debug code
- [ ] Document what the bug was and what fixed it (in your commit message or a comment)

---

## 🧪 Isolation Strategy

The fastest way to find a bug is to eliminate half the system at a time. Think binary search — not linear search.

### Layer Map

```
┌─────────────────────────────────────────┐
│              Browser / Client           │  ← UI Layer
├─────────────────────────────────────────┤
│           JavaScript / Framework        │  ← Frontend Logic
├─────────────────────────────────────────┤
│              HTTP / Network             │  ← Transport Layer
├─────────────────────────────────────────┤
│          Backend / API Server           │  ← Business Logic
├─────────────────────────────────────────┤
│              Database / Cache           │  ← Data Layer
└─────────────────────────────────────────┘
```

### How to Isolate Each Layer

#### Is it a UI problem?
- Open DevTools → Network tab → trigger the action
- Is the network request **being made at all**?
  - **NO** → Bug is in frontend JavaScript (event handler, state, click not wired up)
  - **YES** → Move down to the next layer

#### Is it a Network / API problem?
- Look at the request in the Network tab
- What is the **status code**? (200, 400, 404, 500?)
- What is the **response body**?
  - **Status 200, but wrong data** → Bug is in backend logic or database
  - **Status 4xx** → Bad request from frontend (wrong URL, missing params, auth issue)
  - **Status 5xx** → Bug is in backend (check server logs)
  - **No request at all** → Bug is in frontend

#### Is it a Backend problem?
- Test the API endpoint **directly** using a tool like Postman, curl, or Insomnia
- Bypass the frontend entirely
  ```bash
  curl -X GET "https://api.yourapp.com/users/123" \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json"
  ```
- Does it return correct data when called directly?
  - **YES** → Bug is in frontend (how it's calling the API)
  - **NO** → Bug is in backend logic or database

#### Is it a Database problem?
- Query the database **directly**
- Does the expected data exist?
- Is it structured correctly?
  ```sql
  -- Check if the record exists
  SELECT * FROM users WHERE id = 123;

  -- Check related data
  SELECT u.*, p.* FROM users u
  LEFT JOIN profiles p ON p.user_id = u.id
  WHERE u.id = 123;
  ```

### Disabling Parts of the System

When you can't figure out which layer is broken, **comment out or stub pieces** to narrow it down:

```javascript
// Instead of calling the real API, use hardcoded data
// to test if the UI layer works correctly
const data = { id: 1, name: "Test User" }; // Stubbed data
// const data = await fetchUser(123);       // Real call (disabled)

renderUserProfile(data);
```

If the UI renders correctly with stubbed data → the bug is in the fetch/API layer.

---

## 🌐 API & Fetch Debugging

### Check Response Status First

HTTP status codes tell you **what category of problem** you have:

| Status | Meaning | Where to look |
|--------|---------|---------------|
| 200 | OK — but check the body | Backend logic or DB |
| 201 | Created successfully | Usually fine |
| 204 | No content returned | Did you expect content? |
| 400 | Bad Request | Your request is malformed |
| 401 | Unauthorized | Auth token missing or expired |
| 403 | Forbidden | Token valid, but no permission |
| 404 | Not Found | Wrong URL or resource deleted |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limiting |
| 500 | Server Error | Backend crashed — check server logs |
| 503 | Service Unavailable | Server overloaded or down |

### Log the Full Response (Headers + Body)

Never assume what the response contains. Log everything:

```javascript
async function debugFetch(url, options = {}) {
  console.log(`[FETCH] ${options.method || 'GET'} ${url}`);
  console.log('[FETCH] Request options:', JSON.stringify(options, null, 2));

  const response = await fetch(url, options);

  console.log('[FETCH] Status:', response.status, response.statusText);
  console.log('[FETCH] Headers:', Object.fromEntries(response.headers.entries()));

  // Clone the response so we can read it AND return it
  const cloned = response.clone();
  const text = await cloned.text();
  console.log('[FETCH] Raw body:', text);

  return response;
}
```

### Handle Non-JSON Responses Safely

A common crash point: assuming the response is always JSON.

```javascript
// ❌ BAD — crashes if response is HTML (like a 500 error page)
const data = await response.json();

// ✅ GOOD — safely handles any response type
async function safeJsonParse(response) {
  const contentType = response.headers.get('Content-Type') || '';

  if (!contentType.includes('application/json')) {
    const text = await response.text();
    console.error('[API] Expected JSON but got:', contentType);
    console.error('[API] Response body:', text);
    throw new Error(`Non-JSON response: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
```

### Safe Fetch Handler (Copy-Paste Ready)

```javascript
async function apiFetch(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    // Log for debugging (remove in production)
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${options.method || 'GET'} ${url} → ${response.status}`);
    }

    // Handle non-2xx responses
    if (!response.ok) {
      let errorBody;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = await response.text();
      }

      const error = new Error(`API Error: ${response.status} ${response.statusText}`);
      error.status = response.status;
      error.body = errorBody;
      throw error;
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) return null;

    return await response.json();

  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      console.error('[API] Network error — is the server running?', error);
      throw new Error('Network error: Could not reach the server');
    }
    throw error;
  }
}
```

### CORS Debugging

CORS errors look scary but the fix is usually simple:

```
Access to fetch at 'https://api.example.com' from origin 'http://localhost:3000'
has been blocked by CORS policy.
```

**Checklist:**
- [ ] Is the server sending the correct `Access-Control-Allow-Origin` header?
- [ ] Are you sending credentials (`withCredentials`)? The server must send `Access-Control-Allow-Credentials: true`
- [ ] For preflight requests (PUT, DELETE, custom headers) — does the server handle `OPTIONS` requests?
- [ ] Is this only happening in development? Use a proxy in `package.json` or `vite.config.js`

```javascript
// vite.config.js — proxy API calls to avoid CORS in dev
export default {
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
}
```

---

## 🗄️ Database Debugging

### Step 1 — Does the Data Actually Exist?

The most common database bug: you're looking for data that was never saved.

```sql
-- Check if record exists
SELECT COUNT(*) FROM orders WHERE id = 456;

-- See what's actually there
SELECT * FROM orders WHERE id = 456;

-- Check recently inserted records
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
```

### Step 2 — Verify Relationships (Foreign Keys)

```sql
-- Does the user referenced by this order actually exist?
SELECT o.id, o.user_id, u.id AS user_exists
FROM orders o
LEFT JOIN users u ON u.id = o.user_id
WHERE o.id = 456;

-- Find orphaned records (data integrity problem)
SELECT o.*
FROM orders o
LEFT JOIN users u ON u.id = o.user_id
WHERE u.id IS NULL;  -- Orders with no matching user
```

### Step 3 — NULL vs CASCADE Issues

```sql
-- Check for unexpected NULLs
SELECT * FROM products WHERE price IS NULL;
SELECT * FROM users WHERE email IS NULL OR email = '';

-- Check what happens when you delete a user
-- Does the database cascade? Or leave orphans?
SHOW CREATE TABLE orders;  -- Look for ON DELETE CASCADE / SET NULL / RESTRICT
```

### Step 4 — Debug Slow or Wrong Queries

```sql
-- See the query execution plan
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- Is there an index on user_id? Look for "Using index" vs "Using filescan"
-- If no index, add one:
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

### Common Database Mistakes

```sql
-- ❌ BAD — typo in column name returns NULL silently in some databases
SELECT user_name FROM users WHERE id = 1;

-- ❌ BAD — comparing NULL with = always returns false
SELECT * FROM users WHERE deleted_at = NULL;   -- Always empty!

-- ✅ GOOD — correct NULL comparison
SELECT * FROM users WHERE deleted_at IS NULL;

-- ❌ BAD — LIKE without wildcard is just an exact match
SELECT * FROM users WHERE name LIKE 'John';

-- ✅ GOOD — LIKE with wildcards
SELECT * FROM users WHERE name LIKE '%John%';
```

### Transaction Debugging

```sql
-- If data seems to disappear or not save, check for uncommitted transactions
-- In PostgreSQL:
SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';

-- A transaction that was never committed = data that looks saved but isn't
BEGIN;
  INSERT INTO users (name) VALUES ('Alice');
  -- If you crash or disconnect here, the INSERT never happened
COMMIT;  -- This is what actually saves it
```

---

## 🖥️ Frontend / UI Debugging

### Buttons Not Working

When clicking a button does absolutely nothing:

```javascript
// Step 1: Is the event listener actually attached?
const button = document.getElementById('submit-btn');
console.log('Button element:', button);  // null? Wrong selector.

// Step 2: Add a test listener directly in the console
document.getElementById('submit-btn').addEventListener('click', () => {
  console.log('Button clicked!');
});

// Step 3: Check for event propagation issues
button.addEventListener('click', (e) => {
  e.stopPropagation();  // Is something else catching this event first?
  console.log('Click event fired');
});
```

**Common causes:**
- Element not yet in the DOM when listener was attached (timing issue)
- Wrong selector — ID has a typo, or class used instead of ID
- Another element is overlapping and blocking clicks (check with `pointer-events` in CSS)
- Button is disabled via CSS `pointer-events: none`

```javascript
// Check if element exists at the time you're attaching the listener
document.addEventListener('DOMContentLoaded', () => {
  // ✅ GOOD — DOM is ready
  document.getElementById('submit-btn').addEventListener('click', handleClick);
});

// ❌ BAD — Running before DOM is loaded
document.getElementById('submit-btn').addEventListener('click', handleClick);
```

### Event Listeners Not Firing

```javascript
// Is the element being recreated dynamically? Use event delegation instead
// ❌ BAD — attaches to specific element that might be replaced
document.getElementById('dynamic-item').addEventListener('click', handler);

// ✅ GOOD — event delegation, works even when children are replaced
document.getElementById('parent-container').addEventListener('click', (e) => {
  if (e.target.matches('.dynamic-item')) {
    handler(e);
  }
});
```

### State Not Updating (React)

```javascript
// ❌ BAD — mutating state directly, React won't re-render
const [items, setItems] = useState([]);
items.push(newItem);  // React doesn't know about this change

// ✅ GOOD — always create a new array/object
setItems([...items, newItem]);

// ❌ BAD — stale closure problem with useEffect
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1);  // 'count' is stale!
  }, 1000);
  return () => clearInterval(interval);
}, []);  // Missing dependency

// ✅ GOOD — use functional update
useEffect(() => {
  const interval = setInterval(() => {
    setCount(prev => prev + 1);  // Always uses latest value
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### DOM Inspection Using DevTools

**The most useful DevTools tricks for UI debugging:**

```
Elements Panel:
  → Right-click on element → "Break on" → "Subtree modifications"
    This pauses JS when that element changes — great for finding what's changing the DOM

Console:
  → $0 → refers to the currently selected element in Elements panel
  → $('selector') → shortcut for document.querySelector()
  → $$('selector') → shortcut for document.querySelectorAll()
  → getEventListeners($0) → lists all event listeners on selected element

Sources Panel (Breakpoints):
  → Click the line number to set a breakpoint
  → Right-click → "Add conditional breakpoint" to break only when a condition is true
  → "Never pause here" to skip third-party library breakpoints
```

---

## ⚠️ Async & Race Conditions

### What Is Async Behavior?

Async code doesn't run top-to-bottom like a recipe. It starts a task, continues running other code, and comes back when the task is done.

```javascript
// What you THINK happens:
const user = fetchUser(123);   // Waits for this...
const posts = fetchPosts(user.id);  // ...then does this

// What ACTUALLY happens without await:
const user = fetchUser(123);   // Starts fetching, returns a Promise immediately
const posts = fetchPosts(user.id);  // user is a Promise, not a user object!
// posts will fail because user.id is undefined
```

### What Is a Race Condition?

A race condition happens when **two async operations run in parallel** and the one that finishes last "wins" — even when you expected a specific order.

```javascript
// Classic race condition example:
async function searchUsers(query) {
  setLoading(true);
  const results = await api.search(query);  // This takes variable time
  setResults(results);
  setLoading(false);
}

// User types "jo" → triggers searchUsers("jo")
// User types "john" → triggers searchUsers("john")
// "jo" query returns AFTER "john" → shows "jo" results even though "john" was typed last
```

### Real Examples of Race Conditions

**Example 1: Double-click submitting a form twice**
```javascript
// ❌ BAD — double-click sends request twice
button.addEventListener('click', async () => {
  const result = await submitForm(formData);
  // User clicked again while this was waiting!
});

// ✅ GOOD — use a flag to prevent concurrent submissions
let isSubmitting = false;
button.addEventListener('click', async () => {
  if (isSubmitting) return;
  isSubmitting = true;
  button.disabled = true;

  try {
    const result = await submitForm(formData);
    // handle result
  } finally {
    isSubmitting = false;
    button.disabled = false;
  }
});
```

**Example 2: Stale search results**
```javascript
// ✅ GOOD — cancel previous request when a new one starts
let currentSearch = null;

async function searchUsers(query) {
  // Cancel previous search
  if (currentSearch) {
    currentSearch.abort();
  }

  const controller = new AbortController();
  currentSearch = controller;

  try {
    const results = await api.search(query, { signal: controller.signal });
    setResults(results);  // Only runs if not cancelled
  } catch (error) {
    if (error.name !== 'AbortError') {
      // Only log real errors, not cancellations
      console.error('Search failed:', error);
    }
  }
}
```

**Example 3: Sequencing dependent requests**
```javascript
// ❌ BAD — parallel requests when the second depends on the first
const user = await fetchUser(123);
const [profile, posts] = await Promise.all([
  fetchProfile(user.id),
  fetchPosts(user.id)  // Fine — both only need user.id
]);

// ✅ GOOD — sequential only when necessary, parallel when possible
const user = await fetchUser(123);         // Must come first
const [profile, posts] = await Promise.all([  // These can run in parallel
  fetchProfile(user.id),
  fetchPosts(user.id),
  fetchSettings(user.id)
]);
```

---

## 🧾 Logging Strategy

### What to Log

| Event | Log? | What to include |
|-------|------|-----------------|
| API request starts | ✅ | Method, URL, key params (not passwords) |
| API request completes | ✅ | Status code, response time |
| API request fails | ✅ | Full error, request details |
| User action | ✅ | Action name, relevant ID |
| Data written to DB | ✅ | Table, ID, key fields |
| Auth events | ✅ | User ID, success/failure |
| Passwords / tokens | ❌ | Never log these |
| Full request bodies | ⚠️ | Only in dev — may contain sensitive data |

### Good vs Bad Logging

```javascript
// ❌ BAD — vague, tells you nothing useful
console.log('Error occurred');
console.log('done');
console.log(data);

// ❌ BAD — logs sensitive information
console.log('User logged in:', user);  // logs password hash too!

// ✅ GOOD — specific, structured, safe
console.log('[Auth] User login success:', { userId: user.id, email: user.email });
console.log('[API] GET /users/123 → 200 (45ms)');
console.error('[DB] Failed to insert order:', {
  error: err.message,
  userId: order.userId,
  items: order.items.length,
});
```

### Log Levels — Use the Right One

```javascript
// Use the appropriate level for each situation

console.debug('[Cache] Hit for key:', cacheKey);     // Verbose, dev only
console.info('[Server] Started on port 3000');        // Informational
console.warn('[Config] ENV var REDIS_URL not set, using default');  // Something might go wrong
console.error('[DB] Connection failed:', error);       // Something went wrong

// In production, suppress debug/info to reduce noise
// Most logging libraries let you set a minimum level
```

### Structured Logging (Production-Ready)

```javascript
// Instead of string-based logs, use structured objects
// This makes logs searchable in tools like Datadog, Splunk, or CloudWatch

// ❌ Less searchable
console.log(`User ${userId} purchased item ${itemId} for $${price}`);

// ✅ More searchable and parseable
logger.info({
  event: 'purchase_completed',
  userId,
  itemId,
  price,
  currency: 'USD',
  timestamp: new Date().toISOString(),
});
```

---

## 🧨 Common Bug Patterns

### 1. Undefined / Null Errors

```javascript
// Error: Cannot read properties of undefined (reading 'name')

// ❌ The problem
const user = getUser();
console.log(user.name);  // user might be undefined!

// ✅ Fix — check before accessing
const user = getUser();
if (!user) {
  console.error('User not found');
  return;
}
console.log(user.name);

// ✅ Modern fix — optional chaining
console.log(user?.name ?? 'Unknown');
```

### 2. Wrong API URL

```javascript
// These are all different URLs:
/api/user     // Relative path — depends on current host
/api/users    // Note: 'users' not 'user'
/api/users/   // Trailing slash (some servers treat this differently)
http://localhost:3000/api/users  // Absolute with port

// Always log the full URL you're actually calling:
console.log('[API] Calling:', `${baseURL}${endpoint}`);
```

### 3. CORS Issues

```
Common mistake: thinking CORS is a frontend problem.
CORS is configured on the SERVER. The browser enforces it.
```

```javascript
// Backend fix (Express.js example):
const cors = require('cors');
app.use(cors({
  origin: ['http://localhost:3000', 'https://yourapp.com'],
  credentials: true,  // Required if using cookies/auth headers
}));
```

### 4. Wrong Environment Variables

```javascript
// ❌ Hard to debug — wrong variable is silently undefined
const apiUrl = process.env.API_URL;  // Is this set? Which env?

// ✅ Better — validate at startup
function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}

const apiUrl = requireEnv('API_URL');
```

### 5. Timing Issues

```javascript
// ❌ BAD — element doesn't exist yet when code runs
document.getElementById('app').innerHTML = template;
document.getElementById('submit-btn').addEventListener('click', handler);  // null!

// ✅ GOOD — use callbacks or await rendering
document.getElementById('app').innerHTML = template;
// Wait for next render cycle
requestAnimationFrame(() => {
  document.getElementById('submit-btn').addEventListener('click', handler);
});
```

### 6. Off-by-One Errors

```javascript
// ❌ BAD — misses last item, or goes out of bounds
for (let i = 0; i <= array.length; i++) {  // Should be < not <=
  console.log(array[i]);  // Last iteration: array[array.length] is undefined
}

// ✅ GOOD
for (let i = 0; i < array.length; i++) {
  console.log(array[i]);
}
// Or better:
array.forEach(item => console.log(item));
```

### 7. Mutating Shared State

```javascript
// ❌ BAD — modifying an object that other code is using
function processUser(user) {
  user.name = user.name.trim();  // Mutates the original!
  return user;
}

// ✅ GOOD — create a copy, never mutate inputs
function processUser(user) {
  return { ...user, name: user.name.trim() };
}
```

---

## 🛠️ Debugging Tools

### Browser DevTools

| Panel | What it's for |
|-------|--------------|
| **Elements** | Inspect/modify DOM & CSS live |
| **Console** | Run JS, see errors & logs |
| **Network** | See all HTTP requests, responses, timing |
| **Sources** | Set breakpoints, step through code |
| **Performance** | Find slow rendering & JS execution |
| **Application** | Inspect localStorage, cookies, IndexedDB |
| **Memory** | Find memory leaks |

**Most useful Network tab tricks:**
- Filter by `Fetch/XHR` to see only API calls
- Click a request → "Preview" to see formatted JSON
- Right-click → "Copy as cURL" to replay the exact request in terminal
- Look at the **Timing** tab to see where time is being spent

### Backend Debugging Tools

```bash
# Watch logs in real-time (Node.js)
tail -f logs/app.log | grep ERROR

# See all requests hitting your server
# In Express, use morgan:
app.use(require('morgan')('dev'));

# Query slow queries in PostgreSQL
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### curl — Test APIs Without a Browser

```bash
# GET request
curl -i https://api.example.com/users/123

# POST request with JSON body
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name": "Alice", "email": "alice@example.com"}'

# See full request and response headers (-v = verbose)
curl -v https://api.example.com/users

# Save response to file for inspection
curl -o response.json https://api.example.com/users
```

### Other Essential Tools

| Tool | Purpose |
|------|---------|
| **Postman / Insomnia** | GUI API testing |
| **VS Code Debugger** | Step-through debugging with breakpoints |
| **React DevTools** | Inspect component state & props |
| **Redux DevTools** | Time-travel debugging for Redux state |
| **Sentry** | Automatic error capturing in production |
| **Datadog / LogRocket** | Production monitoring & session replay |
| **pgAdmin / TablePlus** | Visual database inspection |
| **Wireshark** | Network packet inspection (advanced) |

---

## 🧭 Step-by-Step Debugging Flow

Use this universal process for **any bug** you encounter:

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: REPRODUCE                                       │
│  → Can you make the bug happen reliably?                 │
│  → Write down the exact steps                            │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 2: READ THE ERROR                                  │
│  → Read the full error message (not just line 1)         │
│  → Check browser console + server logs                   │
│  → Search the exact error message if unclear             │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 3: IDENTIFY THE LAYER                              │
│  → UI? Network? Backend? Database?                       │
│  → Use isolation strategy (binary search the system)     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 4: ADD TARGETED LOGS                               │
│  → Log inputs and outputs at the suspected failure point │
│  → Log BEFORE and AFTER the suspected bad line           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 5: INSPECT THE DATA                                │
│  → What does the data look like at the failure point?    │
│  → Is it what you expected? (type, shape, value)         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 6: FORM A HYPOTHESIS                               │
│  → "I think the bug is X because I saw Y in the logs"    │
│  → Write it down — makes you commit to a theory          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 7: FIX ONE THING                                   │
│  → Make ONE targeted change                              │
│  → Don't "clean up" other things while you're here       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 8: VERIFY                                          │
│  → Test the exact failing scenario                       │
│  → Test related scenarios (regression check)             │
│  → Bug still there? → Go back to Step 3                  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 9: CLEAN UP & DOCUMENT                             │
│  → Remove debug logs and temporary code                  │
│  → Write a clear commit message explaining the fix       │
│  → Consider: how do I prevent this class of bug?         │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 Real Examples

### Example 1: API Returns Empty Data

**Symptom:** The page loads but shows no data. No error messages.

**Debugging process:**

```javascript
// Step 1: Check if the API call is happening at all
// Open DevTools → Network tab → look for the request

// Step 2: What does the response look like?
// Status 200 but body is: { "data": [] }

// Step 3: Call the endpoint directly with curl
curl "https://api.example.com/products?category=shoes"
// Returns: { "data": [] }

// Step 4: Check the database directly
SELECT COUNT(*) FROM products WHERE category = 'shoes';
-- Returns: 0

// Step 5: Check what categories actually exist
SELECT DISTINCT category FROM products;
-- Returns: 'Shoes' (capital S!)

// Root cause: Frontend sends category=shoes (lowercase)
// Database has 'Shoes' (capitalized) — case-sensitive comparison

// Fix: normalize in the query
SELECT * FROM products
WHERE LOWER(category) = LOWER($1);
```

### Example 2: Button Click Does Nothing

**Symptom:** User clicks "Submit" button. Nothing happens. No error.

**Debugging process:**

```javascript
// Step 1: Open DevTools Console — any errors? (No)

// Step 2: Check if the button exists
console.log(document.getElementById('submit-btn'));
// Output: null ← Found it!

// Step 3: Check the HTML — button has class, not ID
// <button class="submit-btn">Submit</button>

// Step 4: Check the JavaScript
document.getElementById('submit-btn')  // ← Wrong! Looking for ID
// Should be:
document.querySelector('.submit-btn')  // ← Correct (class selector)

// Fix: Update the selector
document.querySelector('.submit-btn').addEventListener('click', handleSubmit);

// Or better: fix the HTML to use an ID since IDs are unique
// <button id="submit-btn">Submit</button>
```

### Example 3: Data Not Saved in Database

**Symptom:** User fills out a form, clicks save, sees "Saved!" message, refreshes the page — data is gone.

**Debugging process:**

```javascript
// Step 1: Check the Network tab
// POST /api/profile → Status 200 ✓
// Response: { "success": true } ✓

// Step 2: Check the database directly
SELECT * FROM user_profiles WHERE user_id = 123;
// Returns: (0 rows)

// Step 3: Add logging to the backend save function
async function saveProfile(userId, data) {
  console.log('[DB] Attempting to save profile for user:', userId);
  console.log('[DB] Data:', data);

  const result = await db.query(
    'UPDATE user_profiles SET bio = $1 WHERE user_id = $2',
    [data.bio, userId]
  );

  console.log('[DB] Rows affected:', result.rowCount);  // ← Output: 0
}

// Step 4: rowCount is 0 — UPDATE found no matching row
// The user doesn't have a profile record yet!

// Root cause: Trying to UPDATE a row that doesn't exist

// Fix: Use UPSERT (INSERT ... ON CONFLICT UPDATE)
await db.query(`
  INSERT INTO user_profiles (user_id, bio)
  VALUES ($1, $2)
  ON CONFLICT (user_id)
  DO UPDATE SET bio = EXCLUDED.bio
`, [userId, data.bio]);
```

---

## 🆘 Quick Checklist Before Panic

When everything feels broken and you don't know where to start — run this list first:

```
□ Did you save the file?
□ Did you restart the server / rebuild the bundle?
□ Is the correct branch checked out?
□ Did someone else push a breaking change? (check git log)
□ Is the database running? (can you connect to it?)
□ Are environment variables set correctly?
□ Is there a syntax error somewhere? (check the console — it shows you the line)
□ Did you clear browser cache? (Ctrl+Shift+R for hard refresh)
□ Is the API server running? (curl localhost:PORT/health)
□ Are node_modules up to date? (try npm install)
□ Is this a known issue? (check GitHub Issues / Slack / error tracker)
□ Has this ever worked before? What changed since then?
```

**If all else fails:**

1. `git stash` your changes and test if the bug existed before your changes
2. `git log --oneline -10` — find the last working commit and do `git checkout <hash>` to test it
3. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
4. Explain the problem out loud to a rubber duck (or a colleague) — you'll often find it yourself

---

## 📋 Debugging Questions Cheat Sheet

Print this out. Keep it nearby. Use it every time.

### When You First See a Bug

```
1. What exactly is the error message? (Copy it word for word)
2. What did I expect to happen?
3. What actually happened instead?
4. Can I reproduce it? How?
5. Is this happening for everyone or just me?
6. When did this start? What changed?
```

### When Isolating the Problem

```
7.  Is the data correct in the database?
8.  Is the API returning the correct data?
9.  Is the frontend receiving the correct data?
10. Is the frontend displaying the data correctly?
11. Where exactly does the data become wrong?
12. What does the data look like at each stage?
```

### When You Think You Found It

```
13. What exactly is the root cause? (Be specific)
14. Why does this cause the symptom I'm seeing?
15. Does my fix actually address the root cause?
16. Could this fix break anything else?
17. How do I verify the fix worked?
```

### When You're Stuck

```
18. Have I actually read the full error message?
19. Have I checked the logs on all layers (browser, server, DB)?
20. Did I try it with hardcoded/simplified data?
21. Did I search this exact error message online?
22. Can I explain the problem clearly to someone else?
23. Have I been staring at this for more than 30 minutes? (Take a break)
24. What's the simplest possible explanation?
25. Am I solving the right problem? (Is this the real issue or a symptom?)
```

---

## Final Thoughts

Debugging is a skill that improves with practice. Every bug you solve teaches you something about how systems work. The developers who debug fastest aren't the ones who know every answer — they're the ones with a **reliable process**.

**The golden rules:**

> 🔎 **Evidence over intuition** — prove it, don't guess it  
> 🎯 **One change at a time** — know what fixed it  
> 📍 **Isolate, then zoom in** — binary search the system  
> 📝 **Log first, fix second** — understand before you change  
> 😮‍💨 **Take breaks** — fresh eyes find what tired eyes miss  

---

*Last updated: 2025 | Maintained as a living document — update it when you discover new patterns.*
