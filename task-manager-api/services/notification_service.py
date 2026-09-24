import logging
import smtplib
from collections import deque
from dataclasses import dataclass

from utils.helpers import utcnow

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailConfig:
    enabled: bool = False
    host: str = ''
    port: int = 587
    user: str = ''
    password: str = ''


class NotificationService:
    def __init__(self, email_config, smtp_factory=smtplib.SMTP, max_history=1000):
        self.email_config = email_config
        self.smtp_factory = smtp_factory
        # Histórico em memória limitado, para não crescer sem fim enquanto o processo roda.
        self.notifications = deque(maxlen=max_history)

    def send_email(self, to, subject, body):
        if not self.email_config.enabled:
            logger.info("Envio de e-mail desabilitado; notificação para %s não enviada: %s", to, subject)
            return False
        cfg = self.email_config
        try:
            with self.smtp_factory(cfg.host, cfg.port) as server:
                server.starttls()
                server.login(cfg.user, cfg.password)
                server.sendmail(cfg.user, to, f"Subject: {subject}\n\n{body}")
            logger.info("E-mail enviado para %s", to)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception("Falha ao enviar e-mail para %s", to)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
                f"Prioridade: {task.priority}\nStatus: {task.status}")
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f"Task atrasada: {task.title}"
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
