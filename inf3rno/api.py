"""REST API for Inf3rno."""

import os
import sys
import json
import uuid
import threading
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inf3rno.core.utils import check_port, detect_service, scan_common_ports
from inf3rno.core.generator import PasswordGenerator
from inf3rno.core.smart_wordlist import SmartWordlist
from inf3rno.modules.ssh import SSHBrute
from inf3rno.modules.ftp import FTPBrute
from inf3rno.modules.http import HTTPBrute
from inf3rno.modules.mysql import MySQLBrute
from inf3rno.modules.smtp import SMTPBrute
from inf3rno.modules.redis import RedisBrute
from inf3rno.modules.postgresql import PostgreSQLBrute
from inf3rno.modules.telnet import TelnetBrute


# Pydantic Models
class ServiceType(str, Enum):
    ssh = "ssh"
    ftp = "ftp"
    http = "http"
    mysql = "mysql"
    smtp = "smtp"
    redis = "redis"
    postgresql = "postgresql"
    telnet = "telnet"


class AttackRequest(BaseModel):
    target: str = Field(..., description="Target IP or hostname")
    service: ServiceType = Field(..., description="Service type")
    port: Optional[int] = Field(None, description="Target port (auto-detect if not set)")
    username: str = Field("admin", description="Username")
    wordlist: str = Field("wordlists/passwords.txt", description="Wordlist file path")
    threads: int = Field(5, ge=1, le=50, description="Number of threads")
    delay: float = Field(0, ge=0, description="Delay between attempts")
    rate_limit: bool = Field(False, description="Enable rate limit detection")
    proxy: Optional[str] = Field(None, description="Proxy URL")


class AttackResponse(BaseModel):
    id: str
    target: str
    service: str
    port: int
    status: str
    created_at: str


class CredentialResponse(BaseModel):
    username: str
    password: str
    service: str
    target: str


class GenerateRequest(BaseModel):
    target: str = Field("localhost", description="Target for smart generation")
    username: str = Field("admin", description="Username")
    mode: str = Field("smart", description="Generation mode: smart, mask, random")
    mask: Optional[str] = Field(None, description="Mask pattern for mask mode")
    count: int = Field(1000, ge=1, description="Number of passwords for random mode")
    rules: List[str] = Field(["leet", "capitalize", "append_number"], description="Rules for smart mode")


class GenerateResponse(BaseModel):
    count: int
    passwords: List[str]
    file_path: Optional[str]


# In-memory storage
attacks: Dict[str, dict] = {}
found_credentials: List[dict] = []

# FastAPI app
app = FastAPI(
    title="Inf3rno API",
    description="Multi-Protocol Brute-Force Tool REST API",
    version="1.0.0",
)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Inf3rno API",
        "version": "1.0.0",
        "description": "Multi-Protocol Brute-Force Tool REST API",
        "endpoints": {
            "docs": "/docs",
            "attacks": "/api/attacks",
            "generate": "/api/generate",
            "scan": "/api/scan",
        }
    }


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Attack endpoints
@app.post("/api/attacks", response_model=AttackResponse)
async def create_attack(request: AttackRequest, background_tasks: BackgroundTasks):
    """Create and start a new brute-force attack."""
    attack_id = str(uuid.uuid4())[:8]

    # Get port
    port = request.port
    if not port:
        port_map = {
            "ssh": 22, "ftp": 21, "http": 80, "mysql": 3306,
            "smtp": 587, "redis": 6379, "postgresql": 5432, "telnet": 23,
        }
        port = port_map.get(request.service, 22)

    # Check if port is open
    if not check_port(request.target, port):
        raise HTTPException(status_code=400, detail=f"Port {port} is closed or unreachable")

    # Create attack record
    attack = {
        "id": attack_id,
        "target": request.target,
        "service": request.service.value,
        "port": port,
        "username": request.username,
        "wordlist": request.wordlist,
        "threads": request.threads,
        "delay": request.delay,
        "rate_limit": request.rate_limit,
        "proxy": request.proxy,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "attempts": 0,
        "found": [],
    }

    attacks[attack_id] = attack

    # Start attack in background
    background_tasks.add_task(run_attack, attack)

    return AttackResponse(
        id=attack_id,
        target=request.target,
        service=request.service.value,
        port=port,
        status="running",
        created_at=attack["created_at"],
    )


def run_attack(attack: dict):
    """Run brute-force attack in background."""
    try:
        # Select module
        module_map = {
            "ssh": SSHBrute,
            "ftp": FTPBrute,
            "http": HTTPBrute,
            "mysql": MySQLBrute,
            "smtp": SMTPBrute,
            "redis": RedisBrute,
            "postgresql": PostgreSQLBrute,
            "telnet": TelnetBrute,
        }

        module_class = module_map.get(attack["service"])
        if not module_class:
            attack["status"] = "failed"
            return

        module = module_class(
            target=attack["target"],
            port=attack["port"],
            username=attack["username"],
            wordlist=attack["wordlist"],
            threads=attack["threads"],
            delay=attack["delay"],
            rate_limit=attack["rate_limit"],
            proxy=attack["proxy"],
        )

        # Run attack
        module.run()

        # Update attack record
        attack["attempts"] = module.attempts
        attack["found"] = module.found
        attack["status"] = "completed"

        # Add to global found credentials
        for user, pwd in module.found:
            found_credentials.append({
                "username": user,
                "password": pwd,
                "service": attack["service"],
                "target": attack["target"],
            })

    except Exception as e:
        attack["status"] = "failed"
        attack["error"] = str(e)


@app.get("/api/attacks", response_model=List[AttackResponse])
async def list_attacks():
    """List all attacks."""
    return [
        AttackResponse(
            id=attack["id"],
            target=attack["target"],
            service=attack["service"],
            port=attack["port"],
            status=attack["status"],
            created_at=attack["created_at"],
        )
        for attack in attacks.values()
    ]


@app.get("/api/attacks/{attack_id}")
async def get_attack(attack_id: str):
    """Get attack details."""
    if attack_id not in attacks:
        raise HTTPException(status_code=404, detail="Attack not found")

    attack = attacks[attack_id]
    return {
        "id": attack["id"],
        "target": attack["target"],
        "service": attack["service"],
        "port": attack["port"],
        "username": attack["username"],
        "status": attack["status"],
        "attempts": attack["attempts"],
        "found": attack["found"],
        "created_at": attack["created_at"],
    }


@app.delete("/api/attacks/{attack_id}")
async def delete_attack(attack_id: str):
    """Delete an attack."""
    if attack_id not in attacks:
        raise HTTPException(status_code=404, detail="Attack not found")

    del attacks[attack_id]
    return {"message": "Attack deleted"}


# Credentials endpoints
@app.get("/api/credentials", response_model=List[CredentialResponse])
async def list_credentials():
    """List all found credentials."""
    return [
        CredentialResponse(
            username=cred["username"],
            password=cred["password"],
            service=cred["service"],
            target=cred["target"],
        )
        for cred in found_credentials
    ]


@app.delete("/api/credentials")
async def clear_credentials():
    """Clear all found credentials."""
    found_credentials.clear()
    return {"message": "Credentials cleared"}


# Generate endpoints
@app.post("/api/generate", response_model=GenerateResponse)
async def generate_passwords(request: GenerateRequest):
    """Generate passwords."""
    gen = PasswordGenerator()
    passwords = []

    if request.mode == "smart":
        smart = SmartWordlist()
        base_words = smart.generate_from_target(
            request.target,
            request.username,
            include_numbers=True,
            include_symbols=True,
        )

        for word in base_words:
            variations = gen.apply_rules(word, request.rules)
            passwords.extend(variations)

    elif request.mode == "mask":
        if not request.mask:
            raise HTTPException(status_code=400, detail="Mask required for mask mode")
        passwords = list(gen.generate_mask(request.mask))

    elif request.mode == "random":
        passwords = list(gen.generate_random(request.count))

    else:
        raise HTTPException(status_code=400, detail="Invalid mode")

    # Deduplicate
    seen = set()
    unique = []
    for p in passwords:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return GenerateResponse(
        count=len(unique),
        passwords=unique[:1000],  # Limit response size
        file_path=None,
    )


# Scan endpoints
@app.get("/api/scan/{target}")
async def scan_target(target: str):
    """Scan common ports on target."""
    open_ports = scan_common_ports(target)

    return {
        "target": target,
        "open_ports": [
            {"port": port, "service": service}
            for port, service in open_ports
        ],
    }


@app.get("/api/scan/{target}/detect")
async def detect_service_endpoint(target: str, port: int):
    """Detect service on specific port."""
    if not check_port(target, port):
        raise HTTPException(status_code=400, detail="Port is closed or unreachable")

    service = detect_service(target, port)

    return {
        "target": target,
        "port": port,
        "service": service,
    }


# Export endpoints
@app.get("/api/export/{format}")
async def export_results(format: str):
    """Export results to file."""
    if format not in ["json", "csv", "html"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == "json":
        filename = f"output/export_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump({
                "tool": "Inf3rno API",
                "timestamp": datetime.now().isoformat(),
                "credentials": found_credentials,
            }, f, indent=2)

    elif format == "csv":
        filename = f"output/export_{timestamp}.csv"
        with open(filename, "w") as f:
            f.write("Username,Password,Service,Target\n")
            for cred in found_credentials:
                f.write(f"{cred['username']},{cred['password']},{cred['service']},{cred['target']}\n")

    elif format == "html":
        filename = f"output/export_{timestamp}.html"
        html = """<!DOCTYPE html>
<html>
<head><title>Inf3rno Export</title></head>
<body>
<h1>Inf3rno Credentials Export</h1>
<table border="1">
<tr><th>Username</th><th>Password</th><th>Service</th><th>Target</th></tr>
"""
        for cred in found_credentials:
            html += f"<tr><td>{cred['username']}</td><td>{cred['password']}</td><td>{cred['service']}</td><td>{cred['target']}</td></tr>\n"
        html += "</table></body></html>"

        with open(filename, "w") as f:
            f.write(html)

    return {
        "format": format,
        "file": filename,
        "count": len(found_credentials),
    }


def run_api(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api()
