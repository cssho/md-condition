"""PostToolUse hook: run the CI flake8 error gate on an edited .py file.

Exit 2 feeds the flake8 output back to Claude so it fixes the error.
"""
import json
import subprocess
import sys

payload = json.load(sys.stdin)
path = (payload.get("tool_input") or {}).get("file_path") \
    or (payload.get("tool_response") or {}).get("filePath") or ""

if path.endswith(".py"):
    result = subprocess.run(
        [sys.executable, "-m", "flake8", "--select=E9,F63,F7,F82",
         "--show-source", path],
        capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write("flake8 (CI gate) failed:\n" + result.stdout + result.stderr)
        sys.exit(2)
