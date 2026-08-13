# MentorAI API Reference

**Version:** 1.0.0  
**Last Updated:** June 2026  
**Status:** Production Ready

---

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Core Endpoints](#core-endpoints)
4. [Query Endpoints](#query-endpoints)
5. [User Endpoints](#user-endpoints)
6. [Analytics Endpoints](#analytics-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)

---

## Introduction

The MentorAI API provides programmatic access to the educational assistant platform. All API calls are local-first and do not require internet connectivity for core functionality.

### Base URL

```
http://localhost:3000/api/v1
```

### Authentication

All API requests require authentication via JWT token or local device ID.

---

## Authentication

### Local Device Authentication

```http
POST /auth/register-device
Content-Type: application/json

{
  "device_id": "unique-device-identifier",
  "device_name": "My Computer",
  "device_type": "windows|android|linux"
}
```

**Response:**

```json
{
  "status": "success",
  "device_id": "unique-device-identifier",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

### Using the Token

Include the token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Core Endpoints

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-10T23:45:00Z"
}
```

### System Information

```http
GET /system/info
```

**Response:**

```json
{
  "os": "Windows 11",
  "processor": "Intel Core i7",
  "memory": "16GB",
  "storage": "512GB SSD",
  "knowledge_base_size": "44KB",
  "total_topics": 35,
  "last_update": "2026-06-10T20:00:00Z"
}
```

---

## Query Endpoints

### Process Query

```http
POST /query/process
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "¿Qué es Python?",
  "language": "es",
  "context": "learning"
}
```

**Response:**

```json
{
  "status": "success",
  "query": "¿Qué es Python?",
  "matched_term": "python",
  "explanation": "Python es un lenguaje de programación versátil...",
  "steps": [
    "Paso 1: Instala Python desde python.org",
    "Paso 2: Verifica la instalación con python --version",
    "Paso 3: Crea tu primer script"
  ],
  "security_tips": [
    "Nunca ejecutes código de fuentes desconocidas",
    "Mantén Python actualizado"
  ],
  "related_topics": ["git", "docker", "programming"],
  "processing_time_ms": 45
}
```

### Semantic Search

```http
POST /query/semantic-search
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "¿Cómo protejo mi código?",
  "top_k": 5
}
```

**Response:**

```json
{
  "status": "success",
  "query": "¿Cómo protejo mi código?",
  "results": [
    {
      "term": "git",
      "similarity": 0.85,
      "explanation": "Git es un sistema de control de versiones..."
    },
    {
      "term": "security",
      "similarity": 0.78,
      "explanation": "La seguridad es fundamental..."
    }
  ]
}
```

### Get Learning Path

```http
GET /query/learning-path?goal=programación
Authorization: Bearer {token}
```

**Response:**

```json
{
  "status": "success",
  "goal": "programación",
  "recommended_path": [
    "python",
    "git",
    "docker",
    "testing",
    "deployment"
  ],
  "estimated_duration_hours": 40
}
```

---

## User Endpoints

### Get User Profile

```http
GET /user/profile
Authorization: Bearer {token}
```

**Response:**

```json
{
  "status": "success",
  "user_id": "user_123",
  "level": 2,
  "points": 250,
  "achievements": 1,
  "topics_completed": 5,
  "learning_streak": 5,
  "joined_at": "2026-06-01T10:00:00Z"
}
```

### Update User Progress

```http
POST /user/progress
Content-Type: application/json
Authorization: Bearer {token}

{
  "topic": "python",
  "status": "completed"
}
```

**Response:**

```json
{
  "status": "success",
  "topic": "python",
  "points_earned": 50,
  "total_points": 300,
  "new_level": 3,
  "level_up": true
}
```

### Get Achievements

```http
GET /user/achievements
Authorization: Bearer {token}
```

**Response:**

```json
{
  "status": "success",
  "achievements": [
    {
      "id": "first_topic",
      "title": "Primer paso",
      "description": "Completa tu primer tema",
      "unlocked": true,
      "unlocked_at": "2026-06-05T15:30:00Z"
    }
  ],
  "total_achievements": 8,
  "unlocked_count": 1
}
```

---

## Analytics Endpoints

### Get Usage Statistics

```http
GET /analytics/usage
Authorization: Bearer {token}
```

**Response:**

```json
{
  "status": "success",
  "total_queries": 150,
  "queries_today": 12,
  "average_response_time_ms": 45,
  "topics_explored": 25,
  "most_searched": ["python", "git", "security"],
  "learning_time_hours": 12.5
}
```

### Get Performance Metrics

```http
GET /analytics/performance
Authorization: Bearer {token}
```

**Response:**

```json
{
  "status": "success",
  "api_response_time_p50": 30,
  "api_response_time_p95": 120,
  "api_response_time_p99": 250,
  "cache_hit_rate": 0.85,
  "error_rate": 0.001,
  "uptime_percentage": 99.99
}
```

---

## Error Handling

### Error Response Format

```json
{
  "status": "error",
  "error_code": "INVALID_QUERY",
  "message": "La consulta no es válida",
  "details": {
    "query": "invalid input",
    "reason": "Query contains invalid characters"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_QUERY` | 400 | Query format is invalid |
| `UNAUTHORIZED` | 401 | Authentication token is missing or invalid |
| `FORBIDDEN` | 403 | User does not have permission |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Standard Users:** 100 requests per minute
- **Premium Users:** 1000 requests per minute
- **Burst Limit:** 50 requests per second

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1623350400
```

---

## Examples

### Example 1: Complete Learning Flow

```bash
# 1. Register device
curl -X POST http://localhost:3000/api/v1/auth/register-device \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "my-device-001",
    "device_name": "My Computer",
    "device_type": "windows"
  }'

# 2. Get learning path
curl -X GET "http://localhost:3000/api/v1/query/learning-path?goal=programación" \
  -H "Authorization: Bearer {token}"

# 3. Process first query
curl -X POST http://localhost:3000/api/v1/query/process \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "query": "¿Qué es Python?",
    "language": "es"
  }'

# 4. Update progress
curl -X POST http://localhost:3000/api/v1/user/progress \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "topic": "python",
    "status": "completed"
  }'

# 5. Get updated profile
curl -X GET http://localhost:3000/api/v1/user/profile \
  -H "Authorization: Bearer {token}"
```

### Example 2: Semantic Search

```bash
curl -X POST http://localhost:3000/api/v1/query/semantic-search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "query": "¿Cómo hago deploy de mi aplicación?",
    "top_k": 3
  }'
```

---

## SDK Examples

### Python SDK

```python
from mentorai import MentorAI

# Initialize client
client = MentorAI(device_id="my-device-001")

# Process query
result = client.query("¿Qué es Python?")
print(result.explanation)
print(result.steps)

# Get learning path
path = client.get_learning_path("programación")
print(path.recommended_topics)

# Update progress
client.complete_topic("python")

# Get profile
profile = client.get_profile()
print(f"Level: {profile.level}, Points: {profile.points}")
```

### JavaScript SDK

```javascript
const MentorAI = require('mentorai');

// Initialize client
const client = new MentorAI({ deviceId: 'my-device-001' });

// Process query
const result = await client.query('¿Qué es Python?');
console.log(result.explanation);
console.log(result.steps);

// Get learning path
const path = await client.getLearningPath('programación');
console.log(path.recommendedTopics);

// Update progress
await client.completeTopic('python');

// Get profile
const profile = await client.getProfile();
console.log(`Level: ${profile.level}, Points: ${profile.points}`);
```

---

## Changelog

### Version 1.0.0 (June 2026)

- Initial release
- Core query processing
- User progress tracking
- Analytics endpoints
- Semantic search
- Learning paths

---

## Support

For API support, visit: https://docs.mentorai.com/api

For bug reports: https://github.com/mentorai/mentorai/issues

---

**Last Updated:** June 2026  
**Status:** Production Ready ✅
