# Guia da avaliação independente
**Tempo: 35–45 minutos. Trabalhe sozinho, sem IA e sem consultar o outro avaliador.** Você recebe somente uma planilha: instruções, casos e scripts estão todos nela. Use apenas o navegador e a planilha; não execute scripts, comandos, console ou clientes de API. Preencha só as células em **amarelo**.

Abas: **Início**, **Oráculo**, **R1** a **R5**. Os IDs avaliados são G01–G20 e O01–O05; os demais são apoio.

1. **Início (3 min):** preencha nome e início.
2. **Oráculo (5 min):** confira os cinco itens O01–O05 no site, quando possível, e registre decisão e motivo.
   - **Válido:** condição e resultado corretos e verificáveis.
   - **Ajustar:** aproveitável com correção de passos, dados ou resultado; descreva a correção.
   - **Inválido:** contradiz o alvo ou o requisito, ou não corresponde a uma funcionalidade existente.
   - **Não verificável:** falta acesso, evidência ou condições para concluir; explique.
3. **Abas R1 a R5 (cerca de 5–6 min cada):** leia a US, os critérios e o oráculo da US.
   - **Pergunta opcional (até 1 min por US):** logo abaixo do oráculo, diga em uma linha se faltou algum caso importante para a US. Ela aparece só na primeira aba de cada US.
   - **Casos (4 por aba):** classifique cada caso gerado.
     - **Corresponde:** mesma condição de entrada e resultado esperado de pelo menos um caso do oráculo. Selecione um ID O; outros equivalentes vão na observação.
     - **Novo válido:** correto e verificável no alvo, sem equivalente no oráculo.
     - **Alucinado:** inventa ou contradiz campos, mensagens, endpoints, status ou fluxos do alvo ou da US.
     - **Não verificável:** não é possível concluir com os recursos e evidências disponíveis.
     - Prioridade: sem evidência, Não verificável; com contradição comprovada, Alucinado; senão, Corresponde ou Novo válido. Nas classes que não são Corresponde, selecione **Nenhum** no caso do oráculo.
   - **Qualidade (5 notas por aba):** o script completo está no **quadro cinza à direita dos casos** (role para a direita), com linhas numeradas. Atribua C1–C5 com inteiros de 0 a 5. Use 1, 2 e 4 para níveis intermediários e cite números de linha ao justificar fragilidades. Avalie o código como está, sem corrigir nem executar.

| Dimensão | 0 — ausente/péssimo | 3 — aceitável | 5 — exemplar |
|---|---|---|---|
| C1 — Legibilidade | Nomes opacos; leitura muito difícil. | Nomes e testes compreensíveis; clareza e idioma razoavelmente consistentes. | Nomes precisos, testes concisos e leitura clara, com idioma consistente. |
| C2 — Estrutura | Sem organização; duplicação generalizada. | Fixtures/helpers e organização suficientes, com alguma repetição. | Fixtures, helpers ou objetos de página e parametrização adequados; pouca duplicação. |
| C3 — Asserções significativas | Sem verificações úteis ou apenas assert True. | Verifica resultados principais de negócio, com lacunas. | Verifica precisamente resultados de negócio (textos, status, corpo) e condições relevantes. |
| C4 — Espera/flakiness | Esperas frágeis e forte dependência entre testes. | Sincronização e isolamento aceitáveis, com fragilidades pontuais. | Auto-wait/expect quando aplicável, sem sleep fixo; dados únicos, isolamento e timeouts razoáveis. |
| C5 — Manutenibilidade | Seletores/configurações frágeis; ordem e dados dificultam manutenção. | Seletores e configurações razoáveis; alguma independência e limpeza. | Seletores robustos quando aplicáveis, constantes, independência de ordem e limpeza de dados. |

4. **Conclusão (3 min):** confira as células amarelas (a pergunta sobre casos faltantes é opcional), preencha o fim e salve. Devolva somente a planilha preenchida, sem discutir decisões antes das duas entregas.

**Observações gerais**
- Em APIs, use os critérios e o material da aba; não execute requisições por código. C4 e C5 não exigem seletores nem esperas de interface.
- O oráculo é referência a verificar, não prova do comportamento atual. As descrições originais foram preservadas; quando faltarem passos, use a US e registre a insuficiência.
- Sem confirmação suficiente, marque Não verificável, sem presumir erro.
- Registre indisponibilidade do site, mudanças e qualquer impedimento.
