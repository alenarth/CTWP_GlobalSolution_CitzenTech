# Registro de uso de IA

A equipe usou o Claude (Anthropic) como copiloto para estruturar e revisar o programa desta pasta, como permite a regra da GS. Todo o código foi lido, testado e é explicado pela equipe.

## Prompts usados

1. "Agora só falta Python para finalizar. Eu tenho acesso ao Wokwi, mas não consigo abrir o ThingSpeak da minha colega. Dá para fazer só com isso? Ou precisa?"
2. "Bom, o Wokwi tá aqui, vê se a chave tá aí ou dá para fazer alguma coisa." (com o projeto do Wokwi do Radar da Desinformação em anexo)
3. "Faz isso para mim então. Estou sem tempo." (pedido para completar as 20 leituras do canal e rodar o programa)

## O que a IA fez

- Encontrou no `config.py` do ESP32 os IDs e as Read API Keys dos dois canais do ThingSpeak e explicou o que cada campo guarda.
- Propôs usar a diferença entre dois envios seguidos como uma partida, já que o ESP32 envia totais acumulados.
- Escreveu o `main.py` seguindo os requisitos da atividade e testou com dados simulados no formato do ThingSpeak, inclusive sem rede, com status 500, com arquivo corrompido e com entrada inválida.
- Escreveu o `gerar_partidas.py`, que envia ao canal partidas simuladas marcadas como "simulado", para completar as 20 leituras.
- Escreveu este README.

## O que a equipe decidiu e revisou

- As duas medidas do índice (taxa de erro e escuridão), os pesos 0,7 e 0,3 e os textos dos avisos.
- A execução final com os dados reais do canal e o print da execução.
