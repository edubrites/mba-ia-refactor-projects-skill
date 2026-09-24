"""Validação de dados de entrada, compartilhada entre create (partial=False) e update (partial=True)."""
import re
from datetime import datetime

from models.constants import (
    DATE_FORMAT, DEFAULT_COLOR, DEFAULT_PRIORITY, MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH,
    MIN_PRIORITY, MIN_TITLE_LENGTH, ROLE_USER, STATUS_PENDING, VALID_ROLES, VALID_STATUSES,
)
from models.errors import ValidationError

EMAIL_RE = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')
COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def require_body(data, allow_empty=False):
    if not isinstance(data, dict) or (not data and not allow_empty):
        raise ValidationError('Dados inválidos')
    return data


def _as_int(value):
    """Aceita int, float inteiro (2.0) e string numérica ("1"), como o ORM já aceitava; senão None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _validate_text(value, message):
    if value is not None and not isinstance(value, str):
        raise ValidationError(message)
    return value


def parse_int_param(value, name):
    if value in (None, ''):
        return None
    try:
        return int(value)
    except ValueError:
        raise ValidationError(f'Parâmetro {name} inválido')


def _validate_title(title):
    if not isinstance(title, str):
        raise ValidationError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return title


def _validate_priority(priority):
    value = None if isinstance(priority, str) else _as_int(priority)
    if value is None or not MIN_PRIORITY <= value <= MAX_PRIORITY:
        raise ValidationError(f'Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}')
    return value


def _validate_optional_id(value, message):
    if value is None:
        return None
    parsed = _as_int(value)
    if parsed is None:
        raise ValidationError(message)
    return parsed


def _parse_due_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except (TypeError, ValueError):
        raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')


def _normalize_tags(tags):
    if isinstance(tags, list):
        if not all(isinstance(t, str) for t in tags):
            raise ValidationError('Tags inválidas')
        return ','.join(tags)
    if tags is None or isinstance(tags, str):
        return tags
    raise ValidationError('Tags inválidas')


def validate_task(data, partial=False):
    """Devolve só os campos presentes (partial) ou todos com defaults (create), já normalizados."""
    data = require_body(data)
    result = {}

    if 'title' in data or not partial:
        if not partial and not data.get('title'):
            raise ValidationError('Título é obrigatório')
        result['title'] = _validate_title(data.get('title'))

    if 'description' in data or not partial:
        result['description'] = _validate_text(data.get('description', ''), 'Descrição inválida')

    if 'status' in data or not partial:
        status = data.get('status', STATUS_PENDING)
        if status not in VALID_STATUSES:
            raise ValidationError('Status inválido')
        result['status'] = status

    if 'priority' in data or not partial:
        result['priority'] = _validate_priority(data.get('priority', DEFAULT_PRIORITY))

    if 'user_id' in data or not partial:
        result['user_id'] = _validate_optional_id(data.get('user_id') or None, 'Usuário inválido')

    if 'category_id' in data or not partial:
        result['category_id'] = _validate_optional_id(data.get('category_id') or None, 'Categoria inválida')

    if 'due_date' in data or not partial:
        result['due_date'] = _parse_due_date(data.get('due_date'))

    if 'tags' in data or not partial:
        tags = _normalize_tags(data.get('tags'))
        result['tags'] = tags if (tags or partial) else None

    return result


def validate_user(data, partial=False):
    data = require_body(data)
    result = {}

    if 'name' in data or not partial:
        name = data.get('name')
        if not name or not isinstance(name, str):
            raise ValidationError('Nome é obrigatório')
        result['name'] = name

    if 'email' in data or not partial:
        email = data.get('email')
        if not partial and not email:
            raise ValidationError('Email é obrigatório')
        if not isinstance(email, str) or not EMAIL_RE.match(email):
            raise ValidationError('Email inválido')
        result['email'] = email

    if 'password' in data or not partial:
        password = data.get('password')
        if not partial and not password:
            raise ValidationError('Senha é obrigatória')
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
        result['password'] = password

    if 'role' in data or not partial:
        role = data.get('role', ROLE_USER)
        if role not in VALID_ROLES:
            raise ValidationError('Role inválido')
        result['role'] = role

    if partial and 'active' in data:
        if not isinstance(data['active'], bool):
            raise ValidationError('Campo active deve ser booleano')
        result['active'] = data['active']

    return result


def validate_category(data, partial=False):
    data = require_body(data, allow_empty=partial)
    result = {}

    if 'name' in data or not partial:
        name = data.get('name')
        if not name or not isinstance(name, str):
            raise ValidationError('Nome é obrigatório')
        result['name'] = name

    if 'description' in data or not partial:
        result['description'] = _validate_text(data.get('description', ''), 'Descrição inválida')

    if 'color' in data or not partial:
        color = data.get('color', DEFAULT_COLOR)
        if not isinstance(color, str) or not COLOR_RE.match(color):
            raise ValidationError('Cor inválida. Use o formato #RRGGBB')
        result['color'] = color

    return result
