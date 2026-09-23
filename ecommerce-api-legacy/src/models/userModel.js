function createUserModel(db) {
    return {
        findById: (id) => db.get('SELECT id, name, email FROM users WHERE id = ?', [id]),

        findByEmail: (email) => db.get('SELECT id, name, email FROM users WHERE email = ?', [email]),

        async create({ name, email, passwordHash }) {
            const { lastID } = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
            return lastID;
        },

        async deleteById(id) {
            const { changes } = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return changes > 0;
        },
    };
}

module.exports = { createUserModel };
