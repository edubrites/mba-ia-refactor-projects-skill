import logging
import os
import secrets

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


APP_ENV = os.environ.get("APP_ENV", "development")
IS_PRODUCTION = APP_ENV == "production"

APP_VERSION = "1.0"

DEBUG = _env_bool("DEBUG", default=False)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY não configurada (defina a variável de ambiente)")
    SECRET_KEY = secrets.token_hex(32)
    logger.warning("SECRET_KEY não definida; usando chave aleatória temporária (apenas dev)")

# Validade (segundos) do token devolvido por POST /login.
TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", str(24 * 60 * 60)))

# Envio de e-mail fica desligado por padrão: sem isso, notificações só são registradas em log.
EMAIL_ENABLED = _env_bool("EMAIL_ENABLED", default=False)
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
if EMAIL_ENABLED and not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
    raise RuntimeError("EMAIL_ENABLED=true exige SMTP_HOST, SMTP_USER e SMTP_PASSWORD definidos")
