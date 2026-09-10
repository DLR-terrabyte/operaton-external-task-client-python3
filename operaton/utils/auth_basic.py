import base64
import copy
from pydantic import BaseModel

DEFAULT_SENSITIVE_KEYS = {
    "password", "secret", "client_secret", "token",
    "access_token", "refresh_token", "api_key", "private_key",
}

def obfuscate_secrets(config: dict, sensitive_keys: set = None, extra_key: str = None) -> dict:
    """Obfuscate password value in config
    :param config:  config from ExternalTaskWorker or ExternalTaskClient
    :param sensitive_keys: optional custom list, replaces DEFAULT_SENSITIVE_KEYS
    :param extra_key: Optional additional key name; is always included in the check
    :returns: _config with obfuscated password
    """
    keys = set(k.lower() for k in (sensitive_keys or DEFAULT_SENSITIVE_KEYS))
    if extra_key:
        keys.add(extra_key.lower())

    _config = copy.deepcopy(config)
    _redact(_config, keys)
    return _config


def _redact(node, sensitive_keys):
    """Redact sensitive_keys from config
    “Secret” must be stored as a key-value pair in the configuration.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                _redact(value, sensitive_keys)
            elif key.lower() in sensitive_keys:
                node[key] = "***"
    elif isinstance(node, list):
        for item in node:
            _redact(item, sensitive_keys)


class AuthBasic(BaseModel):
    username: str
    password: str
    token: str = ""

    def __init__(self, **data):
        super().__init__(**data)
        token = f"{self.username}:{self.password}"
        bytemsg = base64.b64encode(token.encode('utf-8'))
        tokenb64 = str(bytemsg, "utf-8")
        self.token = f"Basic {tokenb64}"
