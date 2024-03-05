from sanic import Sanic
from sanic.response import json, empty

from modelos import Transacao, Cliente, Extrato, ClienteNaoCadastradoException, LimiteInsuficienteException
from db import Db

app = Sanic(__name__)
db = Db()

@app.listener('before_server_start')
async def setup_db_pool(*args):
    await db.pool.open()

@app.post("/clientes/<id_cliente>/transacoes")
async def transacoes(request, id_cliente: int):
    try:
        transacao: Transacao = Transacao.model_validate_json(request.body)
        cliente: Cliente = await db.consulta_cliente(id_cliente)
        cliente.add_transacao(transacao)
        cliente = await db.cadastrar_transacao(id_cliente, cliente, transacao)
        return json(cliente.model_dump(), default=str)
    
    except ClienteNaoCadastradoException:
        return empty(status=404)

    except (
        ValueError,
        LimiteInsuficienteException
    ):
        return empty(status=422)
    
    except Exception as exc:
        print(exc)
        return empty(status=500)


@app.get("/clientes/<id_cliente>/extrato")
async def extratos(request, id_cliente: int):
    try:
        extrato: Extrato = await db.consulta_extrato(id_cliente)
        return json(extrato.model_dump(), default=str)
    
    except ClienteNaoCadastradoException:
        return empty(status=404)

    except ValueError:
        return empty(status=422)
    
    except Exception as exc:
        print(exc)
        return empty(status=500)
