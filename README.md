# Inf3rno 🔥

[![CI](https://github.com/WalkingDreams798/inf3rno/actions/workflows/ci.yml/badge.svg)](https://github.com/WalkingDreams798/inf3rno/actions/workflows/ci.yml)
[![Security](https://github.com/WalkingDreams798/inf3rno/actions/workflows/security.yml/badge.svg)](https://github.com/WalkingDreams798/inf3rno/actions/workflows/security.yml)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Multi-Protocol Brute-Force Tool for Penetration Testing**

A powerful, fast, and extensible brute-force tool supporting 12 protocols with TUI dashboard, REST API, and plugin system.

---

## Preview

### CLI Interface

```
    _____ _____ ____  __  __ ____  _     ___ _____ ____
   |_   _| ____|  _ \|  \/  |  _ \| |   |_ _|_   _/ ___|
     | | |  _| | |_) | |\/| | |_) | |    | |  | | \___ \
     | | | |___|  _ <| |  | |  __/| |___ | |  | |  ___) |
     |_| |_____|_| \_\_|  |_|_|   |_____|___| |_| |____/

    [ Multi-Protocol Brute-Force Tool ]

[*] Target: 192.168.1.1:22
[*] Username: admin
[*] Threads: 5
[*] Passwords loaded: 1000
[*] Starting brute-force...

Progress:  45%|███████████▌                 | 450/1000 [00:45<00:55, 10.0pwd/s]
```

### TUI Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    _____ _____ ____  __  __ ____  _     ___ _____ ____     │
│   |_   _| ____|  _ \|  \/  |  _ \| |   |_ _|_   _/ ___|   │
│     | | |  _| | |_) | |\/| | |_) | |    | |  | | \___ \   │
│     | | | |___|  _ <| |  | |  __/| |___ | |  | |  ___) |  │
│     |_| |_____|_| \_\_|  |_|_|   |_____|___| |_| |____/   │
│                                                             │
│    [ TUI Dashboard - Multi-Protocol Brute-Force Tool ]      │
│                                                             │
│  ┌─ Main Menu ─────────────────────────────────────────┐   │
│  │ No  │ Option              │ Description              │   │
│  ├─────┼─────────────────────┼──────────────────────────┤   │
│  │ 1   │ New Attack          │ Start a new brute-force  │   │
│  │ 2   │ View Attacks        │ List all attacks         │   │
│  │ 3   │ View Credentials    │ Show found credentials   │   │
│  │ 4   │ Generate Wordlist   │ Create smart wordlist    │   │
│  │ 5   │ Scan Ports          │ Scan common ports        │   │
│  │ 6   │ Settings            │ Configure settings       │   │
│  │ 0   │ Exit                │ Exit dashboard           │   │
│  └─────┴─────────────────────┴──────────────────────────┘   │
│                                                             │
│  Select option: 1                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### REST API

```bash
# Start API server
$ python3 inf3rno/cli.py --api

# Create attack via API
$ curl -X POST http://localhost:8000/api/attacks \
    -H "Content-Type: application/json" \
    -d '{"target":"192.168.1.1","service":"ssh","username":"admin","wordlist":"passwords.txt"}'

{
    "id": "abc12345",
    "target": "192.168.1.1",
    "service": "ssh",
    "port": 22,
    "status": "running",
    "created_at": "2024-01-15T10:30:00"
}
```

---

## Features

| Feature | Description |
|---------|-------------|
| **12 Protocols** | SSH, FTP, HTTP, MySQL, SMTP, Redis, PostgreSQL, Telnet, RDP, SMB, VNC, SNMP |
| **Multi-User** | Test multiple usernames with `-U users.txt` |
| **Smart Wordlist** | Generate wordlist from target info |
| **Password Generator** | Mask-based, rule-based, random generation |
| **Rate Limit Detection** | Auto-pause when rate limited |
| **Proxy Support** | SOCKS4/5, HTTP proxy |
| **Resume** | Continue interrupted attacks |
| **Export** | JSON, CSV, HTML reports |
| **TUI Dashboard** | Interactive terminal interface |
| **REST API** | HTTP API for integration |
| **Plugin System** | Extend with custom modules |
| **Docker** | Containerized deployment |

---

## Supported Protocols

| Protocol | Port | Module | Default Users |
|----------|------|--------|---------------|
| SSH | 22 | `--ssh` | root, admin, ubuntu |
| FTP | 21 | `--ftp` | anonymous, ftp, admin |
| HTTP | 80 | `--http` | admin, administrator |
| MySQL | 3306 | `--mysql` | root, admin, mysql |
| SMTP | 587 | `--smtp` | admin@, user@ |
| Redis | 6379 | `--redis` | default, admin |
| PostgreSQL | 5432 | `--postgresql` | postgres, admin |
| Telnet | 23 | `--telnet` | admin, root, user |
| RDP | 3389 | `--rdp` | Administrator |
| SMB | 445 | `--smb` | Administrator, admin |
| VNC | 5900 | `--vnc` | (password only) |
| SNMP | 161 | `--snmp` | public, private |

---

## Installation

### Method 1: Git Clone

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
pip install -r requirements.txt
```

### Method 2: Installer Script

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
chmod +x install.sh
./install.sh
```

### Method 3: Docker

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
docker build -t inf3rno .
docker run --rm inf3rno --help
```

### Method 4: pip install

```bash
git clone https://github.com/WalkingDreams798/inf3rno.git
cd inf3rno
pip install -e .
```

---

## Quick Start

### Basic Usage

```bash
# SSH brute-force
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt

# FTP brute-force
python3 inf3rno/cli.py -t 192.168.1.1 --ftp -u root -w passwords.txt

# Auto-detect service
python3 inf3rno/cli.py -t 192.168.1.1 --auto -u admin -w wordlist.txt
```

### Advanced Usage

```bash
# Multi-user with delay and rate limit
python3 inf3rno/cli.py -t 192.168.1.1 --ssh \
    -U users.txt \
    -w passwords.txt \
    --delay 0.5 \
    --rate-limit \
    --export all

# Smart wordlist generation
python3 inf3rno/cli.py -t example.com -u admin \
    --smart \
    --save-gen smart.txt

# Via Tor proxy
python3 inf3rno/cli.py -t 192.168.1.1 --ssh \
    -u admin \
    -w passwords.txt \
    --proxy socks5://127.0.0.1:9050
```

### TUI Dashboard

```bash
python3 inf3rno/cli.py --tui
```

### REST API

```bash
# Start API server
python3 inf3rno/cli.py --api --api-port 8000

# View API docs
open http://localhost:8000/docs
```

---

## Command Reference

| Flag | Description |
|------|-------------|
| `-t, --target` | Target IP or hostname |
| `-p, --port` | Target port |
| `-u, --user` | Single username |
| `-U, --userlist` | File with usernames |
| `-w, --wordlist` | File with passwords |
| `-T, --threads` | Number of threads (default: 5) |
| `--delay` | Delay between attempts (seconds) |
| `--proxy` | Proxy URL (socks5://host:port) |
| `--rate-limit` | Enable rate limit detection |
| `--export` | Export format (json/csv/html/all) |
| `--smart` | Smart wordlist generation |
| `--gen-mask` | Generate with mask pattern |
| `--resume` | Resume previous attack |
| `-v, --verbose` | Verbose output |
| `--list` | Scan common ports |

---

## Project Structure

```
inf3rno/
├── inf3rno/              # Main package
│   ├── __init__.py
│   ├── cli.py            # CLI entry point
│   ├── tui.py            # TUI dashboard
│   └── api.py            # REST API
├── core/                 # Core modules
│   ├── bruteforce.py     # Base class
│   ├── generator.py      # Password generator
│   ├── smart_wordlist.py # Smart wordlist
│   ├── reporter.py       # Report export
│   ├── validator.py      # Credential validator
│   ├── state.py          # Resume capability
│   ├── threader.py       # Thread pool
│   ├── plugin.py         # Plugin system
│   └── utils.py          # Utilities
├── modules/              # Brute-force modules
│   ├── ssh.py
│   ├── ftp.py
│   ├── http.py
│   ├── mysql.py
│   ├── smtp.py
│   ├── redis.py
│   ├── postgresql.py
│   ├── telnet.py
│   ├── rdp.py
│   ├── smb.py
│   ├── vnc.py
│   └── snmp.py
├── plugins/              # Custom plugins
├── wordlists/            # Wordlists
├── tests/                # Unit tests
├── docs/                 # Documentation
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

---

## Docker

```bash
# Build
docker build -t inf3rno .

# Run
docker run --rm inf3rno --ssh -t 192.168.1.1 -u admin -w wordlist.txt

# Docker Compose (with API)
docker-compose up -d inf3rno-api
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/docs` | Swagger documentation |
| POST | `/api/attacks` | Create attack |
| GET | `/api/attacks` | List attacks |
| GET | `/api/credentials` | List credentials |
| POST | `/api/generate` | Generate passwords |
| GET | `/api/scan/{target}` | Scan ports |
| GET | `/api/export/{format}` | Export results |

---

## Testing

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ -v --cov=inf3rno
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start](docs/quick-start.md)
- [Supported Modules](docs/modules.md)
- [Features](docs/features.md)
- [API Reference](docs/api-reference.md)
- [Plugin System](docs/plugin-system.md)

---

## Author

**WalkingDreams798**

---

## Disclaimer

This tool is for educational and authorized penetration testing only. Use responsibly and only on systems you have permission to test.

---

## License

MIT License - See [LICENSE](LICENSE) for details.
