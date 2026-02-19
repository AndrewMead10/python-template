#!/usr/bin/env python3
"""Interactive setup script for python-template."""

import secrets


def main() -> None:
    print("\nPython App Setup\n")
    print("This script will help you configure your local Python web application.\n")

    app_name = input("App name [Python App]: ").strip() or "Python App"
    app_url = input("App URL [http://localhost:8000]: ").strip() or "http://localhost:8000"

    secret_key = secrets.token_urlsafe(32)
    print(f"\nGenerated secret key: {secret_key}")

    use_google = input("\nEnable Google OAuth? (y/N): ").strip().lower() == "y"
    google_client_id = ""
    google_client_secret = ""
    if use_google:
        print(
            "\nCreate OAuth credentials at: "
            "https://console.cloud.google.com/apis/credentials"
        )
        google_client_id = input("Google Client ID: ").strip()
        google_client_secret = input("Google Client Secret: ").strip()

    db_url = input("\nDatabase URL [sqlite:///./data.db]: ").strip() or "sqlite:///./data.db"

    env_content = f"""# App
APP_NAME={app_name}
APP_URL={app_url}
SECRET_KEY={secret_key}
DEBUG=true

# Database
DATABASE_URL={db_url}

# Auth - Google OAuth
GOOGLE_CLIENT_ID={google_client_id}
GOOGLE_CLIENT_SECRET={google_client_secret}

# Storage
STORAGE_PATH=./uploads

# Logging
LOG_LEVEL=INFO
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n.env file created")
    print("\nNext steps:")
    print("  1. uv sync")
    print("  2. uv run alembic upgrade head")
    print("  3. uv run uvicorn app.main:app --reload")
    print(f"\nYour app will be running at {app_url}\n")
    print("API docs available at: http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
