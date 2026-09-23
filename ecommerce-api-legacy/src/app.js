const express = require('express');
const config = require('./config');
const logger = require('./config/logger');
const { createDatabase } = require('./config/database');
const { initSchema, seed } = require('./database/schema');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createPaymentService } = require('./services/paymentService');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createRoutes } = require('./routes');
const { createErrorHandler } = require('./middlewares/errorHandler');

async function bootstrap() {
    const db = createDatabase(config.dbPath);
    await initSchema(db);
    if (config.nodeEnv !== 'production') await seed(db);

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);

    const paymentService = createPaymentService({ logger, gatewayKey: config.paymentGatewayKey });
    const checkoutService = createCheckoutService({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService,
    });
    const reportService = createReportService({ courseModel });
    const userService = createUserService({ db, userModel, enrollmentModel, paymentModel });

    const app = express();
    app.use(express.json());
    app.use('/api', createRoutes({
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
    }));
    app.use(createErrorHandler({ logger }));

    app.listen(config.port, () => {
        logger.info(`LMS API rodando na porta ${config.port}`);
    });
}

bootstrap().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', { error: err.message, stack: err.stack });
    process.exit(1);
});
