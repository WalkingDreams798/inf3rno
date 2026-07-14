#!/usr/bin/env python3
"""
Inf3rno - Multi-Protocol Brute-Force Tool
Author: WalkingDreams798
"""

import argparse
import sys
import os

from core.utils import print_banner, check_port, detect_service, scan_common_ports
from core.generator import PasswordGenerator
from core.state import StateManager
from modules.ssh import SSHBrute
from modules.ftp import FTPBrute
from modules.http import HTTPBrute
from modules.mysql import MySQLBrute


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
        """
    )

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
    service.add_argument("--http-port", type=int, default=80, help="HTTP port (default: 80)")
    service.add_argument("--login-url", help="HTTP login URL for form-based auth")
    service.add_argument("--fail-string", default="Invalid", help="HTTP fail string")

    generator = parser.add_argument_group("Password Generator")
    generator.add_argument("--gen-mask", help="Generate passwords with mask (?l=lower, ?u=upper, ?d=digit, ?s=special)")
    generator.add_argument("--gen-length", type=int, help="Generate passwords of specific length")
    generator.add_argument("--gen-charset", default="all", choices=["all", "alpha", "digits", "alphanum"],
                           help="Charset for length-based generation")
    generator.add_argument("--gen-random", type=int, help="Generate N random passwords")
    generator.add_argument("--save-gen", help="Save generated passwords to file")

    output = parser.add_argument_group("Output")
    output.add_argument("-o", "--output", help="Output file for found credentials")
    output.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    advanced = parser.add_argument_group("Advanced")
    advanced.add_argument("-T", "--threads", type=int, default=5, help="Number of threads (default: 5)")
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

    if not service:
        print("[!] No service specified. Use --ssh, --ftp, --http, --mysql, or --auto")
        return None, None

    if not check_port(args.target, port):
        print(f"[!] Port {port} is closed or unreachable.")
        return None, None

    # Select module
    if service == "SSH":
        module = SSHBrute(
            target=args.target,
            port=port,
            username=args.user or "root",
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
        )
    elif service == "FTP":
        module = FTPBrute(
            target=args.target,
            port=port,
            username=args.user or "anonymous",
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
        )
    elif service == "HTTP":
        module = HTTPBrute(
            target=args.target,
            port=port,
            username=args.user or "admin",
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
            login_url=args.login_url,
            fail_string=args.fail_string,
        )
    elif service == "MySQL":
        module = MySQLBrute(
            target=args.target,
            port=port,
            username=args.user or "root",
            wordlist=args.wordlist,
            threads=args.threads,
            output_file=args.output,
            verbose=args.verbose,
        )
    else:
        print(f"[!] Unsupported service: {service}")
        return None, None

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


def main():
    """Main function."""
    print_banner()

    args = parse_args()

    # Handle port listing
    if args.list:
        handle_list_ports(args)
        return

    # Handle list states
    if args.list_states:
        handle_list_states()
        return

    # Handle password generation
    if args.gen_mask or args.gen_length or args.gen_random:
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


if __name__ == "__main__":
    main()
