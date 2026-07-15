# Changelog

All notable changes to Inf3rno will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD workflows
- Security scanning workflow
- Release automation workflow
- Issue and PR templates
- Contributing guidelines
- Changelog

## [2.0.0] - 2024-01-15

### Added
- TUI dashboard with Rich
- REST API with FastAPI
- Unit tests (30 tests)
- Docker support (Dockerfile + docker-compose)
- Wiki documentation
- Plugin system
- `--tui` flag for interactive dashboard
- `--api` flag for REST API server
- `--list-plugins` flag for plugin management

### Changed
- Updated project structure
- Improved error handling

## [1.5.0] - 2024-01-10

### Added
- Smart wordlist generation
- Rule-based password generation
- Credential validator
- Rate limit detection
- `--smart` flag for smart wordlist
- `--gen-rule` flag for rule-based generation
- `--rate-limit` flag for rate limit detection

## [1.4.0] - 2024-01-05

### Added
- Username list support (`-U users.txt`)
- Delay/throttle option (`--delay`)
- Proxy support (`--proxy`)
- Report export (JSON, CSV, HTML)
- Multi-user brute-force support

## [1.3.0] - 2024-01-01

### Added
- MySQL brute-force module
- SMTP brute-force module
- Redis brute-force module
- PostgreSQL brute-force module
- Telnet brute-force module
- RDP detection module

## [1.2.0] - 2023-12-25

### Added
- Resume capability
- State management
- Progress bar with tqdm
- Colored output with colorama
- Reporter module

## [1.1.0] - 2023-12-20

### Added
- Password generator (mask, length, random)
- Port scanning
- Service detection
- Auto-detect mode

## [1.0.0] - 2023-12-15

### Added
- Initial release
- SSH brute-force module
- FTP brute-force module
- HTTP brute-force module
- Basic CLI interface
- Wordlist support
- Multi-threading support

[Unreleased]: https://github.com/WalkingDreams798/inf3rno/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/WalkingDreams798/inf3rno/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/WalkingDreams798/inf3rno/releases/tag/v1.0.0
