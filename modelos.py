from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, PositiveInt, constr, Field


class ClienteNaoCadastradoException(Exception):
    ...


class LimiteInsuficienteException(Exception):
    ...


class TipoTransacaoEnum(str, Enum):
    c = 'c'
    d = 'd'


class Transacao(BaseModel):
    valor: PositiveInt
    descricao: constr(min_length=1, max_length=10) # type: ignore
    tipo: TipoTransacaoEnum
    realizada_em: datetime | None = datetime.now()


class Cliente(BaseModel):
    limite: PositiveInt
    saldo: int

    def add_transacao(self, transacao: Transacao):
        if transacao.tipo == "c":
            self.saldo += transacao.valor
            return
            
        
        novo_saldo = self.saldo - transacao.valor
        if novo_saldo < self.limite *-1:
            raise LimiteInsuficienteException

        self.saldo = novo_saldo 


class Saldo(BaseModel):
    total: int
    limite: int
    data_extrato: datetime | None = datetime.now()


class Extrato(BaseModel):
    saldo: Saldo
    ultimas_transacoes: List[Transacao] = Field(default_factory=list)
