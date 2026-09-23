// Encaminha rejeições de handlers async para o error handler (Express 4 não faz isso sozinho).
const asyncHandler = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);

module.exports = asyncHandler;
