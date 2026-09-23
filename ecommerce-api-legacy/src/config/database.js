const { AsyncLocalStorage } = require('async_hooks');
const sqlite3 = require('sqlite3');

// Adapta a API callback do driver sqlite3 para Promises (async/await).
function createDatabase(dbPath) {
    const conn = new sqlite3.Database(dbPath);
    const txContext = new AsyncLocalStorage();
    let queue = Promise.resolve();

    // Conexão única: toda operação fora de uma transação espera a transação aberta terminar,
    // evitando leitura suja e escrita "pegando carona" em transação alheia.
    const enqueue = (task) => {
        if (txContext.getStore()) return task();
        const result = queue.then(task);
        queue = result.catch(() => {});
        return result;
    };

    const rawRun = (sql, params) => new Promise((resolve, reject) => {
        conn.run(sql, params, function onRun(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
    const rawGet = (sql, params) => new Promise((resolve, reject) => {
        conn.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
    const rawAll = (sql, params) => new Promise((resolve, reject) => {
        conn.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
    const rawExec = (sql) => new Promise((resolve, reject) => {
        conn.exec(sql, (err) => (err ? reject(err) : resolve()));
    });

    const run = (sql, params = []) => enqueue(() => rawRun(sql, params));
    const get = (sql, params = []) => enqueue(() => rawGet(sql, params));
    const all = (sql, params = []) => enqueue(() => rawAll(sql, params));
    const exec = (sql) => enqueue(() => rawExec(sql));

    // Transação aninhada reaproveita a transação externa.
    const transaction = (work) => enqueue(() => {
        if (txContext.getStore()) return work();
        return txContext.run(true, async () => {
            await rawExec('BEGIN');
            try {
                const value = await work();
                await rawExec('COMMIT');
                return value;
            } catch (err) {
                try {
                    await rawExec('ROLLBACK');
                } catch (rollbackErr) {
                    err.rollbackError = rollbackErr;
                }
                throw err;
            }
        });
    });

    const close = () => new Promise((resolve, reject) => {
        conn.close((err) => (err ? reject(err) : resolve()));
    });

    return { run, get, all, exec, transaction, close };
}

module.exports = { createDatabase };
