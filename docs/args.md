### Executar o Torneio

**Modo gráfico (padrão):**
```bash
uv run --active main.py
```

**Com número de jogos customizado:**
```bash
uv run --active main.py --num-matches 500
```

**Com velocidade customizada:**
```bash
uv run --active main.py --speed 2  # 2x mais rápido
```

**Modo terminal (sem gráficos):**
```bash
uv run --active main.py --speed 0
```

**Combinações de argumentos:**
```bash
uv run --active main.py -n 100 -s 0.5  # 100 jogos, 50% velocidade
```

### Argumentos da Linha de Comando

- `-n, --num-matches`: Número de mãos em uma partida entre duas duplas (padrão: 1000)
- `-s, --speed`: Velocidade de exibição das jogadas (padrão: 1)
  - `0`: Modo terminal (sem visualização gráfica)
  - `1`: Velocidade normal
  - `> 1`: Mais rápido
  - `< 1`: Mais lento
