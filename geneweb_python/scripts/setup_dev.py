#!/usr/bin/env python3
"""
Post-installation script that automatically installs pre-commit hooks.
This is called after pip install -e ".[dev]"
"""
import subprocess
import sys
from pathlib import Path


def is_git_repo():
    """Check if we're in a git repository."""
    # Check current directory
    if (Path.cwd() / ".git").exists():
        return True

    # Check parent directory (for when running from scripts/)
    parent = Path.cwd().parent
    if (parent / ".git").exists():
        return True

    # Check if we're in geneweb_python and parent has .git
    if Path.cwd().name == "geneweb_python":
        if (parent / ".git").exists():
            return True

    return False


def install_precommit_hooks():
    """Install pre-commit hooks if in a git repository."""
    if not is_git_repo():
        print("⚠️  Not in a git repository, skipping pre-commit hooks installation.")
        return False

    try:
        print("🔧 Installing pre-commit hooks...")
        subprocess.run(
            ["pre-commit", "install"], check=True, capture_output=True, text=True
        )
        print("✅ Pre-commit hooks installed successfully!")
        print("   Hooks will run automatically before each commit.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to install pre-commit hooks: {e}")
        print("   You can install them manually with: pre-commit install")
        return False
    except FileNotFoundError:
        print("⚠️  pre-commit not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pre-commit"], check=True
            )
            return install_precommit_hooks()
        except Exception as e:
            print(f"❌ Failed to install pre-commit: {e}")
            return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Geneweb Python - Post Installation Setup")
    print("=" * 60 + "\n")

    success = install_precommit_hooks()

    print("\n" + "=" * 60)
    if success:
        print("✅ Setup complete! You're ready to develop.")
        print("\nNext steps:")
        print("  1. Run tests: make test")
        print("  2. Start coding with TDD!")
    else:
        print("⚠️  Setup completed with warnings.")
        print("\nManual steps required:")
        print("  1. Install pre-commit: pip install pre-commit")
        print("  2. Setup hooks: pre-commit install")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)
