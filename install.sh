#!/usr/bin/env sh
# Install quickmeme. Installs uv (the Python tool manager) if missing,
# then installs the quickmeme CLI. Usage:
#   curl -fsSL https://raw.githubusercontent.com/jrdn1891/quickmeme/main/install.sh | sh
set -e

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # uv lands in ~/.local/bin; make it visible for the rest of this script
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing quickmeme..."
uv tool install --force git+https://github.com/jrdn1891/quickmeme

echo
echo "Done. Try:  quickmeme"
echo "(If 'quickmeme' isn't found, restart your terminal or add ~/.local/bin to PATH.)"
