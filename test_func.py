from random import randint, choice
import pytest, requests


def obter_id_cliente():
    return randint(1, 5)


def obter_valor_transacao():
     return randint(1, 10000)


def obter_tipo_transacao():
     return choice([
        ("c", "crédito"), 
        ("d", "débito"),
        ("d", "débito"),
        ("d", "débito"),
    ])


def cadastro_transacao():
    valor = obter_valor_transacao()
    tipo, descricao = obter_tipo_transacao()

    response = requests.post(f"http://localhost:9999/clientes/{obter_id_cliente()}/transacoes", json={
        "valor": valor,
        "tipo": tipo,
        "descricao": descricao
    })

    assert response.status_code in (200, 422)
    if response.status_code == 200:
        assert response.json()["saldo"] >= (response.json()["limite"] * -1)


def consulta_extrato():
    response = requests.get(f"http://localhost:9999/clientes/{obter_id_cliente()}/extrato")

    assert response.status_code == 200
    assert response.json()["saldo"]["total"] >= (response.json()["saldo"]["limite"] * -1)


@pytest.mark.parametrize('n', range(10_000))
def test_limite_excedido_worker1(n):
     cadastro_transacao()
     consulta_extrato()


@pytest.mark.parametrize('n', range(10_000))
def test_limite_excedido_worker2(n):
     cadastro_transacao()
     consulta_extrato()


@pytest.mark.parametrize('n', range(10_000))
def test_limite_excedido_worker3(n):
     cadastro_transacao()
     consulta_extrato()


@pytest.mark.parametrize('n', range(10_000))
def test_limite_excedido_worker4(n):
     cadastro_transacao()
     consulta_extrato()
