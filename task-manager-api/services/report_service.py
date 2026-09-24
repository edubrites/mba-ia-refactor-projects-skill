from datetime import timedelta

from models.category import Category
from models.constants import (
    HIGH_PRIORITY_THRESHOLD, PRIORITY_LABELS, RECENT_ACTIVITY_DAYS, STATUS_CANCELLED, STATUS_DONE,
    STATUS_IN_PROGRESS, STATUS_PENDING, VALID_STATUSES,
)
from models.task import Task
from models.user import User
from utils.helpers import calculate_percentage, utcnow


class ReportService:
    """Estatísticas que cruzam tasks, usuários e categorias, calculadas com queries agregadas."""

    def task_stats(self):
        total = Task.count()
        by_status = Task.count_by_status()
        return {
            'total': total,
            **{status: by_status.get(status, 0) for status in VALID_STATUSES},
            'overdue': Task.count_overdue(utcnow()),
            'completion_rate': calculate_percentage(by_status.get(STATUS_DONE, 0), total),
        }

    def summary(self):
        now = utcnow()
        since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
        by_status = Task.count_by_status()
        by_priority = Task.count_by_priority()
        overdue = Task.list_overdue(now)
        per_user = Task.counts_per_user()

        user_stats = []
        for user in User.list_all():
            total, completed = per_user.get(user.id, (0, 0))
            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': calculate_percentage(completed, total),
            })

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': Task.count(),
                'total_users': User.count(),
                'total_categories': Category.count(),
            },
            'tasks_by_status': {status: by_status.get(status, 0) for status in VALID_STATUSES},
            'tasks_by_priority': {label: by_priority.get(p, 0) for p, label in PRIORITY_LABELS.items()},
            'overdue': {
                'count': len(overdue),
                'tasks': [{
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                } for task in overdue],
            },
            'recent_activity': {
                'tasks_created_last_7_days': Task.count_created_since(since),
                'tasks_completed_last_7_days': Task.count_done_since(since),
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user):
        tasks = Task.list_by_user(user.id)
        now = utcnow()
        counts = {status: 0 for status in (STATUS_DONE, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_CANCELLED)}
        for task in tasks:
            if task.status in counts:
                counts[task.status] += 1

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': len(tasks),
                **counts,
                'overdue': sum(1 for task in tasks if task.is_overdue(now)),
                'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_THRESHOLD),
                'completion_rate': calculate_percentage(counts[STATUS_DONE], len(tasks)),
            },
        }
