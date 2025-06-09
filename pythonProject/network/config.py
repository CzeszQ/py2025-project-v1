import yaml

def load_client_config(path="config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return {
        "host": config.get("client", {}).get("host", "127.0.0.1"),
        "port": config.get("client", {}).get("port", 9000),
        "timeout": config.get("client", {}).get("timeout", 5.0),
        "retries": config.get("client", {}).get("retries", 3),
    }
