import subprocess


def print_user_value(user_value: str) -> None:
    subprocess.run(f"printf '%s' {user_value}", shell=True, check=True)
