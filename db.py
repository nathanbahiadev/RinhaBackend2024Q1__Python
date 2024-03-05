from psycopg_pool import AsyncConnectionPool
from modelos import Cliente, Transacao, Extrato, Saldo, ClienteNaoCadastradoException


class Db:
    def __init__(self):
        self.pool = AsyncConnectionPool(
            conninfo='host=localhost port=5432 dbname=mydatabase user=myuser password=mypassword',
            min_size=5,
            max_size=75,
            open=False,
        )
    
    async def consulta_cliente(self, id_cliente: int) -> Cliente:
        query1 = "SELECT ID, ACCOUNT_LIMIT, BALANCE FROM CLIENTS WHERE ID = {};"

        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query1.format(id_cliente))
                if not (row := await cursor.fetchone()):
                    raise ClienteNaoCadastradoException
                
                return Cliente(
                    id=row[0], 
                    limite=row[1], 
                    saldo=row[2],
                )


    async def consulta_extrato(self, id_cliente: int) -> Extrato:
        query1 = "SELECT ACCOUNT_LIMIT, BALANCE FROM CLIENTS WHERE ID = {} FOR UPDATE;"
        query2 = "SELECT VALUE, TYPE, DESCRIPTION, CREATED_AT FROM TRANSACTIONS WHERE CLIENT_ID = {} ORDER BY ID DESC LIMIT 10;"

        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query1.format(id_cliente))
                if not (res1 := await cursor.fetchone()):
                    raise ClienteNaoCadastradoException
                
                extrato = Extrato(saldo=Saldo(
                    limite=res1[0], 
                    total=res1[1],
                ))

                await cursor.execute(query2.format(id_cliente))
                res2 = await cursor.fetchall()

                for transacao in res2:
                    extrato.ultimas_transacoes.append(Transacao(
                        valor=transacao[0],
                        tipo=transacao[1],
                        descricao=transacao[2],
                        realizada_em=transacao[3],
                    ))

                return extrato

    async def cadastrar_transacao(self, id_cliente: int, cliente: Cliente, transacao: Transacao) -> Cliente:
        query1 = "SELECT ACCOUNT_LIMIT, BALANCE FROM CLIENTS WHERE ID = {} FOR UPDATE;"
        query2 = "UPDATE CLIENTS SET BALANCE = {} WHERE ID = {};"
        query3 = "INSERT INTO TRANSACTIONS (VALUE, TYPE, DESCRIPTION, CLIENT_ID) VALUES ({}, '{}', '{}', {})"

        async with self.pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query1.format(id_cliente))
                await cursor.execute(query2.format(cliente.saldo, id_cliente))
                await cursor.execute(query3.format(transacao.valor, transacao.tipo, transacao.descricao, id_cliente))
                return cliente
