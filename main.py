from sanic import Sanic
from sanic.response import json, empty
from psycopg_pool import AsyncConnectionPool
from pydantic import (BaseModel, PositiveInt, constr)


app = Sanic(__name__)

pool = AsyncConnectionPool(
    conninfo='host=localhost port=5432 dbname=mydatabase user=myuser password=mypassword',
    min_size=5,
    open=False
)    


@app.listener("before_server_start")
async def setup_db(*args):
    await pool.open()


class Transacao(BaseModel):
    valor: PositiveInt
    descricao: constr(min_length=1, max_length=10) # type: ignore
    tipo: constr(pattern="[c|d]") # type: ignore


@app.post("/clientes/<id_cliente>/transacoes")
async def transacoes(request, id_cliente: int):
    try:
        transacao: Transacao = Transacao.model_validate_json(request.body)                 

        async with pool.connection() as conn:
            try:
                cursor = await conn.execute(f"""
                    SELECT * 
                    FROM CREATE_TRANSACTION(
                        {id_cliente}, 
                        {transacao.valor}, 
                        '{transacao.tipo}', 
                        '{transacao.descricao}'
                    )
                """)
                res = await cursor.fetchone()
                return json({"saldo": res[0], "limite": res[1]})
            
            except Exception as exc:                
                if "CLIENT_NOT_FOUND" in str(exc):
                    return empty(status=404)
                return empty(status=422)

    except Exception as exc:
        print(exc)
        return empty(status=500)


@app.get("/clientes/<id_cliente>/extrato")
async def extratos(request, id_cliente: int):
    try:
        async with pool.connection() as conn:
            cursor = await conn.execute(f"SELECT * FROM GET_BALANCE({id_cliente})")
            res = await cursor.fetchall()

            if not res:
                return empty(status=404)
            
            return json({
                "saldo": {
                    "limite": res[0][0],
                    "total": res[0][1]
                },
                "ultimas_transacoes": [{
                    "valor": t[2],
                    "tipo": t[3],
                    "descricao": t[4],
                    "realizada_em": t[5],
                } for t in res if len(res) > 1]
            })

    except Exception as exc:
        print(exc)
        return empty(status=500)
