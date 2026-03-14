# API Endpoints Reference

Base URL: `http://<host>/api`

---

## Table of Contents

- [Authentication](#authentication)
- [auth](#auth-endpoints)
  - [POST /auth/register/](#post-authregister)
  - [POST /auth/login/](#post-authlogin)
  - [GET /auth/profile/](#get-authprofile)
  - [PATCH /auth/profile/](#patch-authprofile)
  - [POST /auth/refresh/](#post-authrefresh)
- [scopes](#scopes-endpoints)
  - [GET /scopes/](#get-scopes)
  - [POST /scopes/](#post-scopes-check-access)
  - [GET /scopes/categories/](#get-scopescategories)
  - [GET /scopes/{id}/](#get-scopesid)
- [packages](#packages-endpoints)
  - [GET /packages/](#get-packages)
  - [GET /packages/featured/](#get-packagesfeatured)
  - [GET /packages/{id}/](#get-packagesid)
  - [GET /packages/{id}/comparison/](#get-packagesidcomparison)
- [subscriptions](#subscriptions-endpoints)
  - [GET /subscriptions/](#get-subscriptions)
  - [POST /subscriptions/](#post-subscriptions)
  - [GET /subscriptions/active/](#get-subscriptionsactive)
  - [GET /subscriptions/{id}/](#get-subscriptionsid)
  - [PUT /subscriptions/{id}/](#put-subscriptionsid)
  - [PATCH /subscriptions/{id}/](#patch-subscriptionsid)
  - [DELETE /subscriptions/{id}/](#delete-subscriptionsid)
  - [POST /subscriptions/{id}/cancel/](#post-subscriptionsidcancel)
  - [PATCH /subscriptions/{id}/update_scopes/](#patch-subscriptionsidupdatescopes)
- [goals](#goals-endpoints)
  - [GET /goals/](#get-goals)
  - [POST /goals/](#post-goals)
  - [GET /goals/active/](#get-goalsactive)
  - [GET /goals/{id}/](#get-goalsid)
  - [PUT /goals/{id}/](#put-goalsid)
  - [PATCH /goals/{id}/](#patch-goalsid)
  - [DELETE /goals/{id}/](#delete-goalsid)
  - [POST /goals/{id}/complete/](#post-goalsidcomplete)
  - [PATCH /goals/{id}/update_progress/](#patch-goalsidupdateprogress)
- [messages](#messages-endpoints)
  - [GET /messages/](#get-messages)
  - [POST /messages/](#post-messages)
  - [GET /messages/daily/](#get-messagesdaily)
  - [GET /messages/favorites/](#get-messagesfavorites)
  - [GET /messages/{id}/](#get-messagesid)
  - [PUT /messages/{id}/](#put-messagesid)
  - [PATCH /messages/{id}/](#patch-messagesid)
  - [DELETE /messages/{id}/](#delete-messagesid)
  - [POST /messages/{id}/mark_read/](#post-messagesidmark_read)
  - [POST /messages/{id}/rate/](#post-messagesidrate)
  - [POST /messages/{id}/toggle_favorite/](#post-messagesidtoggle_favorite)
- [payments](#payments-endpoints)
  - [GET /payments/verify/{charge_id}/](#get-paymentsverifycharge_id)
  - [POST /payments/webhook/](#post-paymentswebhook)
- [admin](#admin-endpoints)
  - [GET /admin/users/](#get-adminusers)
  - [POST /admin/users/](#post-adminusers)
  - [POST /admin/trials/](#post-admintrials)
- [features](#features-endpoints)
  - [GET /features/test/](#get-featurestest)
  - [POST /features/test/](#post-featurestest)
  - [PATCH /features/test/](#patch-featurestest)
  - [DELETE /features/test/](#delete-featurestest)

---

## Authentication

Protected endpoints require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained from `/api/auth/login/` or `/api/auth/register/`. Access tokens expire after 7 days. Use `/api/auth/refresh/` to renew them.

---

## auth Endpoints

### POST /auth/register/

Register a new user account. Automatically starts a 7-day free trial for `normal` and `subscriber` roles when `start_trial` is `true`.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "normal",
  "mobile_phone": "+1234567890",
  "country": "US",
  "date_of_birth": "1990-01-15",
  "start_trial": true
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `username` | string | Yes | Unique username |
| `email` | string | Yes | Unique email address |
| `password` | string | Yes | Minimum 8 characters |
| `password_confirm` | string | Yes | Must match `password` |
| `first_name` | string | No | — |
| `last_name` | string | No | — |
| `role` | string | No | `normal` \| `subscriber` \| `admin` — default: `normal` |
| `mobile_phone` | string | No | — |
| `country` | string | No | ISO 3166-1 alpha-2 country code (e.g. `US`, `EG`) |
| `date_of_birth` | string | No | Format: `YYYY-MM-DD` |
| `start_trial` | boolean | No | Default: `true` |

**Response 201:**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": "normal",
    "role_display": "Normal User",
    "mobile_phone": "+1234567890",
    "country": "US",
    "date_of_birth": "1990-01-15",
    "is_phone_verified": false,
    "has_active_trial": true,
    "trial_remaining_days": 7,
    "date_joined": "2026-03-14T10:00:00Z"
  },
  "tokens": {
    "refresh": "<refresh_token>",
    "access": "<access_token>"
  }
}
```

---

### POST /auth/login/

Authenticate a user and receive JWT tokens.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `username` | string | Yes | Username or email address |
| `password` | string | Yes | — |

**Response 200:**
```json
{
  "message": "Login successful",
  "token": {
    "refresh": "<refresh_token>",
    "access": "<access_token>",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "role": "normal",
      "scopes": ["basic_profile"],
      "permissions": ["view_profile"],
      "has_active_trial": true,
      "trial_remaining_days": 5,
      "is_verified": false
    }
  },
  "user_info": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "normal",
    "full_name": "John Doe",
    "has_active_trial": true,
    "trial_remaining_days": 5,
    "scopes": ["basic_profile"],
    "permissions": ["view_profile"]
  }
}
```

---

### GET /auth/profile/

Retrieve the authenticated user's profile.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "normal",
  "role_display": "Normal User",
  "mobile_phone": "+1234567890",
  "country": "US",
  "date_of_birth": "1990-01-15",
  "is_phone_verified": false,
  "trial_started_at": "2026-03-14T10:00:00Z",
  "trial_expires_at": "2026-03-21T10:00:00Z",
  "has_used_trial": true,
  "has_active_trial": true,
  "trial_remaining_days": 5,
  "date_joined": "2026-03-14T10:00:00Z"
}
```

---

### PATCH /auth/profile/

Partially update the authenticated user's profile.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "username": "new_username",
  "email": "newemail@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "mobile_phone": "+9876543210",
  "country": "GB",
  "date_of_birth": "1992-06-20"
}
```

**Response 200:** Updated user object (same shape as GET /auth/profile/)

---

### POST /auth/refresh/

Obtain a new access token using a valid refresh token.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response 200:**
```json
{
  "access": "<new_access_token>"
}
```

---

## scopes Endpoints

### GET /scopes/

List all active scopes. Optionally filter by category.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:**

| Parameter | Type | Notes |
|---|---|---|
| `category` | string | Filter by category: `mental` \| `physical` \| `career` \| `financial` \| `relationships` \| `spiritual` \| `creativity` \| `lifestyle` |

**Example:**
```
GET /api/scopes/?category=mental
```

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Mindfulness",
    "category": "mental",
    "category_display": "Mental",
    "description": "Focus on mindfulness practices",
    "icon": "brain",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
]
```

---

### POST /scopes/ (Check Access)

Check whether the authenticated user has access to specific scopes, permissions, or features.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "scopes": ["subscriber"],
  "permissions": ["create_goals"],
  "feature": "custom_goals"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `scopes` | string[] | No | Scopes to check |
| `permissions` | string[] | No | Permissions to check |
| `feature` | string | No | Feature name to check |

**Response 200:** User's current scopes and permissions info.

---

### GET /scopes/categories/

Retrieve all available scope category options.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Response 200:**
```json
[
  { "value": "mental", "label": "Mental" },
  { "value": "physical", "label": "Physical" },
  { "value": "career", "label": "Career" },
  { "value": "financial", "label": "Financial" },
  { "value": "relationships", "label": "Relationships" },
  { "value": "spiritual", "label": "Spiritual" },
  { "value": "creativity", "label": "Creativity" },
  { "value": "lifestyle", "label": "Lifestyle" }
]
```

---

### GET /scopes/{id}/

Retrieve a single scope by ID.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Response 200:**
```json
{
  "id": 1,
  "name": "Mindfulness",
  "category": "mental",
  "category_display": "Mental",
  "description": "Focus on mindfulness practices",
  "icon": "brain",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

---

## packages Endpoints

### GET /packages/

List all active packages. Optionally filter to featured only.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:**

| Parameter | Type | Notes |
|---|---|---|
| `featured` | boolean | Pass `true` to return only featured packages |

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Starter",
    "description": "Perfect for beginners",
    "price": "9.99",
    "duration": "monthly",
    "duration_display": "Monthly",
    "duration_days": 30,
    "max_scopes": 3,
    "messages_per_day": 1,
    "custom_goals_enabled": false,
    "priority_support": false,
    "is_active": true,
    "is_featured": true,
    "display_order": 1,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z"
  }
]
```

---

### GET /packages/featured/

List featured packages only.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Response 200:** Same array structure as GET /packages/

---

### GET /packages/{id}/

Retrieve a single package by ID.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Response 200:** Single package object (same shape as list items above)

---

### GET /packages/{id}/comparison/

Retrieve a comparison view of a selected package against all available packages.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Response 200:**
```json
{
  "selected_package": { ...package object },
  "all_packages": [ ...array of package objects ]
}
```

---

## subscriptions Endpoints

### GET /subscriptions/

List all subscriptions belonging to the authenticated user.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "user": 1,
    "user_email": "john@example.com",
    "package": 1,
    "package_name": "Starter",
    "status": "active",
    "status_display": "Active",
    "is_active_status": true,
    "start_date": "2026-03-01T00:00:00Z",
    "end_date": "2026-04-01T00:00:00Z",
    "amount_paid": "9.99",
    "auto_renew": true,
    "created_at": "2026-03-01T00:00:00Z"
  }
]
```

---

### POST /subscriptions/

Create a new subscription and initiate a payment via Tap Payment.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "package_id": 1,
  "selected_scope_ids": [1, 2, 3],
  "customer_email": "john@example.com",
  "customer_phone": "+1234567890",
  "redirect_url": "https://yourapp.com/payment/success",
  "post_url": "https://yourapp.com/api/payments/webhook/"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `package_id` | integer | Yes | ID of the package to subscribe to |
| `selected_scope_ids` | integer[] | Yes | IDs of chosen scopes (max determined by package) |
| `customer_email` | string | No | Defaults to user's email |
| `customer_phone` | string | No | — |
| `redirect_url` | string | No | URL to redirect after payment |
| `post_url` | string | No | Webhook URL for payment callbacks |

**Response 201:**
```json
{
  "subscription_id": 1,
  "payment_url": "https://tap.company/payment/...",
  "charge_id": "ch_xxxxxx",
  "status": "payment_initiated"
}
```

---

### GET /subscriptions/active/

Retrieve the currently active subscription for the authenticated user.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Full subscription detail object (see GET /subscriptions/{id}/)

**Response 404:** If no active subscription exists.

---

### GET /subscriptions/{id}/

Retrieve full details of a specific subscription.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "user": { ...user object },
  "user_email": "john@example.com",
  "package": { ...package object },
  "package_name": "Starter",
  "selected_scopes": [ ...scope objects ],
  "status": "active",
  "status_display": "Active",
  "is_active_status": true,
  "start_date": "2026-03-01T00:00:00Z",
  "end_date": "2026-04-01T00:00:00Z",
  "payment_id": "ch_xxxxxx",
  "payment_method": "VISA",
  "amount_paid": "9.99",
  "auto_renew": true,
  "cancelled_at": null,
  "created_at": "2026-03-01T00:00:00Z"
}
```

---

### PUT /subscriptions/{id}/

Full update of a specific subscription.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** Full subscription fields.

**Response 200:** Updated subscription detail object.

---

### PATCH /subscriptions/{id}/

Partial update of a specific subscription.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (any subset of fields):
```json
{
  "auto_renew": false
}
```

**Response 200:** Updated subscription detail object.

---

### DELETE /subscriptions/{id}/

Delete a specific subscription record.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 204:** No content.

---

### POST /subscriptions/{id}/cancel/

Cancel an active subscription.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**No request body required.**

**Response 200:**
```json
{
  "message": "Subscription cancelled successfully"
}
```

---

### PATCH /subscriptions/{id}/update_scopes/

Update the selected scopes for an active subscription.

**Permission:** Authenticated (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "scope_ids": [1, 2]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `scope_ids` | integer[] | Yes | New list of scope IDs (replaces existing) |

**Response 200:** Updated subscription detail object.

---

## goals Endpoints

> **Requirement:** User must have an active, non-expired subscription.

### GET /goals/

List all goals for the authenticated user.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "user": 1,
    "subscription": 1,
    "scope": 1,
    "scope_name": "Mindfulness",
    "title": "Meditate daily",
    "description": "Spend 10 minutes meditating each morning",
    "target_date": "2026-06-01",
    "status": "active",
    "status_display": "Active",
    "progress_percentage": 30,
    "created_at": "2026-03-01T00:00:00Z",
    "updated_at": "2026-03-14T00:00:00Z",
    "completed_at": null
  }
]
```

---

### POST /goals/

Create a new goal.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "subscription": 1,
  "scope": 1,
  "title": "Meditate daily",
  "description": "Spend 10 minutes meditating each morning",
  "target_date": "2026-06-01"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `subscription` | integer | Yes | ID of the active subscription |
| `scope` | integer | No | ID of the related scope |
| `title` | string | Yes | Max 255 characters |
| `description` | string | No | — |
| `target_date` | string | No | Format: `YYYY-MM-DD` |

**Response 201:** Created goal object.

---

### GET /goals/active/

List only active (non-completed) goals for the authenticated user.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Array of goal objects with `status = "active"`.

---

### GET /goals/{id}/

Retrieve a specific goal.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Single goal object.

---

### PUT /goals/{id}/

Full update of a goal.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "subscription": 1,
  "scope": 1,
  "title": "Meditate daily",
  "description": "Updated description",
  "target_date": "2026-07-01",
  "status": "active",
  "progress_percentage": 50
}
```

**Response 200:** Updated goal object.

---

### PATCH /goals/{id}/

Partial update of a goal.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (any subset of writable fields):
```json
{
  "title": "Updated goal title"
}
```

**Response 200:** Updated goal object.

---

### DELETE /goals/{id}/

Delete a goal.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 204:** No content.

---

### POST /goals/{id}/complete/

Mark a goal as completed. Sets `progress_percentage` to 100 and `status` to `completed`.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**No request body required.**

**Response 200:** Updated goal object with `status: "completed"` and `progress_percentage: 100`.

---

### PATCH /goals/{id}/update_progress/

Update the progress percentage of a goal.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "progress_percentage": 75
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `progress_percentage` | integer | Yes | Value between `0` and `100` |

**Response 200:** Updated goal object.

---

## messages Endpoints

> **Requirement:** User must have an active, non-expired subscription.

### GET /messages/

List all AI messages for the authenticated user.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Notes |
|---|---|---|
| `is_read` | boolean | Filter by read status: `true` or `false` |
| `is_favorited` | boolean | Filter by favorite status: `true` or `false` |
| `message_type` | string | `daily` \| `goal_specific` \| `scope_based` \| `custom` |

**Example:**
```
GET /api/messages/?is_read=false&message_type=daily
```

**Response 200:**
```json
[
  {
    "id": 1,
    "user": 1,
    "subscription": 1,
    "scope": 1,
    "scope_name": "Mindfulness",
    "goal": null,
    "goal_title": null,
    "message_type": "daily",
    "message_type_display": "Daily",
    "prompt_used": "Generate a daily mindfulness tip...",
    "content": "Take a moment to breathe deeply and...",
    "is_read": false,
    "is_favorited": false,
    "user_rating": null,
    "ai_model": "gpt-3.5-turbo",
    "tokens_used": 120,
    "generation_time": 1.23,
    "created_at": "2026-03-14T08:00:00Z"
  }
]
```

---

### POST /messages/

Generate a new AI message.

**Permission:** Authenticated + Active Subscription

Returns HTTP 429 if the daily message limit for the subscription's package is reached.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "scope_id": 1,
  "goal_id": 1,
  "message_type": "goal_specific",
  "custom_prompt": "Give me advice on staying consistent"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `scope_id` | integer | No | ID of the related scope |
| `goal_id` | integer | No | ID of the related goal |
| `message_type` | string | Yes | `daily` \| `goal_specific` \| `scope_based` \| `custom` |
| `custom_prompt` | string | No | Required when `message_type` is `custom` |

**Response 201:** Created message object.

**Response 429:**
```json
{
  "detail": "Daily message limit reached."
}
```

---

### GET /messages/daily/

Retrieve today's daily message. Auto-generates one if it does not exist yet.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Single message object with `message_type: "daily"`.

---

### GET /messages/favorites/

List all favorited messages for the authenticated user.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Array of message objects where `is_favorited: true`.

---

### GET /messages/{id}/

Retrieve a specific message.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:** Single message object.

---

### PUT /messages/{id}/

Full update of a message.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response 200:** Updated message object.

---

### PATCH /messages/{id}/

Partial update of a message.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body** (any subset of writable fields):
```json
{
  "is_favorited": true
}
```

**Response 200:** Updated message object.

---

### DELETE /messages/{id}/

Delete a message.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 204:** No content.

---

### POST /messages/{id}/mark_read/

Mark a message as read.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**No request body required.**

**Response 200:** Updated message object with `is_read: true`.

---

### POST /messages/{id}/rate/

Rate a message (1–5 stars).

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "rating": 4
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `rating` | integer | Yes | Value between `1` and `5` |

**Response 200:** Updated message object with `user_rating` set.

---

### POST /messages/{id}/toggle_favorite/

Toggle the favorite status of a message.

**Permission:** Authenticated + Active Subscription (owner only)

**Headers:**
```
Authorization: Bearer <access_token>
```

**No request body required.**

**Response 200:** Updated message object with toggled `is_favorited` value.

---

## payments Endpoints

### GET /payments/verify/{charge_id}/

Verify the status of a payment by its Tap Payment charge ID.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**URL Parameter:**

| Parameter | Type | Notes |
|---|---|---|
| `charge_id` | string | The Tap Payment charge ID (e.g. `ch_xxxxxx`) |

**Response 200:**
```json
{
  "charge_id": "ch_xxxxxx",
  "status": "CAPTURED",
  "details": { ...full Tap Payment charge object }
}
```

---

### POST /payments/webhook/

Receive payment status callbacks from the Tap Payment gateway. This endpoint is called by Tap, not by your app.

**Permission:** Public (no token required)

**Headers:**
```
Content-Type: application/json
```

**Request Body:** Tap Payment webhook payload (sent by Tap).

**Response 200:**
```json
{
  "status": "success"
}
```

---

## admin Endpoints

> **Requirement:** Authenticated user must have `admin` role with the `admin:user_management` scope or the relevant admin permission.

### GET /admin/users/

List all registered users.

**Permission:** Authenticated + `admin:user_management` scope

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "normal",
    "role_display": "Normal User",
    "is_active": true,
    "date_joined": "2026-03-01T00:00:00Z",
    "has_active_trial": true,
    "trial_remaining_days": 5,
    "active_subscription_count": 1
  }
]
```

---

### POST /admin/users/

Create a new admin user.

**Permission:** Authenticated + `create_users` permission

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** Same fields as [POST /auth/register/](#post-authregister). The `role` field is forced to `admin` regardless of the value provided.

**Response 201:** Created user object.

---

### POST /admin/trials/

Manage a user's free trial (start, extend, or cancel).

**Permission:** Authenticated + `manage_trials` permission

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": 1,
  "action": "extend",
  "days": 7
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `user_id` | integer | Yes | ID of the target user |
| `action` | string | Yes | `start` \| `extend` \| `cancel` |
| `days` | integer | Conditional | Required only when `action` is `extend` |

**Response 200:**
```json
{
  "message": "Trial extended successfully.",
  "user": { ...user object }
}
```

---

## features Endpoints

Developer/testing endpoints to verify feature access based on the user's current role and subscription state.

### GET /features/test/

Test access to the `basic_profile` feature. Available to all authenticated users.

**Permission:** Authenticated

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "message": "basic_profile feature accessible"
}
```

---

### POST /features/test/

Test access to the `trial_features` feature. Requires an active trial.

**Permission:** Authenticated + Active Trial

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "message": "trial_features feature accessible"
}
```

---

### PATCH /features/test/

Test access to the `subscriber_features` feature. Requires an active subscription.

**Permission:** Authenticated + Active Subscription

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "message": "subscriber_features feature accessible"
}
```

---

### DELETE /features/test/

Test access to the `custom_goals` feature. Requires an active subscription with custom goals enabled.

**Permission:** Authenticated + Active Subscription + `custom_goals_enabled`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "message": "custom_goals feature accessible"
}
```

---

## Common Error Responses

| Status | Meaning |
|---|---|
| `400` | Bad Request — validation errors in the request body |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient permissions or scope |
| `404` | Not Found — resource does not exist |
| `429` | Too Many Requests — daily message limit reached |
| `500` | Internal Server Error |

**Example 401 response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Example 400 response:**
```json
{
  "field_name": ["This field is required."]
}
```
