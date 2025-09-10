#!/usr/bin/env bash

echo "=== Codex Diagnostics (Bash) ==="

echo "OS:"
uname -a 2>/dev/null || true
if command -v lsb_release >/dev/null 2>&1; then
  echo "---- lsb_release ----"
  lsb_release -a 2>/dev/null || true
fi
if [ "$(uname)" = "Darwin" ] && command -v sw_vers >/dev/null 2>&1; then
  echo "---- sw_vers ----"
  sw_vers || true
fi

echo
echo "Environment:"
echo "  SHELL: ${SHELL:-}"
echo "  PATH entries (first 20):"
echo "${PATH:-}" | tr ':' '\n' | sed -n '1,20p' | sed 's/^/    /'

echo
echo "Working directory:"
pwd

echo
echo "Repo root listing (first 50 lines):"
ls -la 2>/dev/null | sed -n '1,50p' | sed 's/^/  /'

check_cmd() {
  local name="$1"
  shift
  local args=("$@")
  if command -v "$name" >/dev/null 2>&1; then
    echo "FOUND $name: $(command -v "$name")"
    if [ ${#args[@]} -gt 0 ]; then
      "$name" "${args[@]}" 2>/dev/null | head -n 1 | sed 's/^/    /'
    fi
  else
    echo "MISSING $name"
  fi
}

echo
echo "Shell/tool availability:"
check_cmd bash --version
check_cmd zsh --version
check_cmd sh --version
check_cmd pwsh -v
check_cmd powershell -v
check_cmd git --version
check_cmd python --version
check_cmd python3 --version

echo
echo "Write test:"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp_file="$script_dir/_tmp_diagnostic_write_test_sh.txt"
if echo "ok" > "$tmp_file" 2>/dev/null; then
  echo "  Write to $tmp_file: OK"
  rm -f "$tmp_file" 2>/dev/null || true
else
  echo "  Write to $tmp_file: FAILED"
fi

echo
echo "Tips:"
echo "  - If shells are MISSING above, install one and add it to PATH."
echo "  - Configure your CLI to use an available shell (e.g., pwsh or bash)."
echo "  - Run with: bash tools/codex_diagnostics.sh"

