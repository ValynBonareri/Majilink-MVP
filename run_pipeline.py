from pathlib import Path
import subprocess
import sys


BASE_DIR = Path(__file__).resolve().parent


def run_script(script_name):
    script_path = BASE_DIR / "scripts" / script_name

    print()
    print("=" * 60)
    print(f"RUNNING: {script_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(BASE_DIR),
        check=False
    )

    if result.returncode != 0:
        raise SystemExit(
            f"\nERROR: {script_name} failed "
            f"with exit code {result.returncode}"
        )


def main():
    run_script("download_chirps.py")
    run_script("process_chirps.py")
    run_script("rainfall_stats.py")

    print()
    print("=" * 60)
    print("RAINFALL PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()