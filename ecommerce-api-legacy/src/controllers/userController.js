const { parseUserId } = require('../validators/requestValidators');

function createUserController({ userService }) {
    return {
        async deleteUser(req, res) {
            await userService.deleteUser(parseUserId(req.params.id));
            res.send('Usuário deletado');
        },
    };
}

module.exports = { createUserController };
