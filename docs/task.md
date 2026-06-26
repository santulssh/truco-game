## 🎯 Sua Tarefa

Implemente a sua dupla dentro do arquivo `student_players.py`.

Requisitos mínimos:

 - Crie uma classe que estenda `Player` e implemente ao menos os métodos `play(self, top_card, play_hist, score_hist)` e `respond(self, top_card, play_hist, score_hist)`.
- Forneça as funções `pair_name()` e `create_pair()` que retornem o nome da dupla e uma tupla com duas instâncias dos seus jogadores, respectivamente.
- Não modifique as assinaturas públicas exigidas pelo simulador.

Modelo mínimo (exemplo):

```python
from basic_players import Player

class NonePlayer(Player):
  def __init__(self):
    super().__init__(0, "Ninguém")

  def play(self, top_card, play_hist, score_hist):
    """Retorna uma tupla (decisão, carta):
    decisão: 0 = encoberta, 1 = normal, 2 = pedir truco
    carta: a carta a ser jogada (ou None)
    Parâmetros:
    - `top_card` / `vira`: a carta virada na mesa
    - `play_hist`: histórico de jogadas (lista de mãos, cada mão é lista de jogadas)
    - `score_hist`: histórico de placares correspondendo a cada mão
    """
    if self._cards:
      return 1, self._cards[0]
    return 1, None

  def respond(self, top_card, play_hist, score_hist):
    """Responde a pedidos de truco:
    retorna 0 (correr), 1 (aceitar) ou 2 (aumentar)
    """
    return 0

def pair_name():
  return "algum nome"

def create_pair():
  return (NonePlayer(), NonePlayer())
```
