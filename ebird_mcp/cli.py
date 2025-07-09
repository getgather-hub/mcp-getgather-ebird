from dataclasses import dataclass
from typing import List, Any
import sys
import os
import argparse
import requests
from fastmcp import FastMCP


def main():
    parser = argparse.ArgumentParser(
        description="eBird MCP CLI - Interface for eBird integration"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    get_birds_parser = subparsers.add_parser("get-birds", help="Get checklists from eBird")
    get_birds_parser.add_argument("--username", required=True, help="eBird username")
    get_birds_parser.add_argument("--password", required=True, help="eBird password")
    get_birds_parser.add_argument("--host", default="127.0.0.1:8000", help="Host URL (default: 127.0.0.1:8000)")

    args = parser.parse_args()

    if args.command == "get-birds":
        try:
            response = get_ebird_birds(args.username, args.password, args.host)
            print(f"Authenticated! Profile ID: {response.profile_id}")
            print(f"Found {len(response.bundles)} birds")
            for bundle in response.bundles:
                print(f"- {bundle.species} on {bundle.date} at {bundle.location}")
        except AuthException as e:
            print(f"Failed to get birds: {e}")
            sys.exit(1)
            
    else:
        mcp()


@dataclass()
class Bundle(object):
    species: str
    date: str
    location: str


@dataclass
class AuthResponse(object):
    profile_id: str
    bundles: List[Bundle]


class AuthException(Exception):
    msg: str


class AuthError(AuthException):
    def __init__(self, msg):
        self.msg = msg


def get_ebird_birds(username: str, password: str, host: str = "127.0.0.1:8000") -> AuthResponse:
    payload = {
        "platform": "local-bundle",
        "framework": "patchright",
        "browser": "chromium",
        "brand_name": "ebird",
        "state": {
            "inputs": {
                "username": username,
                "password": password,
            }
        },
    }

    try:
        response = requests.post(f"http://{host}/auth/ebird", json=payload)
        response_json = response.json()
    except requests.exceptions.ConnectionError:
        raise AuthError(
            f"Cannot connect to getgather service at {host}. "
            "Please ensure getgather is running:\n"
            "docker run -p 8000:8000 getgather/dax"
        )

    if response.status_code != 200:
        raise AuthError(response.text)

    error_msg = response_json["state"]["error"]
    if error_msg:
        raise AuthError(msg=error_msg)

    profile_id = response_json["profile_id"]
    bundles = get_bundle(response_json["extract_result"]["bundles"])
    return AuthResponse(profile_id=profile_id, bundles=bundles)


def get_bundle(bundles: List[Any]) -> List[Bundle]:
    bundles_response = []

    for bundle in bundles:
        if not isinstance(bundle["content"], list):
            continue

        for content in bundle["content"]:
            bundles_response.append(
                Bundle(
                    species=content["species"],
                    date=content["date"],
                    location=content["location"],
                )
            )

    return bundles_response


def mcp():
    mcp_server = FastMCP("eBird MCP")
    
    def get_auth_response():
        """Helper function to get cached auth response or authenticate if needed."""
        username = os.getenv("EBIRD_USERNAME")
        password = os.getenv("EBIRD_PASSWORD")
        
        if not username or not password:
            raise AuthError("EBIRD_USERNAME and EBIRD_PASSWORD environment variables must be set")
        
        host = os.getenv("GETGATHER_URL", "127.0.0.1:8000")
        return get_ebird_birds(username, password, host)
    
    @mcp_server.tool()
    def get_birds() -> dict:
        """
        Get birds from eBird using configured credentials.
        Credentials should be set via environment variables EBIRD_USERNAME, and EBIRD_PASSWORD.
        
        Returns:
            Dictionary containing profile_id and list of birds
        """
        try:
            response = get_auth_response()
            return {
                "profile_id": response.profile_id,
                "birds": [
                    {
                        "species": bundle.species,
                        "date": bundle.date,
                        "location": bundle.location
                    }
                    for bundle in response.bundles
                ]
            }
        except AuthException as e:
            return {"error": str(e.msg)}
    
    
    mcp_server.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
