from pathlib import Path

import appdirs
import click

# Entrypoint aka binary name aka script name
# Entrypoint must match the name defined in pyproject.toml under
# [tool.poetry.scripts] section
ENTRYPOINT = "dapp-manager"
COMPLETION_FUNC_NAME = f"{ENTRYPOINT}_completion"
SCRIPTS_DIR = Path(__file__).parent / "scripts"

DEFAULT_SHELL_FILES = {
    "bash": Path.home() / ".bashrc",
    "fish": Path(appdirs.user_config_dir("fish"))
    / "completions"
    / f"{ENTRYPOINT}.fish",
    "zsh": Path.home() / ".zshrc",
}


def install_autocomplete(shell: str, path: Path = None) -> None:
    # File containing the shell-specific completion script
    script_file = SCRIPTS_DIR / f".{ENTRYPOINT}.{shell}"
    target_file = path or DEFAULT_SHELL_FILES[shell]

    # Create the target file if it doesn't already exist
    target_file.touch(exist_ok=True)

    # Check if the target file already contains the completion script
    with target_file.open() as f:
        if COMPLETION_FUNC_NAME in target_file.read_text():
            click.echo(f"Completion for {shell} already present in: {target_file}")
            return

    with target_file.open("a") as f:
        f.write(script_file.read_text())

    click.echo(f"Completion for {shell} installed to: {target_file}")
