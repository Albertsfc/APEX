# Changelog

## [1.2.0] - 2026-07-20
### Added
- Módulo de Sincronização Bidirecional Contábil (Accounting Sync) via `accounting_sync.py` e rotas `/api/v1/sync`.
- Integração de Payment Rails para transferências via `external_pay.py` e rotas `/api/v1/payments`.
- Agente Inteligente de Aprovação Semântica (Semantic Approvals) no fluxo LangGraph para automatizar aprovações de faturas comuns.
- Agente Virtual AI CFO (`cfo_advisory.py`) para consumir previsões DSO e gerar recomendações de caixa em linguagem natural.
- Gateway Multimodal de Ingestão via rotas `/api/v1/webhooks` com suporte a Vision LLMs para extração avançada de documentos.
### Changed
- Documentação `README.md` refatorada rigorosamente para adequação ao mercado de SMEs.
## [1.1.0] - 2026-07-13
### Changed
- Refatoração de segurança "exhibit-grade" visando robustez para auditoria.
- Implementação de `PRAGMA journal_mode=WAL` no SQLite para resolver concorrência.
- Refatoração de escopo de sessões em BackgroundTasks (`invoices.py`).
- Implementação de retries exponenciais (`tenacity`) para integração segura com LLM.
- Parsing estruturado (anti-alucinação) usando `pydantic` nos Agentes Dunning.
- Adição de wrappers `try/except` robustos em todos os nós do LangGraph.
- Higienização do README e adição massiva de Docstrings e Type Hints globais.

## [1.0.0] - 2026-06-15
### Added
- Setup inicial da arquitetura LangGraph com 6 subagentes.
- Integração PyTesseract para OCR de faturas.
- Modelos Scikit-learn (Isolation Forest) e Prophet para Fraude e DSO.
- Frontend em Vanilla JS/CSS com paleta Âmbar/Laranja (padrão APEX).
- Plugins de leitura estrita do AFIS (finance) e AXIS (tax).
