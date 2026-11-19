# Registro de uso de IA

A IA foi usada como copiloto nesta parte do projeto. Abaixo estão todos os prompts usados para a pasta `python/`.
Código que a equipe não sabe explicar não pontua: todo o `main.py` foi lido, testado e é explicado pela equipe.

---

## Prompt 1

- **Quem usou:** Arthur Alen Amorelli Pereira
- **Ferramenta:** Claude (Anthropic)
- **Para quê:** saber se dava para fazer a parte de Python sem acesso à conta do ThingSpeak da colega

**Prompt enviado:**

```
Então. Agora só falta python para finalizar. Eu tenho acesso ao wokwi, mas não consigo abrir o thing speak da minha colega. Da para fazer só com isso? Ou precisa?
```

**O que aproveitamos da resposta:** a explicação de que o programa só precisa do número do canal e da Read API Key para ler os dados pela API, sem entrar na conta.

**O que mudamos ou descartamos, e por quê:** descartamos a ideia de criar um canal próprio, porque a atividade pede o canal da equipe.

---

## Prompt 2

- **Quem usou:** Arthur Alen Amorelli Pereira
- **Ferramenta:** Claude (Anthropic)
- **Para quê:** encontrar as chaves do canal no projeto do Wokwi e montar o programa

**Prompt enviado:**

```
Bom o Wokwi, tá aqui, vê se a chave ta ai ou dá para fazer alguma coisa: https://wokwi.com/projects/479911399606222849
```

(com o ZIP do projeto do Radar da Desinformação em anexo)

**O que aproveitamos da resposta:** a leitura do `config.py` do ESP32 (IDs dos canais e campos), a ideia de tratar a diferença entre dois envios seguidos como uma partida e o `main.py` inteiro, que foi testado com dados simulados no formato do ThingSpeak.

**O que mudamos ou descartamos, e por quê:** a equipe escolheu as duas medidas do índice (taxa de erro e escuridão), os pesos 0,7 e 0,3 e os textos dos avisos para combinar com o escopo de Software & Total Experience Design.

---

## Prompt 3

- **Quem usou:** Arthur Alen Amorelli Pereira
- **Ferramenta:** Claude (Anthropic)
- **Para quê:** conferir a primeira execução com os dados reais

**Prompt enviado:**

```
Pronto. Vê se tá tudo certo e se eu posso entregar
```

**O que aproveitamos da resposta:** o aviso de que o canal tinha só 4 envios (3 leituras, abaixo das 20 pedidas), de que faltava o print e de que a pasta precisava se chamar `python`.

**O que mudamos ou descartamos, e por quê:** nada descartado.

---

## Prompt 4

- **Quem usou:** Arthur Alen Amorelli Pereira
- **Ferramenta:** Claude (Anthropic)
- **Para quê:** completar as 20 leituras do canal a tempo da entrega

**Prompt enviado:**

```
MEU ANJO, FAZ ISSO PARA MIM ENTÃO. POR FAVOR. EU REPITO, ESTOU SEM TEMPO. E A COLEGA MANDOU AS CHAVES DE NOVO: [chaves do ThingSpeak omitidas aqui]
```

**O que aproveitamos da resposta:** o `gerar_partidas.py`, que envia ao canal 17 partidas simuladas continuando os totais do ESP32, cada uma marcada com o status "simulado", e o roteiro para rodar o programa e tirar o print.

**O que mudamos ou descartamos, e por quê:** decidimos declarar no README que as partidas 5 a 21 são simuladas, como pede a regra da GS sobre dados simulados.

---

## Prompt 5

- **Quem usou:** Arthur Alen Amorelli Pereira
- **Ferramenta:** Claude (Anthropic)
- **Para quê:** conferir a pasta com as orientações e o kit que o professor publicou no Teams

**Prompt enviado:**

```
Antes de eu entregar agora, vi que no teams o professor botou algumas coisas para CTWP. [texto da tarefa do Teams, modelo de README e kit do professor em anexo]
```

**O que aproveitamos da resposta:** este README reorganizado no modelo do professor, este `prompts.md` no formato pedido e as anotações de tipo que faltavam em três parâmetros.

**O que mudamos ou descartamos, e por quê:** mantivemos o nosso `main.py` em vez de recomeçar pelo modelo do kit, porque ele já cumpre todos os requisitos da atividade e a equipe sabe explicar cada função.
