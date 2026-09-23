const { PAYMENT_STATUS } = require('../models/paymentModel');

// Gateway simulado: apenas cartões iniciados em "4" (bandeira Visa) são aprovados.
const APPROVED_CARD_PREFIX = '4';

function maskCard(cardNumber) {
    return `****${cardNumber.slice(-4)}`;
}

// gatewayKey fica encapsulada aqui para a integração real; nunca é logada.
function createPaymentService({ logger, gatewayKey }) {
    return {
        charge({ cardNumber, amount }) {
            logger.info('Processando pagamento', { card: maskCard(cardNumber), amount, gatewayConfigured: Boolean(gatewayKey) });
            return cardNumber.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        },
    };
}

module.exports = { createPaymentService, maskCard };
