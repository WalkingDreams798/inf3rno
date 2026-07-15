#!/bin/bash
#
# Inf3rno Installer
# Multi-Protocol Brute-Force Tool
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${RED}"
    cat << "EOF"
    _____ _____ ____  __  __ ____  _     ___ _____ ____
   |_   _| ____|  _ \|  \/  |  _ \| |   |_ _|_   _/ ___|
     | | |  _| | |_) | |\/| | |_) | |    | |  | | \___ \
     | | | |___|  _ <| |  | |  __/| |___ | |  | |  ___) |
     |_| |_____|_| \_\_|  |_|_|   |_____|___| |_| |____/
EOF
    echo -e "${NC}"
    echo -e "${CYAN}    [ Installer - Multi-Protocol Brute-Force Tool ]${NC}"
    echo ""
}

check_python() {
    echo -e "${YELLOW}[*] Checking Python installation...${NC}"

    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        echo -e "${RED}[!] Python not found. Please install Python 3.8+${NC}"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}[+] Python found: $PYTHON (version $PYTHON_VERSION)${NC}"

    # Check Python version
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
        echo -e "${RED}[!] Python 3.8+ required. Current: $PYTHON_VERSION${NC}"
        exit 1
    fi
}

install_pip() {
    echo -e "${YELLOW}[*] Checking pip installation...${NC}"

    if $PYTHON -m pip --version &> /dev/null; then
        PIP="$PYTHON -m pip"
        echo -e "${GREEN}[+] pip found${NC}"
    else
        echo -e "${YELLOW}[*] Installing pip...${NC}"
        $PYTHON -m ensurepip --upgrade 2>/dev/null || {
            curl -sS https://bootstrap.pypa.io/get-pip.py | $PYTHON
        }
        PIP="$PYTHON -m pip"
        echo -e "${GREEN}[+] pip installed${NC}"
    fi
}

install_dependencies() {
    echo -e "${YELLOW}[*] Installing dependencies...${NC}"

    $PIP install --break-system-packages -r requirements.txt

    echo -e "${GREEN}[+] Dependencies installed${NC}"
}

install_package() {
    echo -e "${YELLOW}[*] Installing Inf3rno package...${NC}"

    $PIP install --break-system-packages -e .

    echo -e "${GREEN}[+] Inf3rno installed${NC}"
}

create_aliases() {
    echo -e "${YELLOW}[*] Creating shell aliases...${NC}"

    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [[ -n "$SHELL_RC" ]]; then
        # Check if alias already exists
        if ! grep -q "inf3rno" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Inf3rno alias" >> "$SHELL_RC"
            echo "alias inf3rno='python3 $(pwd)/inf3rno/cli.py'" >> "$SHELL_RC"
            echo -e "${GREEN}[+] Alias added to $SHELL_RC${NC}"
            echo -e "${YELLOW}[*] Run 'source $SHELL_RC' or restart terminal to use alias${NC}"
        else
            echo -e "${GREEN}[+] Alias already exists${NC}"
        fi
    fi
}

create_executable() {
    echo -e "${YELLOW}[*] Creating executable wrapper...${NC}"

    cat > inf3rno-cli << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/inf3rno/cli.py" "$@"
EOF

    chmod +x inf3rno-cli
    echo -e "${GREEN}[+] Executable created: ./inf3rno-cli${NC}"
}

show_usage() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${GREEN}[+] Installation complete!${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  Direct:      $PYTHON inf3rno/cli.py --help"
    echo "  Executable:  ./inf3rno-cli --help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./inf3rno-cli -t 192.168.1.1 --ssh -u admin -w wordlist.txt"
    echo "  ./inf3rno-cli --smart -t example.com -u admin --save-gen smart.txt"
    echo ""
    echo -e "${YELLOW}Documentation:${NC}"
    echo "  https://github.com/WalkingDreams798/inf3rno"
    echo ""
}

main() {
    print_banner

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}[*] Note: Some features may require root privileges${NC}"
    fi

    check_python
    install_pip
    install_dependencies
    install_package
    create_executable
    create_aliases
    show_usage
}

# Run installer
main
