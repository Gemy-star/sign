# Frontend API Integration Guide

This guide explains how to connect your frontend to the backend API for the motivational message platform. It covers authentication, data fetching, error handling, localization, and best practices for a seamless user experience.

---

## 1. Base URL
- **Production:** `https://api.yourapp.com/v1`
- **Staging:** `https://staging-api.yourapp.com/v1`

All API requests should use HTTPS.

---

## 2. Authentication
- All authenticated requests must include:
  ```http
  Authorization: Bearer {access_token}
  ```
- Store tokens securely (e.g., HttpOnly cookies or secure storage).
- Handle token expiry and refresh using `/auth/refresh`.

---

## 3. API Request Patterns
- Use `fetch` or your preferred HTTP client (e.g., axios) for requests.
- Always check for `success: true` in responses.
- Handle errors using the `error` object in the response.

**Example:**
```js
const res = await fetch('https://api.yourapp.com/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const data = await res.json();
if (data.success) {
  // Save tokens, update UI
} else {
  alert(data.error.message);
}
```

---

## 4. Common Flows

### Authentication
- **Login:** `POST /auth/login`
- **Register:** `POST /auth/register`
- **Refresh Token:** `POST /auth/refresh`
- **Logout:** `POST /auth/logout`

### Onboarding
- **Get Topics:** `GET /topics`
- **Select Topics:** `POST /user/topics` (min 3 topics)

### Subscription
- **Get Packages:** `GET /packages`
- **Subscribe:** `POST /subscriptions`
- **Get Active Subscription:** `GET /subscriptions/active`
- **Cancel Subscription:** `DELETE /subscriptions/{id}`

### Dashboard & Messages
- **Dashboard:** `GET /dashboard`
- **All Messages:** `GET /messages` (with filters)
- **Message Detail:** `GET /messages/{id}`
- **Favorite Message:** `POST /messages/{id}/favorite`
- **Rate Message:** `POST /messages/{id}/rate`

### Goals & Motivation
- **Daily Quote:** `GET /motivation/daily`
- **Get Categories:** `GET /scopes`
- **Get Goals:** `GET /goals`
- **Create Goal:** `POST /goals`
- **Update Goal Progress:** `PATCH /goals/{id}/progress`

### Notifications
- **Get Notifications:** `GET /notifications`
- **Mark as Read:** `PATCH /notifications/{id}/read`
- **Mark All as Read:** `POST /notifications/mark-all-read`
- **Preferences:** `PUT /notifications/preferences`

### User Profile
- **Get Profile:** `GET /user/profile`
- **Update Profile:** `PUT /user/profile`
- **Change Password:** `POST /user/change-password`
- **Privacy Settings:** `GET/PUT /user/privacy-settings`

### Message Customization
- **Get Preferences:** `GET /user/message-preferences`
- **Update Preferences:** `PUT /user/message-preferences`

### History, Support, News
- **Message History:** `GET /messages/history`
- **FAQ:** `GET /support/faq`
- **Submit Ticket:** `POST /support/tickets`
- **News:** `GET /news`

---

## 5. Error Handling
- Always check for `success: false` and display `error.message` to the user.
- Handle common error codes (401, 403, 404, 422, 429, 500) with user-friendly messages.

---

## 6. Pagination
- Use `page` and `per_page` query parameters for lists.
- Use pagination metadata from the response to build paginators.

---

## 7. Localization
- Set `Accept-Language` header to `en` or `ar` as needed.
- Use both English and Arabic fields for UI text.
- Support RTL layout for Arabic.

---

## 8. Security & Best Practices
- Use HTTPS for all requests.
- Sanitize and validate all user input.
- Handle token expiry and refresh automatically.
- Respect rate limits and show appropriate UI feedback.
- Store sensitive data securely.

---

## 9. UI/UX Consistency
- Use the Inter font and provided color palette for all screens.
- Show loading indicators during API calls.
- Display error and success messages clearly.

---

## 10. Support
- For backend issues, contact: backend@yourapp.com
- See full backend docs: https://docs.yourapp.com

---

**Version:** 1.0.0
**Last Updated:** February 1, 2026
