from flask import Blueprint, jsonify, request


def _json_body():
    return request.get_json(silent=True)


def _responder(resultado):
    body, status = resultado
    return jsonify(body), status


def produtos_blueprint(controller):
    bp = Blueprint("produtos", __name__)
    bp.add_url_rule("/produtos", "listar_produtos", lambda: _responder(controller.listar()), methods=["GET"])
    bp.add_url_rule(
        "/produtos/busca",
        "buscar_produtos",
        lambda: _responder(controller.buscar(
            request.args.get("q", ""),
            request.args.get("categoria"),
            request.args.get("preco_min"),
            request.args.get("preco_max"),
        )),
        methods=["GET"],
    )
    bp.add_url_rule("/produtos/<int:id>", "buscar_produto", lambda id: _responder(controller.buscar_por_id(id)), methods=["GET"])
    bp.add_url_rule("/produtos", "criar_produto", lambda: _responder(controller.criar(_json_body())), methods=["POST"])
    bp.add_url_rule("/produtos/<int:id>", "atualizar_produto", lambda id: _responder(controller.atualizar(id, _json_body())), methods=["PUT"])
    bp.add_url_rule("/produtos/<int:id>", "deletar_produto", lambda id: _responder(controller.deletar(id)), methods=["DELETE"])
    return bp


def usuarios_blueprint(controller):
    bp = Blueprint("usuarios", __name__)
    bp.add_url_rule("/usuarios", "listar_usuarios", lambda: _responder(controller.listar()), methods=["GET"])
    bp.add_url_rule("/usuarios/<int:id>", "buscar_usuario", lambda id: _responder(controller.buscar_por_id(id)), methods=["GET"])
    bp.add_url_rule("/usuarios", "criar_usuario", lambda: _responder(controller.criar(_json_body())), methods=["POST"])
    bp.add_url_rule("/login", "login", lambda: _responder(controller.login(_json_body())), methods=["POST"])
    return bp


def pedidos_blueprint(controller):
    bp = Blueprint("pedidos", __name__)
    bp.add_url_rule("/pedidos", "criar_pedido", lambda: _responder(controller.criar(_json_body())), methods=["POST"])
    bp.add_url_rule("/pedidos", "listar_todos_pedidos", lambda: _responder(controller.listar_todos()), methods=["GET"])
    bp.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        "listar_pedidos_usuario",
        lambda usuario_id: _responder(controller.listar_por_usuario(usuario_id)),
        methods=["GET"],
    )
    bp.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        "atualizar_status_pedido",
        lambda pedido_id: _responder(controller.atualizar_status(pedido_id, _json_body())),
        methods=["PUT"],
    )
    return bp


def relatorios_blueprint(controller):
    bp = Blueprint("relatorios", __name__)
    bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", lambda: _responder(controller.vendas()), methods=["GET"])
    return bp


def sistema_blueprint(controller, admin_reset_enabled=False):
    bp = Blueprint("sistema", __name__)
    bp.add_url_rule("/", "index", lambda: _responder(controller.index()), methods=["GET"])
    bp.add_url_rule("/health", "health_check", lambda: _responder(controller.health()), methods=["GET"])
    # /admin/query (SQL arbitrário) foi removido. O reset só existe quando habilitado por config.
    if admin_reset_enabled:
        bp.add_url_rule(
            "/admin/reset-db",
            "reset_database",
            lambda: _responder(controller.reset_db(request.headers.get("X-Admin-Token"))),
            methods=["POST"],
        )
    return bp


def register_routes(app, controllers, admin_reset_enabled=False):
    app.register_blueprint(produtos_blueprint(controllers["produtos"]))
    app.register_blueprint(usuarios_blueprint(controllers["usuarios"]))
    app.register_blueprint(pedidos_blueprint(controllers["pedidos"]))
    app.register_blueprint(relatorios_blueprint(controllers["relatorios"]))
    app.register_blueprint(sistema_blueprint(controllers["sistema"], admin_reset_enabled))
