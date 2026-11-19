"""Radar da Desinformação · O Cérebro Conectado (Computational Thinking with Python)

Programa que busca no ThingSpeak as estatísticas que o ESP32 do Radar da
Desinformação publica depois de cada partida do quiz, cruza duas medidas num
índice de risco, percebe quando a situação está piorando e mantém o histórico.

Quem usa: o responsável pelo espaço onde fica a estação (biblioteca, escola ou
espaço comunitário). Ele quer saber se o público está errando muito sobre os
cargos políticos e se o espaço está bom para ler o quiz.

Projeto Demokratos · Global Solution 2026.2 · FIAP Engenharia de Software (RJ)
"""

import csv
import json
import os
from datetime import datetime, timedelta, timezone

import requests

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQ_BACKUP = os.path.join(PASTA, "backup.json")
ARQ_HISTORICO = os.path.join(PASTA, "historico.json")
ARQ_RELATORIO = os.path.join(PASTA, "relatorio.csv")

URL_FEEDS = "https://api.thingspeak.com/channels/{canal}/feeds.json"
TIMEOUT_SEGUNDOS = 10
FUSO_BRASILIA = timezone(timedelta(hours=-3))

# Canal geral do Radar: cada envio traz os totais acumulados de todas as partidas.
# field3 = respostas totais | field5 = erros totais | field7 = luz média do LDR
CANAL_GERAL = {"id": "3568353", "read_key": "3PFL07WEV3A2OL27", "resultados": 60}

# Canal por cargo: acertos acumulados de cada cargo (field1 a field5).
CANAL_CARGOS = {"id": "3568360", "read_key": "0XOXQP8QUDMAEY5S", "resultados": 1}
CARGOS = ["Prefeito", "Governador", "Vereador", "Deputado", "Presidente"]

CONFIG = {
    "medidas": {
        # % de respostas erradas na partida: quanto mais erros, maior o risco.
        "taxa_erro": {"nome": "Taxa de erro (%)", "minimo": 0.0, "maximo": 100.0, "peso": 0.7},
        # Leitura do LDR (0 a 4095). No Wokwi, quanto maior, mais escuro o espaço.
        "escuridao": {"nome": "Escuridão (LDR)", "minimo": 0.0, "maximo": 4095.0, "peso": 0.3},
    },
    "limite_atencao": 40.0,
    "limite_perigo": 70.0,
    "altas_para_piorar": 3,
    "avisos": {
        "NORMAL": "Bom conhecimento dos cargos. Indique a próxima trilha do Demokratos.",
        "ATENÇÃO": "Conhecimento mediano. Reforce a trilha 'Quem faz o quê' com o público.",
        "PERIGO": "Muitos erros sobre os cargos. Ofereça a trilha do zero e confira a luz do espaço.",
        "PIORANDO": "O risco subiu 3 vezes seguidas. Converse com o público antes que chegue a PERIGO.",
    },
}

FAIXAS = ["NORMAL", "ATENÇÃO", "PERIGO"]
CABECALHO_CSV = ["id", "horario", "taxa_erro", "escuridao", "risco", "faixa"]


# ---------------------------------------------------------------------------
# VALIDAÇÃO DA CONFIGURAÇÃO
# ---------------------------------------------------------------------------
def validar_config(config: dict) -> None:
    """Confere pesos e limites da configuração. Lança ValueError se algo estiver errado."""
    medidas = config["medidas"]
    soma_pesos = sum(medida["peso"] for medida in medidas.values())

    if abs(soma_pesos - 1.0) > 1e-9:
        raise ValueError(f"Os pesos precisam somar 1, mas somam {soma_pesos}.")

    for chave, medida in medidas.items():
        if medida["minimo"] >= medida["maximo"]:
            raise ValueError(f"Na medida '{chave}', o mínimo precisa ser menor que o máximo.")

    if not 0 < config["limite_atencao"] < config["limite_perigo"] <= 100:
        raise ValueError("Os limites das faixas precisam seguir 0 < ATENÇÃO < PERIGO <= 100.")


# ---------------------------------------------------------------------------
# ARQUIVOS JSON
# ---------------------------------------------------------------------------
def carregar_json(caminho: str, padrao):
    """Lê um arquivo JSON. Se ele não existir ou estiver corrompido, devolve 'padrao'."""
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return padrao


def salvar_json(caminho: str, dados) -> bool:
    """Grava 'dados' em JSON. Devolve True se conseguiu salvar."""
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        return True
    except OSError as erro:
        print(f"  Não foi possível salvar {os.path.basename(caminho)}: {erro}")
        return False


# ---------------------------------------------------------------------------
# API DO THINGSPEAK
# ---------------------------------------------------------------------------
def buscar_feeds(canal: dict) -> list:
    """Busca as últimas entradas de um canal do ThingSpeak.

    Lança requests.RequestException se a rede falhar ou o status não for 200,
    e ValueError se a resposta não for o JSON esperado.
    """
    url = URL_FEEDS.format(canal=canal["id"])
    parametros = {"api_key": canal["read_key"], "results": canal["resultados"]}

    resposta = requests.get(url, params=parametros, timeout=TIMEOUT_SEGUNDOS)

    if resposta.status_code != 200:
        raise requests.HTTPError(f"o ThingSpeak respondeu com status {resposta.status_code}")

    dados = resposta.json()

    if not isinstance(dados, dict) or not isinstance(dados.get("feeds"), list):
        raise ValueError("a resposta do ThingSpeak não tem a lista 'feeds'")

    return dados["feeds"]


def obter_feeds_com_plano_b(canal: dict) -> tuple:
    """Tenta a API; se der certo, atualiza o backup. Se falhar, usa o backup.json.

    Devolve (lista de entradas, origem), em que origem é 'ThingSpeak', 'backup' ou 'nenhuma'.
    """
    try:
        feeds = buscar_feeds(canal)
        salvar_json(ARQ_BACKUP, feeds)
        return feeds, "ThingSpeak"
    except (requests.RequestException, ValueError) as erro:
        print(f"  Sem acesso ao ThingSpeak ({erro}). Usando o backup.json.")

    backup = carregar_json(ARQ_BACKUP, [])

    if isinstance(backup, list) and backup:
        return backup, "backup"

    return [], "nenhuma"


# ---------------------------------------------------------------------------
# MODELO: DE ENTRADAS DO THINGSPEAK PARA LEITURAS
# ---------------------------------------------------------------------------
def para_numero(valor) -> float | None:
    """Converte um campo do ThingSpeak em número. Devolve None se vier vazio ou inválido."""
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def formatar_horario(created_at: str) -> str:
    """Converte o horário UTC do ThingSpeak em 'AAAA-MM-DD HH:MM' no horário de Brasília."""
    try:
        instante = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return instante.astimezone(FUSO_BRASILIA).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return "sem horário"


def calcular_nivel(valor: float, minimo: float, maximo: float) -> float:
    """Normaliza um valor para a escala de 0 a 100, limitando os extremos."""
    nivel = (valor - minimo) / (maximo - minimo) * 100
    return max(0.0, min(100.0, nivel))


def calcular_risco(medidas: dict, config: dict) -> float:
    """Índice de risco = soma de peso x nível de cada medida (resultado de 0 a 100)."""
    risco = 0.0

    for chave, regra in config["medidas"].items():
        nivel = calcular_nivel(medidas[chave], regra["minimo"], regra["maximo"])
        risco += regra["peso"] * nivel

    return round(risco, 1)


def classificar_faixa(risco: float, config: dict) -> str:
    """Define a faixa: NORMAL abaixo de 40, ATENÇÃO de 40 a 70 e PERIGO a partir de 70."""
    if risco >= config["limite_perigo"]:
        return "PERIGO"
    if risco >= config["limite_atencao"]:
        return "ATENÇÃO"
    return "NORMAL"


def extrair_medidas(anterior: dict, atual: dict) -> dict | None:
    """Calcula as medidas de uma partida a partir de dois envios seguidos.

    O ESP32 envia totais acumulados, então a partida é a diferença entre eles.
    Devolve None se os dados não formarem uma partida válida.
    """
    respostas_antes = para_numero(anterior.get("field3"))
    respostas_agora = para_numero(atual.get("field3"))
    erros_antes = para_numero(anterior.get("field5"))
    erros_agora = para_numero(atual.get("field5"))
    escuridao = para_numero(atual.get("field7"))

    if None in (respostas_antes, respostas_agora, erros_antes, erros_agora, escuridao):
        return None

    respostas_partida = respostas_agora - respostas_antes
    erros_partida = erros_agora - erros_antes

    if respostas_partida <= 0 or not 0 <= erros_partida <= respostas_partida:
        return None

    return {
        "taxa_erro": round(erros_partida / respostas_partida * 100, 1),
        "escuridao": escuridao,
    }


def montar_leituras(feeds: list, config: dict) -> list:
    """Transforma as entradas do canal em leituras {id, horario, medidas, risco, faixa}."""
    leituras = []

    for anterior, atual in zip(feeds, feeds[1:]):
        medidas = extrair_medidas(anterior, atual)

        if medidas is None:
            continue

        risco = calcular_risco(medidas, config)
        leituras.append({
            "id": int(atual["entry_id"]),
            "horario": formatar_horario(atual.get("created_at")),
            "medidas": medidas,
            "risco": risco,
            "faixa": classificar_faixa(risco, config),
        })

    return leituras


# ---------------------------------------------------------------------------
# MEMÓRIA: HISTÓRICO SEM DUPLICAR
# ---------------------------------------------------------------------------
def carregar_historico() -> list:
    """Lê o historico.json. Devolve lista vazia se ele não existir ou estiver inválido."""
    historico = carregar_json(ARQ_HISTORICO, [])
    return historico if isinstance(historico, list) else []


def mesclar_historico(historico: list, novas: list) -> tuple:
    """Junta as leituras novas ao histórico sem repetir id. Devolve (histórico, quantas entraram)."""
    ids_conhecidos = {leitura["id"] for leitura in historico}
    adicionadas = 0

    for leitura in novas:
        if leitura["id"] not in ids_conhecidos:
            historico.append(leitura)
            ids_conhecidos.add(leitura["id"])
            adicionadas += 1

    historico.sort(key=lambda leitura: leitura["id"])
    return historico, adicionadas


def exportar_csv(historico: list, caminho: str) -> bool:
    """Exporta o histórico para CSV com cabeçalho. Devolve True se conseguiu."""
    try:
        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(CABECALHO_CSV)

            for leitura in historico:
                escritor.writerow([
                    leitura["id"], leitura["horario"],
                    leitura["medidas"]["taxa_erro"], leitura["medidas"]["escuridao"],
                    leitura["risco"], leitura["faixa"],
                ])
        return True
    except OSError as erro:
        print(f"  Não foi possível exportar o CSV: {erro}")
        return False


# ---------------------------------------------------------------------------
# ANÁLISE
# ---------------------------------------------------------------------------
def calcular_tendencia(leituras: list, altas_seguidas: int) -> str:
    """PIORANDO se o risco subiu 'altas_seguidas' vezes seguidas no fim do histórico,
    MELHORANDO se caiu o mesmo número de vezes, e ESTÁVEL nos outros casos."""
    if len(leituras) <= altas_seguidas:
        return "SEM DADOS SUFICIENTES"

    ultimos = [leitura["risco"] for leitura in leituras[-(altas_seguidas + 1):]]
    pares = list(zip(ultimos, ultimos[1:]))

    if all(depois > antes for antes, depois in pares):
        return "PIORANDO"
    if all(depois < antes for antes, depois in pares):
        return "MELHORANDO"
    return "ESTÁVEL"


def maior_episodio_perigo(leituras: list) -> list:
    """Devolve a maior sequência contínua de leituras em PERIGO (lista vazia se não houver)."""
    maior, atual = [], []

    for leitura in leituras:
        if leitura["faixa"] == "PERIGO":
            atual.append(leitura)
            if len(atual) > len(maior):
                maior = list(atual)
        else:
            atual = []

    return maior


def contar_por_faixa(leituras: list) -> dict:
    """Conta quantas leituras caíram em cada faixa."""
    contagem = {faixa: 0 for faixa in FAIXAS}

    for leitura in leituras:
        contagem[leitura["faixa"]] += 1

    return contagem


def piores_leituras(leituras: list, quantidade: int = 5) -> list:
    """Ranking das leituras com maior risco."""
    return sorted(leituras, key=lambda leitura: leitura["risco"], reverse=True)[:quantidade]


def duracao_em_texto(inicio: str, fim: str) -> str:
    """Diferença entre dois horários 'AAAA-MM-DD HH:MM' no formato '1h30'."""
    try:
        formato = "%Y-%m-%d %H:%M"
        minutos = int((datetime.strptime(fim, formato) - datetime.strptime(inicio, formato)).total_seconds() // 60)
        return f"{minutos // 60}h{minutos % 60:02d}"
    except ValueError:
        return "duração desconhecida"


def cargo_mais_fraco() -> str:
    """Busca no canal por cargo qual cargo tem menos acertos acumulados."""
    try:
        feeds = buscar_feeds(CANAL_CARGOS)
    except (requests.RequestException, ValueError):
        return "indisponível (sem acesso ao canal por cargo)"

    if not feeds:
        return "indisponível (canal por cargo vazio)"

    ultimo = feeds[-1]
    acertos = [para_numero(ultimo.get(f"field{i + 1}")) or 0 for i in range(len(CARGOS))]
    indice = acertos.index(min(acertos))
    return f"{CARGOS[indice]} ({int(acertos[indice])} acertos acumulados)"


# ---------------------------------------------------------------------------
# TELAS DO MENU
# ---------------------------------------------------------------------------
def mostrar_cabecalho() -> None:
    """Mostra o título do programa."""
    print("\n=== Radar da Desinformação · Demokratos ===")


def mostrar_menu() -> None:
    """Mostra as opções do menu."""
    print("\n1 · Atualizar leituras")
    print("2 · Situação agora")
    print("3 · Relatório")
    print("4 · Exportar relatório.csv")
    print("0 · Sair")


def ler_opcao() -> str:
    """Lê a opção digitada. Entradas inválidas, Ctrl+C ou fim de entrada nunca derrubam o programa."""
    try:
        opcao = input("\nEscolha uma opção: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "0"

    if opcao not in {"0", "1", "2", "3", "4"}:
        print("  Opção inválida. Digite 0, 1, 2, 3 ou 4.")
        return ""

    return opcao


def acao_atualizar(historico: list) -> list:
    """Busca as leituras, junta ao histórico sem duplicar e salva o historico.json."""
    feeds, origem = obter_feeds_com_plano_b(CANAL_GERAL)

    if origem == "nenhuma":
        print("  Sem rede e sem backup.json: nenhuma leitura disponível.")
        return historico

    novas = montar_leituras(feeds, CONFIG)
    historico, adicionadas = mesclar_historico(historico, novas)
    salvar_json(ARQ_HISTORICO, historico)

    print(f"  Origem: {origem} · {len(novas)} leituras válidas · {adicionadas} novas · histórico {len(historico)}")
    return historico


def acao_situacao(historico: list) -> None:
    """Mostra a última leitura, o índice de risco, a faixa e o aviso."""
    if not historico:
        print("  Ainda não há leituras. Use a opção 1 primeiro.")
        return

    ultima = historico[-1]
    tendencia = calcular_tendencia(historico, CONFIG["altas_para_piorar"])

    print(f"  Última partida: {ultima['horario']} (id {ultima['id']})")
    print(f"  Taxa de erro: {ultima['medidas']['taxa_erro']}% · Escuridão (LDR): {ultima['medidas']['escuridao']:.0f}")
    print(f"  Índice de risco: {ultima['risco']} · Faixa: {ultima['faixa']}")
    print(f"  AVISO: {CONFIG['avisos'][ultima['faixa']]}")

    if tendencia == "PIORANDO":
        print(f"  ALERTA PIORANDO: {CONFIG['avisos']['PIORANDO']}")


def acao_relatorio(historico: list) -> None:
    """Mostra média, pico, tendência, maior episódio em PERIGO, contagem por faixa e ranking."""
    if not historico:
        print("  Ainda não há leituras. Use a opção 1 primeiro.")
        return

    riscos = [leitura["risco"] for leitura in historico]
    pico = max(historico, key=lambda leitura: leitura["risco"])
    tendencia = calcular_tendencia(historico, CONFIG["altas_para_piorar"])
    episodio = maior_episodio_perigo(historico)
    contagem = contar_por_faixa(historico)

    print(f"  Partidas no histórico: {len(historico)}")
    print(f"  Risco médio {sum(riscos) / len(riscos):.1f} · pico {pico['risco']} em {pico['horario']}")
    print(f"  Tendência: {tendencia}")

    if episodio:
        duracao = duracao_em_texto(episodio[0]["horario"], episodio[-1]["horario"])
        print(f"  Maior episódio em PERIGO: {len(episodio)} partidas seguidas, "
              f"de {episodio[0]['horario']} a {episodio[-1]['horario']} ({duracao})")
    else:
        print("  Nenhuma partida em PERIGO.")

    print("  Contagem por faixa: " + " · ".join(f"{faixa} {total}" for faixa, total in contagem.items()))
    print(f"  Cargo com menos acertos: {cargo_mais_fraco()}")

    print("  5 partidas com maior risco:")
    for posicao, leitura in enumerate(piores_leituras(historico), 1):
        print(f"    {posicao}. {leitura['horario']} · risco {leitura['risco']} · {leitura['faixa']}")


def acao_exportar(historico: list) -> None:
    """Exporta o histórico para relatorio.csv."""
    if not historico:
        print("  Ainda não há leituras. Use a opção 1 primeiro.")
        return

    if exportar_csv(historico, ARQ_RELATORIO):
        print(f"  relatorio.csv salvo com {len(historico)} linhas.")


def main() -> None:
    """Valida a configuração e roda o menu até o usuário escolher Sair."""
    try:
        validar_config(CONFIG)
    except ValueError as erro:
        print(f"Configuração inválida: {erro}")
        return

    mostrar_cabecalho()
    historico = carregar_historico()
    print(f"Histórico carregado: {len(historico)} partidas.")

    while True:
        mostrar_menu()
        opcao = ler_opcao()

        if opcao == "1":
            historico = acao_atualizar(historico)
        elif opcao == "2":
            acao_situacao(historico)
        elif opcao == "3":
            acao_relatorio(historico)
        elif opcao == "4":
            acao_exportar(historico)
        elif opcao == "0":
            print("Até a próxima!")
            break


if __name__ == "__main__":
    main()
