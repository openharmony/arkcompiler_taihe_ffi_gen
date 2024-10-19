# Utility function to include in each script.
# Example: source "$(dirname "$0")/common_lib.sh"

init_shell_options() {
    # Sane defaults.
    set -eu
    set -o pipefail
}

# Chdir to project root
chdir_root() {
    cd "$(dirname "$0")/.."
}

init_py_env() {
    init_shell_options
    chdir_root
    cd compiler
    source .venv/bin/activate
    set -x
}
