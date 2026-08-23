def read_requested_file(user_path: str) -> str:
    with open(user_path) as handle:
        return handle.read()
