const express = require('express');
const asyncHandler = require('../middlewares/asyncHandler');

function createRoutes({ checkoutController, reportController, userController }) {
    const router = express.Router();

    router.post('/checkout', asyncHandler(checkoutController.checkout));
    router.get('/admin/financial-report', asyncHandler(reportController.financialReport));
    router.delete('/users/:id', asyncHandler(userController.deleteUser));

    return router;
}

module.exports = { createRoutes };
