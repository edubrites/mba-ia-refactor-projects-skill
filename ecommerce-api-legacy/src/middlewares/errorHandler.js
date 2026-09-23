const { AppError } = require('../errors/AppError');

function createErrorHandler({ logger }) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (res.headersSent) return next(err);
        if (err instanceof AppError) {
            return res.status(err.statusCode).send(err.message);
        }
        // Erros do body-parser (JSON inválido, payload grande, charset) já trazem status 4xx.
        if (err.status >= 400 && err.status < 500) {
            return res.status(err.status).send('Bad Request');
        }
        logger.error('Erro não tratado', {
            method: req.method, path: req.path, error: err.message, stack: err.stack, rollbackError: err.rollbackError?.message,
        });
        return res.status(500).send('Erro interno');
    };
}

module.exports = { createErrorHandler };
