"""PostToolUse hook: ruff format + ruff check an edited .py file.

Exit 2 feeds the lint output back to Claude so it fixes the error.
"""

import json
import subprocess
import sys

payload = json.load(sys.stdin)
path = (
    (payload.get("tool_input") or {}).get("file_path")
    or (payload.get("tool_response") or {}).get("filePath")
    or ""
)

if path.endswith(".py"):
    ruff = [sys.executable, "-m", "ruff"]
    subprocess.run([*ruff, "format", "--quiet", path], capture_output=True)
    result = subprocess.run([*ruff, "check", "--quiet", path], capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write("ruff check failed:\n" + result.stdout + result.stderr)
        sys.exit(2)
