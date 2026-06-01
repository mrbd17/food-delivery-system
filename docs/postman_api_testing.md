# Postman API Testing — Practical Guide

> A concise, example-driven reference for backend engineers.

---

## 1. What is Postman?

Postman is a GUI tool for sending HTTP requests and inspecting responses — no code needed. Backend engineers use it to:

- Test API endpoints during development
- Validate request/response behavior
- Debug errors quickly
- Share request collections with teammates

---

## 2. Anatomy of a Request

| Part | Description | Example |
|------|-------------|---------|
| **Method** | HTTP verb | `GET`, `POST`, `PUT`, `DELETE` |
| **URL** | Endpoint address | `https://api.example.com/users/42` |
| **Params** | Query string key-values | `?page=1&limit=20` |
| **Headers** | Metadata about the request | `Content-Type: application/json` |
| **Body** | Data payload (POST/PUT only) | Raw JSON, form-data |

### Body types

- **raw / JSON** — for creating or updating resources (`POST`, `PUT`)
- **form-data** — for file uploads or multipart forms
- **none** — for `GET` and `DELETE` requests

---

## 3. Authentication Basics

### Bearer Token
In the **Authorization** tab → select **Bearer Token** → paste your JWT or OAuth token.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### API Key
Add a custom header directly:

```
x-api-key: YOUR_API_KEY
```

Or as a query param: `?api_key=YOUR_API_KEY` (depends on the API's spec).

---

## 4. How to Test a Real API — Step by Step

### POST — Create a resource

1. Method = `POST` | URL = `https://reqres.in/api/users`
2. Headers → `Content-Type: application/json`
3. Body → raw → JSON:

```json
{
  "name": "Youssef",
  "job": "Backend Engineer"
}
```

4. Hit **Send** → expect **201 Created**
5. Copy the returned `id` field — you'll use it for DELETE

---

### DELETE — Delete a resource

1. Method = `DELETE` | URL = `https://reqres.in/api/users/2`
2. No body needed — the resource is identified by the URL
3. Hit **Send** → expect **204 No Content** (empty body is correct)

---

### DELETE — Resource does NOT exist

1. Use a non-existent ID → `https://reqres.in/api/users/99999`
2. Expect **404 Not Found** with an error body like:

```json
{
  "error": "User not found"
}
```

> ⚠️ If you get a `500` here, that's a **backend bug** — the server must handle missing resources gracefully, not crash.

---

## 5. Reading Responses

Always check: **status code**, **response body**, **response time**, and **headers**.

| Code | Meaning | When you see it |
|------|---------|-----------------|
| `200` | OK | GET / PUT succeeded, resource returned |
| `201` | Created | POST succeeded, new resource was made |
| `400` | Bad Request | Invalid body, missing required field |
| `401` | Unauthorized | Token is missing, expired, or wrong |
| `404` | Not Found | Endpoint or resource doesn't exist |
| `500` | Server Error | Bug on the backend — check server logs |

---

## 6. Debugging Tips

**Request fails immediately?**
Check the URL for typos, wrong port, or missing `https://`. Open Postman's **Console** tab (`View → Show Postman Console`) for raw network errors.

**Getting 401?**
Your token is missing, expired, or placed in the wrong header. Re-authenticate and retry. Double-check the auth scheme (`Bearer` vs `ApiKey` vs custom header).

**Getting 400?**
Read the response body — a good API tells you exactly which field is wrong. Also verify `Content-Type: application/json` is set in your headers.

**Getting 500?**
The request is fine — the server crashed processing it. Check your backend logs (terminal output, Sentry, CloudWatch, etc.).

---

## 7. Best Practices

- **Use Collections** to group requests by resource (e.g., Users, Products, Orders)
- **Use Environments** for variables like `{{base_url}}` and `{{token}}` — swap dev/staging/prod in one click
- **Always test the unhappy path**: missing fields, wrong IDs, expired tokens, duplicate records
- **Write test scripts** in the Tests tab to auto-assert responses:

```javascript
pm.test("Status is 201", () => {
  pm.expect(pm.response.code).to.equal(201);
});

pm.test("Response has id", () => {
  const body = pm.response.json();
  pm.expect(body).to.have.property("id");
});
```

- **Save example responses** — teammates can use them to mock the API without a running server

---

## Practice API

Use **[reqres.in](https://reqres.in)** — a free hosted mock API that accepts real GET / POST / DELETE calls with no auth required. Perfect for drilling every scenario above.

---

*Guide covers: Postman basics · Request anatomy · Auth · POST/DELETE scenarios · Status codes · Debugging · Best practices*