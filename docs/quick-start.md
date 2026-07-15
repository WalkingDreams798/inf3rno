# Quick Start Guide

## Basic Usage

### SSH Brute-Force

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt
```

### FTP Brute-Force

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ftp -u root -w wordlist.txt
```

### HTTP Brute-Force

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --http -u admin -w wordlist.txt
```

### Auto-Detect Service

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --auto -u admin -w wordlist.txt
```

## Common Options

### Multi-User Attack

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -U users.txt -w passwords.txt
```

### With Delay

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --delay 0.5
```

### With Rate Limit Detection

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --rate-limit
```

### With Proxy

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --proxy socks5://127.0.0.1:9050
```

### Export Results

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --export all
```

## Password Generation

### Smart Wordlist

```bash
python3 inf3rno/cli.py -t example.com -u admin --smart --save-gen smart.txt
```

### Mask-Based Generation

```bash
python3 inf3rno/cli.py --gen-mask "?l?l?l?d?d" --save-gen masked.txt
```

### Rule-Based Generation

```bash
echo -e "password\nadmin\nletmein" > words.txt
python3 inf3rno/cli.py --gen-rule --gen-rule-input words.txt --save-gen ruled.txt
```

## Advanced Usage

### Resume Attack

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --resume
```

### Verbose Output

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt -v
```

### Multiple Threads

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt -T 10
```

## Running in Background

### Using nohup

```bash
nohup python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt > output.log 2>&1 &
```

### Using screen

```bash
screen -S inf3rno
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt
# Press Ctrl+A, D to detach
screen -r inf3rno  # To reattach
```

## Using Docker

```bash
# Build
docker build -t inf3rno .

# Run
docker run --rm inf3rno --ssh -t 192.168.1.1 -u admin -w wordlist.txt

# With volume mount for wordlists
docker run --rm -v $(pwd)/wordlists:/app/wordlists inf3rno --ssh -t 192.168.1.1 -u admin -w /app/wordlist.txt
```

## API Usage

### Start API Server

```bash
python3 inf3rno/cli.py --api --api-port 8000
```

### Create Attack via API

```bash
curl -X POST http://localhost:8000/api/attacks \
  -H "Content-Type: application/json" \
  -d '{"target":"192.168.1.1","service":"ssh","username":"admin","wordlist":"wordlist.txt"}'
```

### Check Attack Status

```bash
curl http://localhost:8000/api/attacks
```

## TUI Dashboard

```bash
python3 inf3rno/cli.py --tui
```

The TUI provides an interactive menu for managing attacks without command-line arguments.
