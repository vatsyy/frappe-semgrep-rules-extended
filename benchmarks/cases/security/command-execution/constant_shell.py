import subprocess


def show_status() -> None:
    subprocess.run("git status --short", shell=True, check=True)
