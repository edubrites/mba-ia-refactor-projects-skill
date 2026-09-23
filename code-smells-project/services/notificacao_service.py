import logging

from models.constants import StatusPedido

logger = logging.getLogger(__name__)


class NotificacaoService:
    """Ponto único de side-effects de notificação (hoje só loga; trocar por e-mail/SMS/push reais)."""

    def notificar_pedido_criado(self, pedido_id, usuario_id):
        logger.info("EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
        logger.info("SMS: Seu pedido foi recebido!")
        logger.info("PUSH: Novo pedido recebido pelo sistema")

    def notificar_status_pedido(self, pedido_id, status):
        if status == StatusPedido.APROVADO:
            logger.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)
        elif status == StatusPedido.CANCELADO:
            logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
