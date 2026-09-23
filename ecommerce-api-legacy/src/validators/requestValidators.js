const { ValidationError } = require('../errors/AppError');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{13,19}$/;

function isNonEmptyString(value) {
    return typeof value === 'string' && value.trim().length > 0;
}

// Mantém o contrato público (usr, eml, pwd, c_id, card) e devolve nomes de domínio.
function parseCheckoutRequest(body = {}) {
    const { usr, eml, c_id: courseId } = body;
    // pwd vazio/nulo equivale a ausente; só é exigido para usuário novo (regra no service).
    const pwd = body.pwd === null || body.pwd === '' ? undefined : body.pwd;
    const card = typeof body.card === 'string' ? body.card.replace(/[\s-]/g, '') : body.card;
    const numericCourseId = Number(courseId);

    const valid = isNonEmptyString(usr)
        && isNonEmptyString(eml) && EMAIL_PATTERN.test(eml)
        && Number.isInteger(numericCourseId) && numericCourseId > 0
        && typeof card === 'string' && CARD_PATTERN.test(card)
        && (pwd === undefined || isNonEmptyString(pwd));

    if (!valid) throw new ValidationError();

    return {
        name: usr.trim(),
        email: eml.trim(),
        password: pwd,
        courseId: numericCourseId,
        cardNumber: card,
    };
}

function parseUserId(rawId) {
    const id = Number(rawId);
    if (!Number.isInteger(id) || id <= 0) throw new ValidationError();
    return id;
}

module.exports = { parseCheckoutRequest, parseUserId };
