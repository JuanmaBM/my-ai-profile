import os
import sys
import argparse
import time
from pathlib import Path

# Ensure we run from the project root so output files land in the right place
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
# Make sure Python can import top-level modules like `cli.py`
sys.path.insert(0, str(PROJECT_ROOT))

# Import CLI command functions directly
from cli import github as cmd_github, linkedin as cmd_linkedin, merge as cmd_merge  # type: ignore


def _load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ[key] = value
    except Exception as e:
        print(f"[dotenv] error loading .env: {e}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GitHub, LinkedIn and merge steps in sequence")
    parser.add_argument("--github-user", required=True, help="GitHub username")
    parser.add_argument("--linkedin-user", required=True, help="LinkedIn public id/username")
    parser.add_argument("--name", required=True, help="Profile display name for the final merge")
    args = parser.parse_args()

    # Load environment variables from .env (if present)
    _load_dotenv(PROJECT_ROOT / ".env")

    start_ts = time.time()
    github_s = linkedin_s = merge_s = 0.0
    try:
        # 1) Analyze GitHub repos/code style
        print("▶️  Starting GitHub analysis…")
        t0 = time.time()
        cmd_github(args.github_user)
        github_s = time.time() - t0
        print(f"✅ GitHub completed in {github_s:.2f}s")

        # 2) Analyze LinkedIn posts/interests
        print("▶️  Starting LinkedIn analysis…")
        t0 = time.time()
        cmd_linkedin(args.linkedin_user)
        linkedin_s = time.time() - t0
        print(f"✅ LinkedIn completed in {linkedin_s:.2f}s")

        # 3) Merge into final profile
        print("▶️  Starting final merge…")
        t0 = time.time()
        cmd_merge(args.name)
        merge_s = time.time() - t0
        print(f"✅ Merge completed in {merge_s:.2f}s")
    except SystemExit as e:
        # In case Typer raises SystemExit internally
        return int(e.code)
    except Exception as e:
        print(f"Error running pipeline: {e}", file=sys.stderr)
        return 1
    finally:
        total_s = time.time() - start_ts
        print("——— Timing summary ———")
        print(f"GitHub:   {github_s:.2f}s")
        print(f"LinkedIn: {linkedin_s:.2f}s")
        print(f"Merge:    {merge_s:.2f}s")
        print(f"Total:    {total_s:.2f}s")

    print("✅ Pipeline completed: github → linkedin → merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main()) 