# REST API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production use, consider adding API key authentication.

## Endpoints

### Health Check

```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Create Attack

```
POST /api/attacks
```

**Request Body:**
```json
{
  "target": "192.168.1.1",
  "service": "ssh",
  "port": 22,
  "username": "admin",
  "wordlist": "wordlist.txt",
  "threads": 5,
  "delay": 0,
  "rate_limit": false,
  "proxy": null
}
```

**Response:**
```json
{
  "id": "abc12345",
  "target": "192.168.1.1",
  "service": "ssh",
  "port": 22,
  "status": "running",
  "created_at": "2024-01-01T00:00:00"
}
```

### List Attacks

```
GET /api/attacks
```

**Response:**
```json
[
  {
    "id": "abc12345",
    "target": "192.168.1.1",
    "service": "ssh",
    "port": 22,
    "status": "running",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Get Attack Details

```
GET /api/attacks/{attack_id}
```

**Response:**
```json
{
  "id": "abc12345",
  "target": "192.168.1.1",
  "service": "ssh",
  "port": 22,
  "username": "admin",
  "status": "completed",
  "attempts": 1000,
  "found": [
    ["admin", "password123"]
  ],
  "created_at": "2024-01-01T00:00:00"
}
```

### Delete Attack

```
DELETE /api/attacks/{attack_id}
```

**Response:**
```json
{
  "message": "Attack deleted"
}
```

### List Credentials

```
GET /api/credentials
```

**Response:**
```json
[
  {
    "username": "admin",
    "password": "password123",
    "service": "ssh",
    "target": "192.168.1.1"
  }
]
```

### Clear Credentials

```
DELETE /api/credentials
```

**Response:**
```json
{
  "message": "Credentials cleared"
}
```

### Generate Passwords

```
POST /api/generate
```

**Request Body:**
```json
{
  "target": "example.com",
  "username": "admin",
  "mode": "smart",
  "mask": null,
  "count": 1000,
  "rules": ["leet", "capitalize", "append_number"]
}
```

**Modes:**
- `smart`: Generate based on target info
- `mask`: Generate using mask pattern
- `random`: Generate random passwords

**Response:**
```json
{
  "count": 5000,
  "passwords": ["admin123", "Admin123", "4dm1n123", ...],
  "file_path": null
}
```

### Scan Target

```
GET /api/scan/{target}
```

**Response:**
```json
{
  "target": "192.168.1.1",
  "open_ports": [
    {"port": 22, "service": "SSH"},
    {"port": 80, "service": "HTTP"},
    {"port": 443, "service": "HTTPS"}
  ]
}
```

### Detect Service

```
GET /api/scan/{target}/detect?port=22
```

**Response:**
```json
{
  "target": "192.168.1.1",
  "port": 22,
  "service": "SSH"
}
```

### Export Results

```
GET /api/export/{format}
```

**Formats:** `json`, `csv`, `html`

**Response:**
```json
{
  "format": "json",
  "file": "output/export_20240101_120000.json",
  "count": 5
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Port 22 is closed or unreachable"
}
```

### 404 Not Found

```json
{
  "detail": "Attack not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Usage Examples

### cURL

**Create Attack:**
```bash
curl -X POST http://localhost:8000/api/attacks \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.1","service":"ssh","username":"admin","wordlist":"wordlist.txt"}'
```

**List Attacks:**
```bash
curl http://localhost:8000/api/attacks
```

**Generate Passwords:**
```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"target":"example.com","mode":"smart"}'
```

### Python

```python
import requests

# Create attack
response = requests.post("http://localhost:8000/api/attacks", json={
    "target": "192.168.1.1",
    "service": "ssh",
    "username": "admin",
    "wordlist": "wordlist.txt"
})

# List attacks
response = requests.get("http://localhost:8000/api/attacks")
attacks = response.json()

# Generate passwords
response = requests.post("http://localhost:8000/api/generate", json={
    "target": "example.com",
    "mode": "smart"
})
passwords = response.json()
```

### JavaScript

```javascript
// Create attack
const response = await fetch("http://localhost:8000/api/attacks", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    target: "192.168.1.1",
    service: "ssh",
    username: "admin",
    wordlist: "wordlist.txt"
  })
});

// List attacks
const attacks = await fetch("http://localhost:8000/api/attacks").json();
```
