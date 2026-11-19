# Demokratos

> Global Solution 2026.2 · CitizenTech · Engenharia de Software 1º ano · FIAP Rio de Janeiro

## Ficha da CitizenTech

| Campo | Resposta da equipe |
|---|---|
| **Nome da CitizenTech** | Demokratos |
| **Cidade e bairro** | Rio de Janeiro (toda a cidade). A estação física fica em espaços comunitários, como bibliotecas e escolas. A persona mora em Madureira |
| **Cidadão beneficiado** | O morador do Rio que tem curiosidade cívica, mas evita política por achar o assunto complicado, técnico ou distante. Exemplo: João, 34 anos, atendente de loja em Madureira, que usa trem e BRT e se informa por vídeos curtos e grupos de mensagem |
| **Problema, em uma frase** | Moradores do Rio têm dificuldade de entender e acompanhar a política que afeta seu dia a dia, por causa da linguagem técnica, da falta de educação política básica e da dificuldade de achar informação confiável e ligada à realidade local |
| **Como funciona** | Na plataforma web, o cidadão aprende política do zero em trilhas curtas, entende propostas reais e consulta representantes e direitos, sempre com link para a fonte oficial. Na estação física, o ESP32 detecta a presença da pessoa, aplica um quiz sobre cargos políticos e publica as estatísticas no ThingSpeak. O Python busca esses dados, calcula o Índice de Risco de desinformação e avisa o responsável pelo espaço |
| **O que cada parte faz** | veja a tabela abaixo |
| **Link do repositório** | https://github.com/alenarth/CTWP_GlobalSolution_CitzenTech |
| **Indicador de impacto** | Evolução dos acertos no quiz antes e depois das trilhas. Na estação, a taxa de erro por partida e o número de partidas em PERIGO |
| **ODS conectados** | ODS 4 (meta 4.7): educação política gratuita e acessível. ODS 10 (meta 10.2): linguagem simples e ponto de acesso para quem tem menos acesso à informação. ODS 11 (meta 11.3): cidadãos que entendem as decisões da cidade participam e cobram melhor |

### Links do protótipo

| O quê | Link |
|---|---|
| Simulação no Wokwi | https://wokwi.com/projects/479911399606222849 |
| Canal público no ThingSpeak | https://thingspeak.com/channels/3568353 |
| Vídeo do pitch | https://www.youtube.com/watch?v=Oc4OHlXjvLs |

### O que cada parte faz

| Parte | Disciplina | Pasta | O que faz |
|---|---|---|---|
| Lógica | Computational Thinking with Python | `python/` | Busca as estatísticas do Radar no ThingSpeak, calcula o Índice de Risco (taxa de erro × escuridão), guarda o histórico e gera o aviso |
| Matemática | Differentiated Problem Solving | entregue no Teams | Taxas, limites, derivadas e integrais aplicados ao crescimento da plataforma |
| Sensor | Edge Computing & Computer Systems | [Wokwi](https://wokwi.com/projects/479911399606222849) | O ESP32 do Radar da Desinformação: sensor de presença, LDR, OLED, botões e LEDs. Aplica o quiz e publica no ThingSpeak |
| Interface | Front-end Design | [GS-front-end](https://github.com/annaju507/GS-front-end) | As telas em React que o cidadão usa |
| Experiência | Software & Total Experience Design | entregue no Teams | A jornada, os requisitos, as regras de negócio e o backlog |
| Interação | Web Development | [GS-front-end](https://github.com/annaju507/GS-front-end) | O JavaScript da página, com interações e modo claro/escuro |
| Pitch | Storytelling & Inspiração Empreendedora | — | [cole aqui o link do YouTube] |

## Equipe

| Nome completo | RM |
|---|---|
| Arthur Alen Amorelli Pereira | 571897 |
| Anna Júlia Elias Andrade | 573453 |
| Clara Diel Gama Secco | 571679 |
