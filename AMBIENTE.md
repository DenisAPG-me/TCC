# Ambiente, agentes e controle de acesso

## Estação e versões
| Item | Valor |
|---|---|
| Estação | AMD Ryzen 9 9950X3D (16 núcleos), 31,1 GB de RAM |
| Sistema operacional | Windows 11 Pro 10.0.26200, com WSL2 (kernel 6.18.54.1) |
| Rede | Banda larga doméstica de 750 Mb/s |
| Python (testes e análise) | 3.14.4 |
| pytest / pytest-playwright / pytest-json-report | 9.2.0 / 0.10.0 / 1.5.0 |
| Playwright (Python) / requests | 1.63.0 / 2.34.2 |
| Navegador dos testes de interface | Microsoft Edge 156.0.4314.50, `--browser chromium --browser-channel msedge`, sem interface gráfica |
| Claude Code / Codex CLI / Gemini CLI | 2.1.316 / 0.166.0 / 0.66.0 |
| SciPy / NumPy / Matplotlib | 1.18.1 / 2.5.2 / 3.11.2 |
| Limites de tempo | 900 s por geração (`harness/run_model.py`); 600 s por execução de script (`harness/run_tests.py`) |

## Agentes: comando, restrições e identificadores
| Configuração | Comando (prompt pela entrada padrão, diretório de trabalho vazio) | Restrição | Identificador retornado | Término das gerações (UTC) |
|---|---|---|---|---|
| Haiku | `claude -p --model haiku --tools "" --output-format json` | `--tools ""` desativa as ferramentas internas | claude-haiku-5-5 | 30/10 15:35 a 16:11 |
| Opus | `claude -p --model opus --tools "" --output-format json` | idem | claude-opus-5-5 | 30/10 15:37 a 16:10 |
| Luna | `codex exec --skip-git-repo-check -m gpt-6-luna -s read-only -` | sandbox somente leitura, aprovação "never" | gpt-6-luna | 30/10 15:36 a 31/10 06:36 |
| Astra | `codex exec --skip-git-repo-check -m gpt-6-astra -s read-only -` | idem | gpt-6-astra | 30/10 15:38 a 31/10 06:35 |
| Flash-Lite | `gemini --skip-trust -m gemini-flash-lite-latest -p -` | sem opção de restrição; ferramentas padrão da CLI disponíveis | gemini-flash-lite-latest | 30/10 15:36 a 15:44 |

## Verificação de acesso
- **Claude Code:** nenhuma chamada de ferramenta em todas as sessões.
- **Codex CLI:** nenhuma chamada de ferramenta nas 72 respostas finais.
- **Gemini CLI:** uma chamada interna `update_topic` por sessão, que só atualiza o título da sessão, sem acesso a arquivos ou à web.

## Itens não determinados
- a versão exata do modelo por trás do alias do Gemini;
- a versão do Claude Code no momento de cada geração;
- a eventual carga de conectores externos no Claude Code.
