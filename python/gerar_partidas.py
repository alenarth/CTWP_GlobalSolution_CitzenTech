"""Gera partidas simuladas do Radar da Desinformação e envia ao ThingSpeak.

Continua os totais acumulados a partir do último envio real do ESP32, no mesmo
formato dos campos do canal. Cada envio sai marcado com status "simulado".
Uso: python gerar_partidas.py
"""

import random
import time

import requests

API = "https://api.thingspeak.com"
CHAVE_GERAL = "0PQ5TKYRWMB1AWXD"
CHAVE_AREAS = "9HHVW5Z4DFT844MD"
ID_CANAL_GERAL = "3568353"
ID_CANAL_AREAS = "3568360"
READ_KEY_GERAL = "3PFL07WEV3A2OL27"
READ_KEY_AREAS = "0XOXQP8QUDMAEY5S"

PERGUNTAS_POR_PARTIDA = 20
PERGUNTAS_POR_CARGO = 4
INTERVALO_S = 16
STATUS = "simulado (gerar_partidas.py)"

# Taxa de erro (%) e leitura do LDR de cada partida simulada.
PARTIDAS = [
    (35, 1200), (30, 900), (45, 1500), (40, 2600), (25, 800), (50, 1800),
    (60, 3000), (75, 3600), (80, 3900), (55, 2200), (40, 1400), (35, 1000),
    (30, 900), (45, 2000), (55, 2600), (65, 3300), (80, 3800),
]


def ultimo_registro(canal: str, read_key: str) -> dict:
    """Lê a última entrada de um canal."""
    resposta = requests.get(f"{API}/channels/{canal}/feeds/last.json",
                            params={"api_key": read_key}, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def numero(registro: dict, campo: str) -> int:
    """Lê um campo numérico, tratando vazio como zero."""
    try:
        return int(float(registro.get(campo) or 0))
    except ValueError:
        return 0


def enviar(chave: str, campos: list) -> bool:
    """Envia um registro ao canal. Tenta de novo uma vez se o ThingSpeak recusar."""
    parametros = {"api_key": chave, "status": STATUS}
    parametros.update({f"field{i}": v for i, v in enumerate(campos, 1)})

    for _ in range(2):
        resposta = requests.get(f"{API}/update", params=parametros, timeout=10)
        if resposta.text.strip().isdigit() and int(resposta.text.strip()) > 0:
            return True
        time.sleep(INTERVALO_S)

    return False


def distribuir_acertos(acertos: int) -> list:
    """Distribui os acertos da partida entre os 5 cargos (no máximo 4 por cargo)."""
    por_cargo = [0] * 5
    vagas = [c for c in range(5) for _ in range(PERGUNTAS_POR_CARGO)]
    for cargo in random.sample(vagas, acertos):
        por_cargo[cargo] += 1
    return por_cargo


def main() -> None:
    """Continua os contadores do canal e envia as partidas simuladas."""
    random.seed(2026)
    geral = ultimo_registro(ID_CANAL_GERAL, READ_KEY_GERAL)
    areas = ultimo_registro(ID_CANAL_AREAS, READ_KEY_AREAS)

    presencas, sessoes = numero(geral, "field1"), numero(geral, "field2")
    respostas, acertos, erros = numero(geral, "field3"), numero(geral, "field4"), numero(geral, "field5")
    por_cargo = [numero(areas, f"field{i}") for i in range(1, 6)]
    print(f"Último envio no canal: entry {geral.get('entry_id')} · {sessoes} partidas · {respostas} respostas")

    if numero(geral, "entry_id") >= 21:
        print("O canal já tem 21 envios ou mais. Nenhuma partida nova foi gerada.")
        return

    for indice, (taxa_erro, luz) in enumerate(PARTIDAS, 1):
        erros_partida = round(PERGUNTAS_POR_PARTIDA * taxa_erro / 100)
        acertos_partida = PERGUNTAS_POR_PARTIDA - erros_partida

        presencas += 1
        sessoes += 1
        respostas += PERGUNTAS_POR_PARTIDA
        acertos += acertos_partida
        erros += erros_partida
        por_cargo = [a + b for a, b in zip(por_cargo, distribuir_acertos(acertos_partida))]
        aproveitamento = round(acertos / respostas * 100, 2)

        ok_geral = enviar(CHAVE_GERAL, [presencas, sessoes, respostas, acertos, erros,
                                        aproveitamento, luz, 1 if luz > 2000 else 0])
        ok_areas = enviar(CHAVE_AREAS, por_cargo)
        print(f"Partida {indice}/{len(PARTIDAS)}: erro {taxa_erro}% · luz {luz} · "
              f"geral {'ok' if ok_geral else 'FALHOU'} · cargos {'ok' if ok_areas else 'FALHOU'}")

        if indice < len(PARTIDAS):
            time.sleep(INTERVALO_S)

    print("Pronto.")


if __name__ == "__main__":
    main()
