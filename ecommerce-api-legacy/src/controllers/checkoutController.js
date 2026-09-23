const { parseCheckoutRequest } = require('../validators/requestValidators');

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const input = parseCheckoutRequest(req.body);
            const { enrollmentId } = await checkoutService.checkout(input);
            res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
