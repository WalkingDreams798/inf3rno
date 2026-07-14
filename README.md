# Inf3rno 🔥

A powerful brute-force tool for penetration testing.

## Features

- Multi-protocol support (SSH, FTP, HTTP)
- Multi-threaded for speed
- Custom wordlist support
- Password mask generator
- Resume capability
- Colored output with progress bar

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Basic SSH brute-force
python3 inf3rno.py -t 192.168.1.1 -u admin -w wordlist.txt

# FTP brute-force
python3 inf3rno.py -t 192.168.1.1 --ftp -u root -w passwords.txt

# HTTP form brute-force
python3 inf3rno.py -t target.com --http -U users.txt -w passwords.txt

# With password generator
python3 inf3rno.py -t 192.168.1.1 -u admin --gen-mask "?l?l?l?d?d"

# Auto-detect service
python3 inf3rno.py -t scanme.org --auto
```

## Arguments

| Argument | Description |
|----------|-------------|
| `-t, --target` | Target IP or hostname |
| `-u, --user` | Single username |
| `-U, --userlist` | File with usernames |
| `-w, --wordlist` | File with passwords |
| `-p, --port` | Target port (optional, auto-detect) |
| `-T, --threads` | Number of threads (default: 5) |
| `-o, --output` | Output file |
| `--ssh` | SSH mode |
| `--ftp` | FTP mode |
| `--http` | HTTP mode |
| `--auto` | Auto-detect service |
| `--gen-mask` | Generate passwords with mask |
| `-v, --verbose` | Verbose output |

## Author

WalkingDreams798 

## Disclaimer

This tool is for educational and authorized penetration testing only. Use responsibly.
