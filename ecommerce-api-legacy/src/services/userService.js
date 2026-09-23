const { NotFoundError } = require('../errors/AppError');

function createUserService({ db, userModel, enrollmentModel, paymentModel }) {
    return {
        // Remove o usuário junto com matrículas e pagamentos, sem deixar registros órfãos.
        async deleteUser(id) {
            return db.transaction(async () => {
                const user = await userModel.findById(id);
                if (!user) throw new NotFoundError('Usuário não encontrado');

                await paymentModel.deleteByUserId(id);
                await enrollmentModel.deleteByUserId(id);
                await userModel.deleteById(id);
            });
        },
    };
}

module.exports = { createUserService };
