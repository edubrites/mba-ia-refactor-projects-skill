const { NotFoundError, PaymentDeniedError, ValidationError } = require('../errors/AppError');
const { PAYMENT_STATUS } = require('../models/paymentModel');
const { hashPassword } = require('./passwordService');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService }) {
    async function resolveUserId({ name, email, password }) {
        const existing = await userModel.findByEmail(email);
        if (existing) return existing.id;

        if (!password) throw new ValidationError();
        const passwordHash = await hashPassword(password);
        return userModel.create({ name, email, passwordHash });
    }

    return {
        async checkout({ name, email, password, courseId, cardNumber }) {
            return db.transaction(async () => {
                const course = await courseModel.findActiveById(courseId);
                if (!course) throw new NotFoundError('Curso não encontrado');

                // Todas as validações e a criação do usuário acontecem antes da cobrança;
                // se o pagamento for recusado, a transação desfaz o usuário recém-criado.
                const userId = await resolveUserId({ name, email, password });

                const status = paymentService.charge({ cardNumber, amount: course.price });
                if (status !== PAYMENT_STATUS.PAID) throw new PaymentDeniedError();

                const enrollmentId = await enrollmentModel.create({ userId, courseId });
                await paymentModel.create({ enrollmentId, amount: course.price, status });
                await auditLogModel.record(`Checkout curso ${courseId} por ${userId}`);
                return { enrollmentId };
            });
        },
    };
}

module.exports = { createCheckoutService };
