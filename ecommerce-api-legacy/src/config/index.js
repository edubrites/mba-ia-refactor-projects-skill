const nodeEnv = process.env.NODE_ENV || 'development';

function required(name) {
    const value = process.env[name];
    if (!value && nodeEnv === 'production') {
        throw new Error(`Variável de ambiente ${name} não configurada`);
    }
    return value || null;
}

const config = {
    nodeEnv,
    port: Number(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: required('PAYMENT_GATEWAY_KEY'),
};

module.exports = config;
