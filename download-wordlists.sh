#!/bin/bash
#
# Inf3rno Wordlist Downloader
# Downloads common wordlists for brute-force testing
#

set -e

WORDLIST_DIR="wordlists"
TEMP_DIR="/tmp/wordlist_download"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[*] Inf3rno Wordlist Downloader${NC}"
echo ""

# Create directories
mkdir -p "$WORDLIST_DIR"
mkdir -p "$TEMP_DIR"

# Function to download with progress
download() {
    local url=$1
    local output=$2
    local name=$3

    echo -e "${YELLOW}[*] Downloading ${name}...${NC}"
    if wget -q --show-progress -O "$output" "$url" 2>/dev/null; then
        echo -e "${GREEN}[+] Downloaded: ${name}${NC}"
        return 0
    else
        echo -e "${RED}[-] Failed to download: ${name}${NC}"
        return 1
    fi
}

# Function to extract compressed files
extract() {
    local file=$1
    local output_dir=$2

    case "$file" in
        *.gz)
            gunzip -k "$file" 2>/dev/null || true
            ;;
        *.zip)
            unzip -o "$file" -d "$output_dir" 2>/dev/null || true
            ;;
        *.7z)
            7z x "$file" -o"$output_dir" 2>/dev/null || true
            ;;
    esac
}

# Download RockYou
echo ""
echo -e "${GREEN}=== Common Wordlists ===${NC}"
echo ""

if [ ! -f "$WORDLIST_DIR/rockyou.txt" ]; then
    download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt" \
        "$WORDLIST_DIR/rockyou.txt" "RockYou (top 1M)"
else
    echo -e "${GREEN}[+] RockYou already exists${NC}"
fi

# Download SecLists Common
echo ""
echo -e "${GREEN}=== SecLists Common ===${NC}"
echo ""

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Common-Credentials/10-million-password-list-top-10000.txt" \
    "$WORDLIST_DIR/common-passwords.txt" "Common Passwords (top 10K)"

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Common-Credentials/10k-most-common.txt" \
    "$WORDLIST_DIR/10k-common.txt" "10K Most Common"

# Download Usernames
echo ""
echo -e "${GREEN}=== Username Lists ===${NC}"
echo ""

download "https://github.com/danielmiessler/SecLists/raw/master/Usernames/top-usernames-shortlist.txt" \
    "$WORDLIST_DIR/common-users.txt" "Common Usernames"

download "https://github.com/danielmiessler/SecLists/raw/master/Usernames/xato-net-10-million-usernames.txt" \
    "$WORDLIST_DIR/xato-users.txt" "Xato 10M Usernames"

# Download Default Credentials
echo ""
echo -e "${GREEN}=== Default Credentials ===${NC}"
echo ""

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Default-Credentials/default-passwords.txt" \
    "$WORDLIST_DIR/default-credentials.txt" "Default Credentials"

# Download Weak Passwords
echo ""
echo -e "${GREEN}=== Weak Passwords ===${NC}"
echo ""

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/rockyou.txt.tar.gz" \
    "$TEMP_DIR/rockyou.tar.gz" "RockYou Full (compressed)"

if [ -f "$TEMP_DIR/rockyou.tar.gz" ]; then
    echo -e "${YELLOW}[*] Extracting rockyou.txt...${NC}"
    tar -xzf "$TEMP_DIR/rockyou.tar.gz" -C "$WORDLIST_DIR/" 2>/dev/null || true
fi

# Download Specialized Lists
echo ""
echo -e "${GREEN}=== Specialized Lists ===${NC}"
echo ""

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/ashley-madison.txt" \
    "$WORDLIST_DIR/ashley-madison.txt" "Ashley Madison"

download "https://github.com/danielmiessler/SecLists/raw/master/Passwords/Leaked-Databases/LinkedIn.txt" \
    "$WORDLIST_DIR/linkedin.txt" "LinkedIn"

# Generate custom wordlists
echo ""
echo -e "${GREEN}=== Generating Custom Wordlists ===${NC}"
echo ""

# Service-specific wordlists
cat > "$WORDLIST_DIR/ssh-default.txt" << 'EOF'
root
admin
user
test
guest
ubuntu
debian
centos
 fedora
root123
admin123
password
letmein
EOF

cat > "$WORDLIST_DIR/ftp-default.txt" << 'EOF'
anonymous
ftp
admin
root
user
test
guest
ftpuser
ftpadmin
EOF

cat > "$WORDLIST_DIR/mysql-default.txt" << 'EOF'
root
admin
mysql
test
user
dbadmin
EOF

cat > "$WORDLIST_DIR/postgres-default.txt" << 'EOF'
postgres
admin
root
user
test
pgsql
EOF

cat > "$WORDLIST_DIR/redis-default.txt" << 'EOF'
redis
admin
default
root
EOF

cat > "$WORDLIST_DIR/smb-default.txt" << 'EOF'
administrator
admin
root
guest
user
test
EOF

cat > "$WORDLIST_DIR/vnc-default.txt" << 'EOF'
password
admin
123456
1234
12345
123456789
test
guest
EOF

cat > "$WORDLIST_DIR/snmp-default.txt" << 'EOF'
public
private
community
manager
test
admin
snmp
EOF

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}[+] Download complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Wordlists saved to: ${WORDLIST_DIR}/${NC}"
echo ""
ls -lh "$WORDLIST_DIR/" | head -20
echo ""
echo -e "${YELLOW}Total wordlists: $(ls -1 "$WORDLIST_DIR/"*.txt 2>/dev/null | wc -l)${NC}"

# Cleanup
rm -rf "$TEMP_DIR"
