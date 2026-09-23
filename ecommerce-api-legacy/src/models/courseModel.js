function createCourseModel(db) {
    return {
        findActiveById: (id) => db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]),

        // Uma linha por matrícula (ou uma linha com campos nulos para curso sem matrículas).
        listEnrollmentFinancials: () => db.all(`
            SELECT c.id AS course_id, c.title AS course_title,
                   e.id AS enrollment_id, u.name AS student_name,
                   p.amount AS payment_amount, p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.id = (
                SELECT MIN(p2.id) FROM payments p2 WHERE p2.enrollment_id = e.id
            )
            ORDER BY c.id, e.id
        `),
    };
}

module.exports = { createCourseModel };
