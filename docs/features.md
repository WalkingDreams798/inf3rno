# Advanced Features

## Multi-User Attack

Test multiple usernames against the same target:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -U users.txt -w passwords.txt
```

**users.txt format:**
```
admin
root
user
test
```

## Delay/Throttle

Add delay between attempts to avoid detection:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --delay 0.5
```

**Options:**
- `--delay 0.5`: 500ms delay between attempts
- `--delay 1`: 1 second delay
- `--delay 2`: 2 seconds delay

## Rate Limit Detection

Automatically pause when rate limiting is detected:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --rate-limit
```

**Options:**
- `--rate-limit`: Enable rate limit detection
- `--rate-max-failures 10`: Max failures before pause (default: 10)
- `--rate-window 60`: Time window in seconds (default: 60)
- `--rate-pause-time 60`: Pause duration in seconds (default: 60)

## Proxy Support

Route attacks through SOCKS/HTTP proxy:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --proxy socks5://127.0.0.1:9050
```

**Supported proxies:**
- `socks5://host:port`
- `socks4://host:port`
- `http://host:port`

**Example with Tor:**
```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --proxy socks5://127.0.0.1:9050
```

## Resume Attack

Resume a previously interrupted attack:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --resume
```

## Export Results

Export found credentials to various formats:

```bash
# JSON format
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --export json

# CSV format
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --export csv

# HTML report
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --export html

# All formats
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt --export all
```

## Password Generation

### Smart Wordlist

Generate wordlist based on target information:

```bash
python3 inf3rno/cli.py -t example.com -u admin --smart --save-gen smart.txt
```

**Options:**
- `--smart`: Enable smart generation
- `--smart-rules leet,capitalize,append_number`: Custom rules
- `--smart-max-length 12`: Max password length

### Mask-Based Generation

Generate passwords using mask patterns:

```bash
python3 inf3rno/cli.py --gen-mask "?l?l?l?d?d" --save-gen masked.txt
```

**Mask characters:**
- `?l`: Lowercase letters
- `?u`: Uppercase letters
- `?d`: Digits
- `?s`: Special characters
- `?a`: All characters

### Rule-Based Generation

Apply rules to existing words:

```bash
echo -e "password\nadmin\nletmein" > words.txt
python3 inf3rno/cli.py --gen-rule --gen-rule-input words.txt --save-gen ruled.txt
```

**Available rules:**
- `leet`: Leet speak (a→4, e→3, i→1, o→0, s→5, t→7)
- `capitalize`: Capitalize first letter
- `append_number`: Append numbers (0-9, 123, !, @, #)
- `prepend_number`: Prepend numbers
- `duplicate`: Duplicate the word
- `reverse`: Reverse the word

## Verbose Output

Show detailed output during attack:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt -v
```

## Thread Configuration

Control number of concurrent threads:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --ssh -u admin -w wordlist.txt -T 10
```

**Default:** 5 threads
**Maximum:** 50 threads

## Port Scanning

Scan common ports on target:

```bash
python3 inf3rno/cli.py -t 192.168.1.1 --list
```

## State Management

View saved attack states:

```bash
python3 inf3rno/cli.py --list-states
```

## Combined Example

Full-featured attack with all options:

```bash
python3 inf3rno/cli.py \
  -t 192.168.1.1 \
  --ssh \
  -U users.txt \
  -w passwords.txt \
  -T 10 \
  --delay 0.5 \
  --rate-limit \
  --proxy socks5://127.0.0.1:9050 \
  --export all \
  -v
```
