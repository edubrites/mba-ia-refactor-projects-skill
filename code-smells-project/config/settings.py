import logging
import os
import secrets

logger = logging.getLogger(__name__)


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


APP_ENV = os.environ.get("APP_ENV", "development")
IS_PRODUCTION = APP_ENV == "production"

APP_VERSION = "1.0.0"

DEBUG = _env_bool("DEBUG", default=False)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
DB_PATH = os.environ.get("DB_PATH", "loja.db")

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY não configurada (defina a variável de ambiente)")
    SECRET_KEY = secrets.token_hex(32)
    logger.warning("SECRET_KEY não definida; usando chave aleatória temporária (apenas dev)")

# Senha aplicada aos usuários de exemplo criados no primeiro boot.
# Sem a variável, uma senha aleatória é gerada e exibida no log uma única vez.
SEED_USER_PASSWORD = os.environ.get("SEED_USER_PASSWORD")

# Endpoint /admin/reset-db só é registrado quando explicitamente habilitado
# e exige o header X-Admin-Token igual a ADMIN_TOKEN.
ADMIN_RESET_ENABLED = _env_bool("ADMIN_RESET_ENABLED", default=False)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
if ADMIN_RESET_ENABLED and not ADMIN_TOKEN:
    raise RuntimeError("ADMIN_RESET_ENABLED=true exige ADMIN_TOKEN definido")
