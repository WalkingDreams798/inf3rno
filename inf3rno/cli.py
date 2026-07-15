#!/usr/bin/env python3
"""
Inf3rno - Multi-Protocol Brute-Force Tool
Author: WalkingDreams798
"""

import argparse
import sys
import os

# Support both direct execution and package import
try:
    from .core.utils import print_banner, check_port, detect_service, scan_common_ports
    from .core.generator import PasswordGenerator
    from .core.smart_wordlist import SmartWordlist
    from .core.state import StateManager
    from .core.reporter import ReportExporter
    from .core.validator import CredentialValidator
    from .core.plugin import plugin_manager, load_plugins
    from .modules.ssh import SSHBrute
    from .modules.ftp import FTPBrute
    from .modules.http import HTTPBrute
    from .modules.mysql import MySQLBrute
    from .modules.smtp import SMTPBrute
    from .modules.redis import RedisBrute
    from .modules.postgresql import PostgreSQLBrute
    from .modules.telnet import TelnetBrute
    from .modules.smb import SMBBrute
    from .modules.vnc import VNCBrute
    from .modules.snmp import SNMPBrute
except ImportError:
    # Direct execution - add parent to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from inf3rno.core.utils import print_banner, check_port, detect_service, scan_common_ports
    from inf3rno.core.generator import PasswordGenerator
    from inf3rno.core.smart_wordlist import SmartWordlist
    from inf3rno.core.state import StateManager
    from inf3rno.core.reporter import ReportExporter
    from inf3rno.core.validator import CredentialValidator
    from inf3rno.core.plugin import plugin_manager, load_plugins
    from inf3rno.modules.ssh import SSHBrute
    from inf3rno.modules.ftp import FTPBrute
    from inf3rno.modules.http import HTTPBrute
    from inf3rno.modules.mysql import MySQLBrute
    from inf3rno.modules.smtp import SMTPBrute
    from inf3rno.modules.redis import RedisBrute
    from inf3rno.modules.postgresql import PostgreSQLBrute
    from inf3rno.modules.telnet import TelnetBrute
    from inf3rno.modules.smb import SMBBrute
    from inf3rno.modules.vnc import VNCBrute
    from inf3rno.modules.snmp import SNMPBrute


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Inf3rno - Multi-Protocol Brute-Force Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t 192.168.1.1 -u admin -w wordlist.txt
  %(prog)s -t 192.168.1.1 --ftp -u root -w passwords.txt
  %(prog)s -t target.com --http -U users.txt -w passwords.txt
  %(prog)s -t 192.168.1.1 -u admin --gen-mask "?l?l?l?d?d"
  %(prog)s -t scanme.org --auto
  %(prog)s -t 192.168.1.1 --ssh -U users.txt -w passwords.txt --delay 0.5
  %(prog)s -t 192.168.1.1 --ssh -u admin -w passwords.txt --proxy socks5://127.0.0.1:9050
  %(prog)s --tui                              # Launch TUI dashboard
  %(prog)s --api --api-port 8000              # Launch REST API server
        """
    )

    # Mode selection
    mode = parser.add_argument_group("Mode")
    mode.add_argument("--tui", action="store_true", help="Launch TUI dashboard")
    mode.add_argument("--api", action="store_true", help="Launch REST API server")
    mode.add_argument("--api-host", default="0.0.0.0", help="API server host (default: 0.0.0.0)")
    mode.add_argument("--api-port", type=int, default=8000, help="API server port (default: 8000)")
    mode.add_argument("--list-plugins", action="store_true", help="List installed plugins")
    mode.add_argument("--plugin-dir", default="plugins", help="Plugins directory (default: plugins)")

    target = parser.add_argument_group("Target")
    target.add_argument("-t", "--target", help="Target IP or hostname")
    target.add_argument("-p", "--port", type=int, help="Target port (auto-detect if not set)")
    target.add_argument("--auto", action="store_true", help="Auto-detect service and attack")

    auth = parser.add_argument_group("Authentication")
    auth.add_argument("-u", "--user", help="Single username")
    auth.add_argument("-U", "--userlist", help="File with usernames (one per line)")
    auth.add_argument("-w", "--wordlist", help="File with passwords")

    service = parser.add_argument_group("Service")
    service.add_argument("--ssh", action="store_true", help="SSH mode (port 22)")
    service.add_argument("--ftp", action="store_true", help="FTP mode (port 21)")
    service.add_argument("--http", action="store_true", help="HTTP mode (port 80)")
    service.add_argument("--mysql", action="store_true", help="MySQL mode (port 3306)")
    service.add_argument("--smtp", action="store_true", help="SMTP mode (port 587)")
    service.add_argument("--redis", action="store_true", help="Redis mode (port 6379)")
    service.add_argument("--postgresql", action="store_true", help="PostgreSQL mode (port 5432)")
    service.add_argument("--telnet", action="store_true", help="Telnet mode (port 23)")
    service.add_argument("--smb", action="store_true", help="SMB mode (port 445)")
    service.add_argument("--vnc", action="store_true", help="VNC mode (port 5900)")
    service.add_argument("--snmp", action="store_true", help="SNMP mode (port 161)")
    service.add_argument("--http-port", type=int, default=80, help="HTTP port (default: 80)")
    service.add_argument("--login-url", help="HTTP login URL for form-based auth")
    service.add_argument("--fail-string", default="Invalid", help="HTTP fail string")

    generator = parser.add_argument_group("Password Generator")
    generator.add_argument("--gen-mask", help="Generate passwords with mask (?l=lower, ?u=upper, ?d=digit, ?s=special)")
    generator.add_argument("--gen-length", type=int, help="Generate passwords of specific length")
    generator.add_argument("--gen-charset", default="all", choices=["all", "alpha", "digits", "alphanum"],
                           help="Charset for length-based generation")
    generator.add_argument("--gen-random", type=int, help="Generate N random passwords")
    generator.add_argument("--gen-rule", action="store_true", help="Generate with rules (leet, capitalize, etc)")
    generator.add_argument("--gen-rule-input", help="Input file for rule-based generation")
    generator.add_argument("--save-gen", help="Save generated passwords to file")

    smart = parser.add_argument_group("Smart Wordlist")
    smart.add_argument("--smart", action="store_true", help="Generate smart wordlist from target")
    smart.add_argument("--smart-rules", default="leet,capitalize,append_number",
                       help="Rules for smart generation (comma-separated)")
    smart.add_argument("--smart-max-length", type=int, default=12, help="Max password length for smart gen")

    output = parser.add_argument_group("Output")
    output.add_argument("-o", "--output", help="Output file for found credentials")
    output.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    output.add_argument("--export", choices=["json", "csv", "html", "all"], help="Export report format")
    output.add_argument("--export-file", help="Export filename (without extension)")

    advanced = parser.add_argument_group("Advanced")
    advanced.add_argument("-T", "--threads", type=int, default=5, help="Number of threads (default: 5)")
    advanced.add_argument("--delay", type=float, default=0.0, help="Delay between attempts in seconds (default: 0)")
    advanced.add_argument("--proxy", help="Proxy URL (socks5://host:port, http://host:port)")
    advanced.add_argument("--rate-limit", action="store_true", help="Enable rate limit detection")
    advanced.add_argument("--rate-max-failures", type=int, default=10, help="Max failures before pause (default: 10)")
    advanced.add_argument("--rate-window", type=int, default=60, help="Failure window in seconds (default: 60)")
    advanced.add_argument("--rate-pause-time", type=int, default=60, help="Pause duration when rate limited (default: 60)")
    advanced.add_argument("--list", action="store_true", help="Scan and list common open ports")
    advanced.add_argument("--resume", action="store_true", help="Resume previous attack")
    advanced.add_argument("--list-states", action="store_true", help="List saved attack states")

    return parser.parse_args()


def handle_generator(args):
    """Handle password generation."""
    gen = PasswordGenerator()

    if args.gen_mask:
        print(f"[*] Generating passwords with mask: {args.gen_mask}")
        passwords = gen.generate_mask(args.gen_mask)

    elif args.gen_length:
        print(f"[*] Generating passwords of length {args.gen_length} with charset: {args.gen_charset}")
        passwords = gen.generate_length(args.gen_length, args.gen_charset)

    elif args.gen_random:
        print(f"[*] Generating {args.gen_random} random passwords")
        passwords = gen.generate_random(args.gen_random)

    elif args.gen_rule:
        # Rule-based generation from input file
        if not args.gen_rule_input:
            print("[!] Input file required for rule-based generation. Use --gen-rule-input")
            return False

        if not os.path.exists(args.gen_rule_input):
            print(f"[!] Input file not found: {args.gen_rule_input}")
            return False

        with open(args.gen_rule_input, "r") as f:
            words = [line.strip() for line in f if line.strip()]

        rules = ["leet", "capitalize", "append_number", "prepend_number", "duplicate", "reverse"]
        print(f"[*] Generating {len(words)} words with {len(rules)} rules...")
        passwords = gen.generate_from_words(words, rules)

    elif args.smart:
        # Smart wordlist generation
        target = args.target or "localhost"
        username = args.user or "admin"
        rules = args.smart_rules.split(",")

        print(f"[*] Generating smart wordlist for: {target}")
        print(f"[*] Username: {username}")
        print(f"[*] Rules: {rules}")

        smart = SmartWordlist()
        base_words = smart.generate_from_target(
            target, username,
            include_numbers=True,
            include_symbols=True,
            max_length=args.smart_max_length
        )

        # Apply rules to base words
        all_passwords = []
        for word in base_words:
            variations = gen.apply_rules(word, rules)
            all_passwords.extend(variations)

        # Deduplicate
        seen = set()
        passwords = []
        for p in all_passwords:
            if p not in seen:
                seen.add(p)
                passwords.append(p)

    else:
        return False

    if args.save_gen:
        gen.save_to_file(args.save_gen, passwords)
        return True

    output_file = args.save_gen or "output/generated.txt"
    gen.save_to_file(output_file, passwords)
    return True


def get_brute_module(args):
    """Select the appropriate brute-force module."""
    port = args.port
    service = None

    # Auto-detect service
    if args.auto:
        if not port:
            print("[*] Auto-detecting service...")
            open_ports = scan_common_ports(args.target)
            if not open_ports:
                print("[-] No open ports found.")
                return None, None

            print("[*] Open ports:")
            for p, s in open_ports:
                print(f"    {p}/{s}")

            # Use first open port
            port, service = open_ports[0]
            print(f"\n[*] Using: {port}/{service}")
        else:
            service = detect_service(args.target, port)
            print(f"[*] Detected service on port {port}: {service}")

    # Manual service selection
    if args.ssh:
        service = "SSH"
        port = port or 22
    elif args.ftp:
        service = "FTP"
        port = port or 21
    elif args.http:
        service = "HTTP"
        port = port or args.http_port
    elif args.mysql:
        service = "MySQL"
        port = port or 3306
    elif args.smtp:
        service = "SMTP"
        port = port or 587
    elif args.redis:
        service = "Redis"
        port = port or 6379
    elif args.postgresql:
        service = "PostgreSQL"
        port = port or 5432
    elif args.telnet:
        service = "Telnet"
        port = port or 23
    elif args.smb:
        service = "SMB"
        port = port or 445
    elif args.vnc:
        service = "VNC"
        port = port or 5900
    elif args.snmp:
        service = "SNMP"
        port = port or 161

    if not service:
        print("[!] No service specified. Use --ssh, --ftp, --http, --mysql, --smtp, --redis, --postgresql, --telnet, --smb, --vnc, --snmp, or --auto")
        return None, None

    if not check_port(args.target, port):
        print(f"[!] Port {port} is closed or unreachable.")
        return None, None

    # Load usernames
    usernames = []
    if args.userlist:
        try:
            with open(args.userlist, "r", encoding="utf-8", errors="ignore") as f:
                usernames = [line.strip() for line in f if line.strip()]
            print(f"[*] Loaded {len(usernames)} usernames from {args.userlist}")
        except FileNotFoundError:
            print(f"[!] Userlist not found: {args.userlist}")
            return None, None
    else:
        usernames = [args.user or "admin"]

    # Select module class
    module_class = None
    default_user = "root"
    extra_kwargs = {}

    if service == "SSH":
        module_class = SSHBrute
        default_user = "root"
    elif service == "FTP":
        module_class = FTPBrute
        default_user = "anonymous"
    elif service == "HTTP":
        module_class = HTTPBrute
        default_user = "admin"
        extra_kwargs = {
            "login_url": args.login_url,
            "fail_string": args.fail_string,
        }
    elif service == "MySQL":
        module_class = MySQLBrute
        default_user = "root"
    elif service == "SMTP":
        module_class = SMTPBrute
        default_user = ""
    elif service == "Redis":
        module_class = RedisBrute
        default_user = "default"
    elif service == "PostgreSQL":
        module_class = PostgreSQLBrute
        default_user = "postgres"
    elif service == "Telnet":
        module_class = TelnetBrute
        default_user = "admin"
    elif service == "SMB":
        module_class = SMBBrute
        default_user = "Administrator"
    elif service == "VNC":
        module_class = VNCBrute
        default_user = ""
    elif service == "SNMP":
        module_class = SNMPBrute
        default_user = "public"
    else:
        print(f"[!] Unsupported service: {service}")
        return None, None

    # Create module(s)
    if len(usernames) == 1:
        # Single username
        module = module_class(
            target=args.target,
            port=port,
            username=usernames[0] or default_user,
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
            delay=args.delay,
            proxy=args.proxy,
            rate_limit=args.rate_limit,
            rate_max_failures=args.rate_max_failures,
            rate_window=args.rate_window,
            rate_pause_time=args.rate_pause_time,
            **extra_kwargs,
        )
    else:
        # Multiple usernames
        from inf3rno.core.bruteforce import MultiUserBrute
        module = MultiUserBrute(
            brute_class=module_class,
            target=args.target,
            port=port,
            usernames=usernames,
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
            delay=args.delay,
            proxy=args.proxy,
            rate_limit=args.rate_limit,
            rate_max_failures=args.rate_max_failures,
            rate_window=args.rate_window,
            rate_pause_time=args.rate_pause_time,
            **extra_kwargs,
        )

    return module, service


def handle_list_ports(args):
    """Handle port listing."""
    print(f"[*] Scanning common ports on {args.target}...")
    open_ports = scan_common_ports(args.target)

    if open_ports:
        print("\n[+] Open ports found:")
        for port, service in open_ports:
            print(f"    {port}/{service or 'Unknown'}")
    else:
        print("[-] No open ports found.")


def handle_list_states():
    """Handle listing saved attack states."""
    state_manager = StateManager()
    states = state_manager.list_saved_states()

    if states:
        print("\n[+] Saved attack states:")
        for state in states:
            print(f"    {state['key']} - Attempts: {state['attempts']} - {state['timestamp']}")
    else:
        print("[-] No saved states found.")


def handle_list_plugins():
    """Handle listing installed plugins."""
    plugins = plugin_manager.list_plugins()

    if plugins:
        print("\n[+] Installed plugins:")
        for plugin in plugins:
            print(f"    {plugin['name']} v{plugin['version']} - {plugin['description']}")
    else:
        print("[-] No plugins installed.")


def main():
    """Main function."""
    args = parse_args()

    # Load plugins
    load_plugins(args.plugin_dir)

    # Handle TUI mode
    if args.tui:
        from .tui import main as tui_main
        tui_main()
        return

    # Handle API mode
    if args.api:
        from .api import run_api
        print(f"[*] Starting API server on {args.api_host}:{args.api_port}")
        run_api(host=args.api_host, port=args.api_port)
        return

    # Handle list plugins
    if args.list_plugins:
        handle_list_plugins()
        return

    print_banner()

    # Handle port listing
    if args.list:
        handle_list_ports(args)
        return

    # Handle list states
    if args.list_states:
        handle_list_states()
        return

    # Handle password generation
    if args.gen_mask or args.gen_length or args.gen_random or args.gen_rule or args.smart:
        if not handle_generator(args):
            print("[!] Password generation failed.")
        return

    # Check for target
    if not args.target:
        print("[!] Target required. Use -t or --target")
        sys.exit(1)

    # Check for wordlist
    if not args.wordlist:
        print("[!] Wordlist required. Use -w or --wordlist")
        sys.exit(1)

    if not os.path.exists(args.wordlist):
        print(f"[!] Wordlist not found: {args.wordlist}")
        sys.exit(1)

    # Get brute-force module
    module, service = get_brute_module(args)
    if not module:
        sys.exit(1)

    print(f"[*] Module: {service}")
    print(f"[*] Starting brute-force attack...\n")

    # Run attack
    module.run(resume=args.resume)

    # Export report if requested
    if args.export and hasattr(module, "found") and module.found:
        exporter = ReportExporter()
        export_file = args.export_file or "report"

        if args.export == "all":
            exporter.export_all(
                module.found,
                target=args.target,
                port=args.port or 0,
                service=service,
            )
        elif args.export == "json":
            exporter.export_json(
                module.found,
                filename=f"{export_file}.json",
                target=args.target,
                port=args.port or 0,
                service=service,
            )
        elif args.export == "csv":
            exporter.export_csv(
                module.found,
                filename=f"{export_file}.csv",
            )
        elif args.export == "html":
            exporter.export_html(
                module.found,
                filename=f"{export_file}.html",
                target=args.target,
                port=args.port or 0,
                service=service,
            )
    elif args.export and hasattr(module, "all_found") and module.all_found:
        # MultiUserBrute case
        exporter = ReportExporter()
        export_file = args.export_file or "report"

        if args.export == "all":
            exporter.export_all(
                module.all_found,
                target=args.target,
                port=args.port or 0,
                service=service,
            )
        elif args.export == "json":
            exporter.export_json(
                module.all_found,
                filename=f"{export_file}.json",
                target=args.target,
                port=args.port or 0,
                service=service,
            )
        elif args.export == "csv":
            exporter.export_csv(
                module.all_found,
                filename=f"{export_file}.csv",
            )
        elif args.export == "html":
            exporter.export_html(
                module.all_found,
                filename=f"{export_file}.html",
                target=args.target,
                port=args.port or 0,
                service=service,
            )


if __name__ == "__main__":
    main()
