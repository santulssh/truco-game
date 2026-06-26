## Critérios de Avaliação

Os jogadores serão avaliados segundo os seguintes critérios:

- **Funcionamento:** o agente joga seguindo as regras do simulador e não causa erros em partidas completas.
- **Conformidade com a API:** não alterar assinaturas; implementar `play`, `respond`, `pair_name` e `create_pair` conforme esperado.
- **Robustez:** o código deve tratar casos limites (mãos vazias, respostas inválidas) e não deve lançar exceções durante uma simulação padrão.
- **Comportamento esperado:** a estratégia deve ser coerente e justificar-se por meio do histórico (`play_hist`).
- **Qualidade do código e documentação:** clareza, nomes significativos e comentários mínimos explicando a estratégia.
- **Execução:** o simulador deve rodar com sua dupla no modo terminal (`--speed 0`) e no modo gráfico sem alterações adicionais ao resto do código.

EXTRA: Implementar jogada fake (TALVEZ)
