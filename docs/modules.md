# Supported Modules

Inf3rno supports multiple protocols for brute-force attacks.

## SSH (Secure Shell)

**Port:** 22
**Module:** `--ssh`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u root -w wordlist.txt
```

**Features:**
- Key-based authentication detection
- Banner grabbing
- Proxy support via SOCKS/HTTP

## FTP (File Transfer Protocol)

**Port:** 21
**Module:** `--ftp`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ftp -u anonymous -w wordlist.txt
```

**Features:**
- Anonymous login detection
- Passive/Active mode support
- Proxy support

## HTTP (Hypertext Transfer Protocol)

**Port:** 80/443
**Module:** `--http`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --http -u admin -w wordlist.txt
```

**Features:**
- Basic authentication
- Form-based authentication
- Custom login URL
- Custom fail string detection

**Options:**
- `--login-url`: URL for form-based auth
- `--fail-string`: String to detect failed login

## MySQL

**Port:** 3306
**Module:** `--mysql`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --mysql -u root -w wordlist.txt
```

**Features:**
- Native MySQL authentication
- Connection timeout handling

## SMTP (Simple Mail Transfer Protocol)

**Port:** 587/465/25
**Module:** `--smtp`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --smtp -u user@example.com -w wordlist.txt
```

**Features:**
- STARTTLS support
- SSL/TLS support
- Plain SMTP support

## Redis

**Port:** 6379
**Module:** `--redis`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --redis -w wordlist.txt
```

**Features:**
- AUTH command support
- No-auth detection
- RESP protocol handling

## PostgreSQL

**Port:** 5432
**Module:** `--postgresql`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --postgresql -u postgres -w wordlist.txt
```

**Features:**
- Native PostgreSQL authentication
- md5/scram-sha-256 support

## Telnet

**Port:** 23
**Module:** `--telnet`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --telnet -u admin -w wordlist.txt
```

**Features:**
- Login/Password prompt detection
- Command execution verification
- Banner grabbing

## RDP (Remote Desktop Protocol)

**Port:** 3389
**Module:** `--rdp`

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --rdp -u Administrator -w wordlist.txt
```

**Features:**
- NLA (Network Level Authentication) detection
- Connection verification
- Banner grabbing

**Note:** RDP brute-force is limited due to protocol complexity. Current implementation focuses on connection verification.

## Auto-Detection

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --auto -u admin -w wordlist.txt
```

**Features:**
- Port scanning
- Service fingerprinting
- Automatic module selection

## Custom Ports

All modules support custom ports:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -p 2222 -u admin -w wordlist.txt
```
