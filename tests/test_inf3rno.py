"""Unit tests for Inf3rno."""

import os
import sys
import pytest
import tempfile
import shutil

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordGenerator:
    """Tests for PasswordGenerator class."""

    def setup_method(self):
        from inf3rno.core.generator import PasswordGenerator
        self.gen = PasswordGenerator()

    def test_generate_mask_lowercase(self):
        passwords = list(self.gen.generate_mask("?l?l?l"))
        assert len(passwords) > 0
        assert all(len(p) == 3 for p in passwords)
        assert all(p.islower() for p in passwords)

    def test_generate_mask_digits(self):
        passwords = list(self.gen.generate_mask("?d?d"))
        assert len(passwords) > 0
        assert all(p.isdigit() for p in passwords)

    def test_generate_mask_mixed(self):
        passwords = list(self.gen.generate_mask("?l?d"))
        assert len(passwords) > 0
        assert any(p.isalnum() for p in passwords)

    def test_generate_random(self):
        passwords = list(self.gen.generate_random(10))
        assert len(passwords) == 10

    def test_generate_random_unique(self):
        passwords = list(self.gen.generate_random(100))
        assert len(passwords) == len(set(passwords))

    def test_apply_rule_leet(self):
        result = self.gen._apply_rule("password", "leet")
        assert len(result) > 0
        assert any("4" in p or "3" in p for p in result)

    def test_apply_rule_capitalize(self):
        result = self.gen._apply_rule("password", "capitalize")
        assert len(result) > 0
        assert any(p[0].isupper() for p in result)

    def test_apply_rule_append_number(self):
        result = self.gen._apply_rule("test", "append_number")
        assert len(result) > 0
        assert any(p.endswith(("0", "1", "2", "3", "!", "@", "#")) for p in result)

    def test_apply_rule_duplicate(self):
        result = self.gen._apply_rule("ab", "duplicate")
        assert "abab" in result

    def test_apply_rule_reverse(self):
        result = self.gen._apply_rule("abc", "reverse")
        assert "cba" in result

    def test_generate_from_words(self):
        words = ["password", "admin"]
        rules = ["leet", "capitalize"]
        passwords = self.gen.generate_from_words(words, rules)
        assert len(passwords) > 2


class TestSmartWordlist:
    """Tests for SmartWordlist class."""

    def setup_method(self):
        from inf3rno.core.smart_wordlist import SmartWordlist
        self.smart = SmartWordlist()

    def test_generate_from_target(self):
        words = self.smart.generate_from_target("example.com", "admin")
        assert len(words) > 0
        assert any("example" in w.lower() for w in words)
        assert any("admin" in w.lower() for w in words)

    def test_generate_from_target_no_username(self):
        words = self.smart.generate_from_target("test.com")
        assert len(words) > 0

    def test_generate_from_word(self):
        variations = self.smart.generate_from_word("test")
        assert len(variations) > 0
        assert "test" in variations

    def test_generate_from_word_with_rules(self):
        variations = self.smart.generate_from_word("test", ["leet", "capitalize"])
        assert len(variations) > 0


class TestCredentialValidator:
    """Tests for CredentialValidator class."""

    def setup_method(self):
        from inf3rno.core.validator import CredentialValidator
        self.validator = CredentialValidator()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_validate_credential(self):
        result = self.validator.validate_credential(
            "admin", "password123", "SSH", "192.168.1.1"
        )
        assert result["username"] == "admin"
        assert result["password"] == "password123"
        assert result["validated"] is True

    def test_check_duplicate(self):
        credentials = [
            {"username": "admin", "password": "password123"},
            {"username": "root", "password": "toor"},
        ]
        assert self.validator.check_duplicate("admin", "password123", credentials) is True
        assert self.validator.check_duplicate("admin", "wrong", credentials) is False

    def test_merge_credentials(self):
        list1 = [{"username": "admin", "password": "pass1"}]
        list2 = [{"username": "admin", "password": "pass1"}, {"username": "root", "password": "pass2"}]
        merged = self.validator.merge_credentials(list1, list2)
        assert len(merged) == 2


class TestUtils:
    """Tests for utility functions."""

    def setup_method(self):
        from inf3rno.core.utils import check_port, detect_service, scan_common_ports
        self.check_port = check_port
        self.detect_service = detect_service
        self.scan_common_ports = scan_common_ports

    def test_check_port_invalid(self):
        result = self.check_port("192.168.1.1", 9999)
        assert result is False

    def test_detect_service_unknown(self):
        result = self.detect_service("192.168.1.1", 9999)
        assert result is None

    def test_scan_common_ports(self):
        result = self.scan_common_ports("127.0.0.1")
        assert isinstance(result, list)


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def setup_method(self):
        from inf3rno.core.bruteforce import RateLimiter
        self.limiter = RateLimiter(max_failures=3, window=60, pause_time=1)

    def test_record_failure(self):
        self.limiter.record_failure()
        assert len(self.limiter.failures) == 1

    def test_is_rate_limited(self):
        for _ in range(3):
            self.limiter.record_failure()
        assert self.limiter.is_rate_limited() is True

    def test_not_rate_limited(self):
        self.limiter.record_failure()
        assert self.limiter.is_rate_limited() is False


class TestStateManager:
    """Tests for StateManager class."""

    def setup_method(self):
        from inf3rno.core.state import StateManager
        self.state_manager = StateManager()
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager.state_file = os.path.join(self.temp_dir, "state.json")

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_save_and_get_state(self):
        self.state_manager.save_attack_state(
            "192.168.1.1", 22, "admin", "wordlist.txt", 100, [("admin", "pass")]
        )
        state = self.state_manager.get_attack_state("192.168.1.1", 22, "admin")
        assert state is not None
        assert state["attempts"] == 100

    def test_list_saved_states(self):
        self.state_manager.save_attack_state(
            "192.168.1.1", 22, "admin", "wordlist.txt", 100, []
        )
        states = self.state_manager.list_saved_states()
        assert len(states) == 1


class TestModules:
    """Tests for brute-force modules."""

    def setup_method(self):
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

        self.modules = {
            "SSH": SSHBrute,
            "FTP": FTPBrute,
            "HTTP": HTTPBrute,
            "MySQL": MySQLBrute,
            "SMTP": SMTPBrute,
            "Redis": RedisBrute,
            "PostgreSQL": PostgreSQLBrute,
            "Telnet": TelnetBrute,
            "SMB": SMBBrute,
            "VNC": VNCBrute,
            "SNMP": SNMPBrute,
        }

    def test_module_init(self):
        for name, module_class in self.modules.items():
            module = module_class(
                target="127.0.0.1",
                port=22,
                username="test",
                wordlist="wordlists/passwords.txt",
            )
            assert module.target == "127.0.0.1"


class TestReportExporter:
    """Tests for ReportExporter class."""

    def setup_method(self):
        from inf3rno.core.reporter import ReportExporter
        self.exporter = ReportExporter()
        self.temp_dir = tempfile.mkdtemp()
        self.exporter.output_dir = self.temp_dir

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_export_json(self):
        credentials = [("admin", "password123"), ("root", "toor")]
        filepath = self.exporter.export_json(credentials, "test.json", "192.168.1.1", 22, "SSH")
        assert os.path.exists(filepath)

    def test_export_csv(self):
        credentials = [("admin", "password123")]
        filepath = self.exporter.export_csv(credentials, "test.csv")
        assert os.path.exists(filepath)

    def test_export_html(self):
        credentials = [("admin", "password123")]
        filepath = self.exporter.export_html(credentials, "test.html", "192.168.1.1", 22, "SSH")
        assert os.path.exists(filepath)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
