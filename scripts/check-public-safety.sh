#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

strict_public=0
if [[ "${1:-}" == "--strict-public" ]]; then
  strict_public=1
elif [[ $# -gt 0 ]]; then
  echo "Usage: bash scripts/check-public-safety.sh [--strict-public]" >&2
  exit 2
fi

paths=(README.md CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md CHANGELOG.md PUBLIC_REPO_CHECKLIST.md .github scripts)

patterns=(
  'AKIA[0-9A-Z]{16}'
  '-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----'
  'ghp_[A-Za-z0-9]{36,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'xox[baprs]-[A-Za-z0-9-]+'
  'AIza[0-9A-Za-z\-_]{35}'
  'https?://[^[:space:]]+\.(internal|corp|local)(/|$)'
)

strict_patterns=(
  'https://github.com/<owner>/<repo>/security/policy'
  '<owner>'
  '<repo>'
  'talos-private'
)

status=0

tmpfile="$(mktemp)"
trap 'rm -f "$tmpfile"' EXIT

base_excludes=(--exclude-dir=.git --exclude-dir=.context --exclude=scripts/check-public-safety.sh)

check_patterns() {
  local label="$1"
  shift
  local pattern
  for pattern in "$@"; do
    if grep -RInE "${base_excludes[@]}" -- "$pattern" "${paths[@]}" >"$tmpfile" 2>/dev/null; then
      echo "${label}: $pattern"
      cat "$tmpfile"
      echo
      status=1
    fi
  done
}

check_patterns "Potential match" "${patterns[@]}"

if [[ "$strict_public" -eq 1 ]]; then
  check_patterns "Strict-public match" "${strict_patterns[@]}"
fi

if [[ "$status" -eq 0 ]]; then
  if [[ "$strict_public" -eq 1 ]]; then
    echo "Strict public safety check passed: no configured secret, internal-URL, or publication-placeholder patterns found in scoped files."
  else
    echo "Public safety check passed: no obvious secrets or internal URL patterns found in scoped files."
  fi
else
  if [[ "$strict_public" -eq 1 ]]; then
    echo "Strict public safety check failed: review the matches above before publishing."
  else
    echo "Public safety check failed: review the matches above."
  fi
fi

exit "$status"
