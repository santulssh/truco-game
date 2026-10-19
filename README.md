# Truco — Simulador de Torneio

Projeto desenvolvido para a disciplina **MC102 — Algoritmos e Programação de Computadores**, da UNICAMP. O objetivo é simular torneios de Truco entre duplas de jogadores controlados por diferentes estratégias, permitindo acompanhar partidas, pontuações e histórico de jogadas. O projeto foi desenvolvido como parte das atividades da disciplina MC102, com foco na aplicação prática dos fundamentos de programação.

## Sobre o Projeto

O projeto implementa um simulador de torneios de Truco com sistema de competição *todos contra todos*, no qual cada dupla enfrenta as demais. Os jogadores utilizam estratégias distintas para tomar decisões durante as partidas, tornando possível comparar seu comportamento e desempenho. O simulador conta com uma interface gráfica para acompanhar as jogadas, um sistema de pontuação e o registro das ações realizadas durante as partidas.

### Principais Funcionalidades

- **Simulação de torneios:** partidas entre diferentes duplas em um sistema *todos contra todos*.
- **Estratégias de jogadores:** implementação de diferentes comportamentos e formas de tomar decisões.
- **Sistema de pontuação:** acompanhamento dos pontos, das mãos vencidas e dos resultados das partidas.
- **Interface gráfica:** visualização das partidas e das jogadas utilizando Pygame.
- **Histórico de jogadas:** registro das ações realizadas durante as partidas.
- **Execução configurável:** opções para definir o número de jogos e a velocidade da simulação, incluindo um modo sem interface gráfica.

## Como Funciona

O simulador organiza a competição em diferentes etapas:

1. **Mão:** cada jogador recebe três cartas e disputa até três rodadas.
2. **Jogo:** sequência de mãos até que uma das duplas alcance 12 pontos.
3. **Confronto:** conjunto de jogos disputados entre duas duplas.
4. **Torneio:** competição em que todas as duplas se enfrentam.

### Regras do Truco

O simulador utiliza regras de Truco para definir a força das cartas, as apostas e os resultados das mãos.

- **Vira e manilhas:** uma carta é revelada após a distribuição, e a carta seguinte na sequência define as manilhas, que possuem a maior força na rodada.
- **Pedido de truco:** os jogadores podem aumentar o valor da mão, seguindo a sequência de apostas prevista pelas regras implementadas.
- **Respostas às apostas:** a dupla adversária pode aceitar, desistir ou aumentar a aposta.
- **Cartas encobertas:** os jogadores podem utilizar cartas viradas para baixo como parte de suas decisões estratégicas.
- **Vitória da mão:** vence a mão a dupla que ganhar duas das três rodadas, respeitando as regras específicas do jogo.

### Estratégias dos Jogadores

O projeto inclui diferentes implementações de jogadores, cada uma com uma abordagem própria:

- **`DummyPlayer`:** escolhe suas jogadas de forma aleatória, servindo como estratégia básica de comparação.
- **`GreedyPlayer`:** prioriza as cartas mais fortes e pode pedir truco quando possui manilhas.
- **`ReverseGreedyPlayer`:** busca guardar cartas fortes para as etapas finais da mão.

A implementação do jogador da dupla segue a seguinte abordagem:
- **`ProbabilisticStrategist`:** utiliza um algoritmo de decisão baseado em cálculos probabilísticos e análise de cenários possíveis. Avalia a força das cartas e as combinações possíveis de mãos da própria dupla e dos adversários, considerando as cartas em sua mão, as jogadas realizadas e as informações fornecidas pelo parceiro. Com base nessas estimativas, define a ordem de suas jogadas e decide quando aumentar o valor do truco, buscando explorar situações favoráveis e levar os adversários a desistir da mão.

## Tecnologias Utilizadas

- **Python 3.11:** implementação da lógica do jogo, das estratégias dos jogadores e da simulação do torneio.
- **Pygame:** criação da interface gráfica para acompanhar as partidas.
- **uv:** gerenciamento do ambiente virtual e das dependências do projeto.

## Como Executar

### Requisitos

- Python 3.11
- [uv](https://docs.astral.sh/uv/), para gerenciar o ambiente e as dependências do projeto.

### 1. Criar o ambiente virtual

Abra o terminal na pasta raiz do projeto e execute:

```bash
uv venv --python 3.11
```

Esse comando cria um ambiente virtual utilizando a versão especificada do Python.

### 2. Instalar as dependências

Sincronize as dependências definidas no arquivo `uv.lock` com o ambiente virtual:

```bash
uv sync
```

O `uv` instalará as dependências declaradas no projeto. Para executar os comandos dentro do ambiente gerenciado, não é necessário ativá-lo manualmente.

Caso prefira utilizar um ambiente virtual já ativado, consulte a [documentação do uv](https://docs.astral.sh/uv/pip/environments/).

### 3. Executar o simulador

Após a instalação das dependências, execute o projeto a partir da pasta raiz.

**Modo gráfico:**

```bash
uv run main.py
```

**Definir o número de jogos:**

```bash
uv run main.py -n 500
```

**Alterar a velocidade da simulação:**

```bash
uv run main.py -s 2
```

**Executar sem interface gráfica:**

```bash
uv run main.py -s 0
```

**Combinar argumentos:**

```bash
uv run main.py -n 100 -s 0.5
```

### Argumentos da Linha de Comando

| Argumento | Descrição | Valor padrão |
|---|---|---|
| `-n`, `--num-matches` | Define o número de mãos ou jogos processados pelo simulador, conforme a implementação do programa. | `1000` |
| `-s`, `--speed` | Define a velocidade de exibição das jogadas. | `1` |

Os valores de velocidade seguem esta lógica:

- `0`: execução sem visualização gráfica.
- `1`: velocidade normal.
- Maior que `1`: execução mais rápida.
- Entre `0` e `1`: execução mais lenta.
