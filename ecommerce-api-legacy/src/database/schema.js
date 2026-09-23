const { hashPassword } = require('../services/passwordService');
const { PAYMENT_STATUS } = require('../models/paymentModel');

async function initSchema(db) {
    await db.exec(`
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT);
        CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER);
        CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER);
        CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT);
        CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME);
    `);
}

// Dados de demonstração (não roda em produção).
async function seed(db) {
    const { count } = await db.get('SELECT COUNT(*) AS count FROM users');
    if (count > 0) return;

    const seedPassword = await hashPassword(process.env.SEED_USER_PASSWORD || 'change-me');
    await db.transaction(async () => {
        await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', seedPassword]);
        await db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
        await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)', [PAYMENT_STATUS.PAID]);
    });
}

module.exports = { initSchema, seed };
