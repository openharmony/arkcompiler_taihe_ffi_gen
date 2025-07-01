# Utility function to include in each script.
# Example: source "$(dirname "$0")/common_lib.sh"

# Logging
COLOR_RST='\033[0m' COLOR_INV="\033[7m"
COLOR_RED='\033[31m' COLOR_GREEN='\033[32m' COLOR_BLUE='\033[34m' COLOR_GREY='\033[90m'
log_error() { echo -e "${COLOR_INV}${COLOR_RED}[!]${COLOR_RST} $*" >&2; }
log_stage() { echo -e "${COLOR_INV}${COLOR_GREEN}[*]${COLOR_RST} $*" >&2; }
log_action() { echo -e "${COLOR_INV}${COLOR_BLUE}[-]${COLOR_RST} $*" >&2; }
log_verbose() { echo -e "${COLOR_INV}${COLOR_GREY}[.]${COLOR_RST}${COLOR_GREY} $*${COLOR_RST}" >&2; }

PROJECT_ROOT="$(realpath "$(dirname "$0")"/..)"

init_shell_options() { set -eu -o pipefail; }

chdir_root() { cd "$PROJECT_ROOT"; }

# Shorthand for running the standard uv.
_uv() { uv --directory="$PROJECT_ROOT" "$@"; }

init_py_env() {
    init_shell_options
    chdir_root
    source .venv/bin/activate
    export PYTHONPATH="$PROJECT_ROOT/compiler"
    set -x
}
