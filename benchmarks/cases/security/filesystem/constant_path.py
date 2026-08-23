def read_site_config() -> str:
    with open("sites/common_site_config.json") as handle:
        return handle.read()
