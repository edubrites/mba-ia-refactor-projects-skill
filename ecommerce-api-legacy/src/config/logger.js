function write(level, message, context) {
    const entry = { ...context, level, time: new Date().toISOString(), message };
    const line = JSON.stringify(entry);
    if (level === 'error') console.error(line);
    else console.log(line);
}

module.exports = {
    info: (message, context = {}) => write('info', message, context),
    warn: (message, context = {}) => write('warn', message, context),
    error: (message, context = {}) => write('error', message, context),
};
