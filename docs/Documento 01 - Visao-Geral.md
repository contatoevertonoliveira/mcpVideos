# Briefing Mestre do Projeto

## 1. Visão Geral

Construir uma plataforma SaaS multiusuário e multicanal para planejamento, geração, avaliação, agendamento, publicação e otimização automática de conteúdo para YouTube.

A experiência do usuário deve ser extremamente simples e clean.

O usuário deverá basicamente:

1. Criar uma conta.
2. Conectar um ou mais canais do YouTube via OAuth.
3. Aguardar a análise automática do canal.
4. Visualizar o diagnóstico e a estratégia sugerida.
5. Revisar ou aprovar sugestões de novos conteúdos.
6. Visualizar o calendário editorial sugerido.
7. Permitir que o sistema produza os conteúdos.
8. Aprovar manualmente ou ativar níveis maiores de automação.
9. Acompanhar publicações, resultados e recomendações.

Toda a complexidade técnica deve permanecer nos bastidores.

---

# 2. Objetivo Principal

Criar um sistema que consiga operar este ciclo:

```text
Conectar Canal
      ↓
Importar Histórico
      ↓
Entender o Canal
      ↓
Criar Channel DNA
      ↓
Entender Público e Conteúdo
      ↓
Identificar Oportunidades
      ↓
Criar Ideias
      ↓
Pontuar Ideias
      ↓
Montar Estratégia
      ↓
Criar Calendário Editorial
      ↓
Produzir Conteúdo
      ↓
Avaliar Conteúdo
      ↓
Corrigir se Necessário
      ↓
Preparar SEO
      ↓
Agendar
      ↓
Publicar
      ↓
Coletar Analytics
      ↓
Aprender com Resultados
      ↓
Melhorar Próximas Produções
```

O objetivo final é criar um verdadeiro sistema de:

**Content Intelligence + Content Production + Content Growth Automation.**

---

# 3. Princípio Central de Produto

O usuário não deve precisar conhecer:

- modelos de IA;
- APIs;
- MCPs;
- prompts;
- filas;
- renderizadores;
- LLMs;
- geração de imagem;
- geração de vídeo;
- geração de áudio;
- FFmpeg;
- custos por chamada;
- workers;
- jobs;
- retries;
- scores internos;
- infraestrutura.

Ele deve enxergar apenas:

```text
Ideia
Planejado
Produzindo
Pronto
Agendado
Publicado
```

Toda a complexidade deverá existir apenas no backend e no painel administrativo.

---

# 4. Público-Alvo Inicial

Criadores de conteúdo e gestores de canais do YouTube que desejam:

- aumentar frequência de publicação;
- automatizar produção;
- manter coerência editorial;
- encontrar novas pautas;
- otimizar Shorts;
- produzir vídeos longos;
- melhorar títulos e thumbnails;
- acompanhar resultados;
- reduzir trabalho manual;
- manter uma estratégia contínua.

A arquitetura deve ser preparada para atender posteriormente:

- agências;
- redes de canais;
- empresas;
- canais faceless;
- canais educacionais;
- canais infantis;
- entretenimento;
- notícias;
- curiosidades;
- esportes;
- nichos profissionais.

---

# 5. Escopo Inicial

A primeira plataforma deverá focar no YouTube.

Porém, toda a arquitetura deve ser independente da plataforma para futuramente suportar:

```text
YouTube
YouTube Shorts
TikTok
Instagram Reels
Facebook
X
Blogs
Podcasts
```

Evitar qualquer arquitetura que torne o núcleo dependente exclusivamente do YouTube.

---

# 6. Arquitetura Conceitual

A plataforma deverá ser dividida em grandes camadas:

```text
USER INTERFACE
      ↓
APPLICATION CORE
      ↓
CONTENT INTELLIGENCE
      ↓
ORCHESTRATION ENGINE
      ↓
AGENT LAYER
      ↓
WORKFLOW ENGINE
      ↓
MEDIA GATEWAY
      ↓
AI / MCP / PROVIDERS
      ↓
QUALITY GATE
      ↓
PUBLICATION ENGINE
      ↓
YOUTUBE
      ↓
ANALYTICS ENGINE
      ↓
LEARNING ENGINE
```

---

# 7. Stack Base

Utilizar como arquitetura principal:

## Frontend

- Next.js
- TypeScript
- React
- Tailwind CSS
- shadcn/ui

## Backend

- Python
- FastAPI

## Banco de Dados

- PostgreSQL

## Cache e Fila

- Redis

## Processamento Assíncrono

- Celery

## Processamento Multimídia

- FFmpeg

## Storage

Abstração S3-compatible.

Compatível inicialmente com:

- Cloudflare R2;
- AWS S3;
- MinIO para ambiente local.

## Infraestrutura

- Docker
- Docker Compose
- arquivos `.env`
- ambientes development/staging/production

---

# 8. Multiusuário e Multicanal

A plataforma deverá nascer como SaaS.

Estrutura conceitual:

```text
Organization
    ↓
Users
    ↓
Channels
```

Um usuário poderá:

- fazer parte de uma organização;
- possuir vários canais;
- gerenciar vários projetos;
- ter diferentes níveis de permissão.

Não implementar arquitetura single-user.

---

# 9. Autenticação

Criar autenticação própria da plataforma.

Separar:

```text
Login na Plataforma
```

de:

```text
Conexão com YouTube
```

O canal deverá ser conectado via Google OAuth.

Tokens devem ser armazenados de forma segura.

Nunca misturar credenciais de usuários diferentes.

---

# 10. Channel Intelligence

Ao conectar um canal, deverá iniciar automaticamente um workflow de análise.

O sistema deverá importar e analisar:

- informações do canal;
- vídeos;
- Shorts;
- playlists;
- títulos;
- descrições;
- datas;
- durações;
- categorias;
- frequência;
- métricas disponíveis;
- histórico de desempenho;
- padrões editoriais;
- padrões temáticos.

---

# 11. Channel DNA

Cada canal deverá possuir uma representação estruturada chamada:

**Channel DNA**

O Channel DNA deverá armazenar informações como:

- nicho;
- subnichos;
- idioma;
- audiência;
- estilo;
- formatos;
- frequência;
- pilares editoriais;
- temas recorrentes;
- temas de melhor desempenho;
- temas de pior desempenho;
- padrões de títulos;
- estilo visual;
- padrões de duração;
- identidade da marca;
- restrições;
- formatos preferidos;
- baseline de performance.

O Channel DNA deverá:

- possuir versão;
- registrar histórico;
- ser atualizado ao longo do tempo;
- nunca ser apenas um grande texto livre.

---

# 12. Audience Profile

O sistema deverá criar um perfil estimado da audiência.

Possíveis informações:

- perfil etário;
- interesses;
- idioma;
- formatos preferidos;
- duração de conteúdo;
- temas relevantes;
- comportamento histórico.

Sempre diferenciar:

```text
Dado confirmado
```

de:

```text
Inferência da IA
```

---

# 13. Content Strategy Engine

Cada canal deverá possuir uma estratégia editorial.

A estratégia deverá determinar:

- pilares de conteúdo;
- frequência;
- proporção Shorts/vídeos;
- séries recorrentes;
- temas principais;
- conteúdo experimental;
- estratégia de crescimento;
- estratégia de retenção;
- equilíbrio entre conteúdo evergreen e tendências.

---

# 14. Trend Intelligence

Criar uma camada responsável por identificar oportunidades externas.

No futuro poderá utilizar:

- tendências de busca;
- Google Trends;
- YouTube;
- notícias;
- redes sociais;
- concorrentes;
- tendências do nicho.

A arquitetura deve permitir múltiplas fontes de sinais.

---

# 15. Idea Engine

Criar agente responsável por gerar novas pautas.

Ele deverá obrigatoriamente utilizar como contexto:

```text
Channel DNA
+
Audience Profile
+
Content Strategy
+
Performance History
+
Trends
+
Recent Publications
```

Nunca produzir ideias aleatórias sem contexto.

---

# 16. Opportunity Engine

Toda ideia deverá ser avaliada e receber scores.

Exemplos:

```text
Channel Fit
Audience Fit
Trend Score
Novelty
Retention Potential
Search Potential
Competition
Brand Fit
Strategic Fit
```

Gerar posteriormente:

```text
Opportunity Score
```

As ideias deverão ser classificadas por prioridade.

---

# 17. Calendário Editorial

O sistema deverá transformar oportunidades em um plano de publicação.

O calendário deverá considerar:

- frequência definida;
- formatos;
- temas;
- equilíbrio de conteúdo;
- séries;
- campanhas;
- horário;
- disponibilidade;
- eventos;
- conteúdo relacionado.

---

# 18. Clusters de Conteúdo

A plataforma deverá conseguir relacionar conteúdos.

Exemplo:

```text
Vídeo principal
      ↓
Short 1
Short 2
Short 3
Community Post
```

Isso permitirá futuramente criação multiplataforma.

---

# 19. Content Project

Cada conteúdo aprovado deverá gerar uma entidade chamada:

```text
Content Project
```

Ela deverá centralizar:

- ideia;
- objetivo;
- formato;
- roteiro;
- hook;
- storyboard;
- cenas;
- assets;
- voz;
- áudio;
- imagens;
- vídeos;
- thumbnail;
- título;
- descrição;
- SEO;
- avaliações;
- publicação;
- analytics.

---

# 20. Pipeline de Produção

Fluxo conceitual:

```text
Idea Approved
      ↓
Research
      ↓
Script
      ↓
Script QA
      ↓
Storyboard
      ↓
Scene Planning
      ↓
Asset Generation
      ↓
Image Generation
      ↓
Video Generation
      ↓
Voice
      ↓
Audio
      ↓
Assembly
      ↓
Render
      ↓
Quality Gate
      ↓
SEO
      ↓
Final Approval
```

---

# 21. Storyboard e Scene Engine

Vídeos deverão ser divididos em cenas.

Cada cena deverá possuir:

- descrição;
- personagens;
- ambiente;
- duração;
- ação;
- câmera;
- voz;
- efeitos;
- assets;
- estado;
- relação com cena anterior;
- relação com próxima cena.

---

# 22. Continuidade

O sistema deverá manter estado entre cenas.

Exemplo:

Se um personagem termina uma cena segurando um objeto, a cena seguinte deverá saber disso.

Criar suporte para:

```text
Scene State
Character State
Object State
Environment State
```

---

# 23. Brand Registry

Criar registro de identidade do canal.

Pode incluir:

- logos;
- cores;
- fontes;
- personagens;
- templates;
- estilo;
- referências;
- instruções visuais;
- elementos proibidos.

---

# 24. Character Registry

Para canais com personagens recorrentes, criar:

```text
Character Registry
```

Cada personagem poderá possuir:

- nome;
- ID;
- descrição;
- idade aparente;
- características;
- referências;
- views;
- roupas;
- cores;
- personalidade;
- voz;
- idioma;
- negative prompt;
- regras de consistência.

---

# 25. Agent Architecture

Criar arquitetura genérica para agentes.

Agentes previstos:

## Intelligence

- Channel Analyst
- Audience Analyst
- Strategy Agent
- Trend Researcher
- Idea Agent
- Opportunity Evaluator

## Production

- Research Agent
- Script Writer
- Script Critic
- Storyboard Director
- Media Director
- Prompt Engineer
- Editor Agent

## Quality

- Brand Guardian
- Visual QA
- Audio QA
- Continuity QA
- Audience QA
- Safety QA

## Growth

- SEO Agent
- Title Agent
- Thumbnail Agent
- Performance Analyst
- Learning Agent

---

# 26. Agent Registry

Prompts não deverão ficar hardcoded em arquivos aleatórios.

Criar estrutura com:

```text
Agent
AgentVersion
AgentPrompt
AgentRun
```

Cada agente deverá ter:

- ID;
- função;
- versão;
- modelo;
- configurações;
- prompt;
- input schema;
- output schema;
- histórico de execução.

---

# 27. AI Provider Abstraction

Nunca integrar a lógica da aplicação diretamente a um fornecedor específico.

Criar abstrações como:

```text
LLMGateway
MediaGateway
VoiceGateway
MusicGateway
```

---

# 28. MCP e Media Gateway

Criar uma camada para integração com provedores/MCPs.

Exemplos futuros:

- Higgsfield;
- Kie;
- fal.ai;
- WaveSpeed;
- Replicate;
- outros.

A aplicação deverá chamar:

```text
MediaGateway
```

e não diretamente um provider específico.

---

# 29. Model Registry

Criar registro dos modelos disponíveis.

Cada modelo poderá possuir:

- nome;
- provider;
- capabilities;
- custo estimado;
- qualidade histórica;
- velocidade;
- reliability;
- resoluções;
- duração máxima;
- suporte a referência;
- image-to-video;
- text-to-video;
- áudio;
- status.

---

# 30. Media Router

Criar arquitetura para seleção automática de modelo/provedor.

Critérios futuros:

```text
Quality
Cost
Speed
Reliability
Capability
Historical Approval Rate
```

O sistema deverá futuramente escolher automaticamente a melhor combinação.

---

# 31. Cost Controller

Toda operação de IA deverá poder registrar custo.

Criar:

```text
CostEvent
```

Relacionável com:

- usuário;
- organização;
- canal;
- projeto;
- cena;
- geração;
- provider;
- modelo.

Permitir futuramente:

```text
Budget per Project
Budget per Channel
Budget per Organization
```

---

# 32. Generation Attempts

Nunca sobrescrever simplesmente uma geração anterior.

Registrar:

```text
Generation
GenerationAttempt
```

Cada tentativa deverá possuir:

- modelo;
- provider;
- input;
- output;
- custo;
- duração;
- resultado;
- erro;
- avaliação.

---

# 33. Quality Gate

Conteúdo nunca deverá ir diretamente da geração para publicação.

Fluxo:

```text
GENERATED
    ↓
QUALITY GATE
    ↓
PASS
REPAIR
REGENERATE
HUMAN REVIEW
```

---

# 34. Quality Scores

Criar estrutura capaz de receber:

```text
Brand Score
Visual Score
Audio Score
Script Score
Continuity Score
Audience Score
SEO Score
Safety Score
Retention Score
```

E posteriormente:

```text
Final Quality Score
```

---

# 35. Política de Retry

Evitar loops infinitos.

Exemplo conceitual:

```text
Attempt 1
→ repair

Attempt 2
→ alternate model

Attempt 3
→ human review
```

Também interromper se:

- orçamento excedido;
- provider indisponível;
- erro recorrente;
- baixa confiança.

---

# 36. SEO Engine

Antes da publicação, gerar:

- títulos;
- descrição;
- keywords;
- hashtags;
- capítulos quando aplicável;
- sugestões de thumbnail;
- thumbnail text;
- search intent;
- cluster relacionado.

Gerar múltiplas opções quando apropriado.

---

# 37. Thumbnail Engine

Criar suporte para:

- geração de thumbnail;
- variações;
- comparação;
- branding;
- armazenamento;
- aprovação.

---

# 38. Publication Engine

Criar camada responsável por:

- upload;
- título;
- descrição;
- thumbnail;
- metadados;
- privacidade;
- agendamento;
- publicação;
- status;
- erros.

---

# 39. Scheduler

Criar suporte para:

```text
Draft
Planned
Scheduled
Publishing
Published
Failed
```

Nunca depender apenas de jobs Celery como fonte de estado.

O banco de dados deve ser a fonte de verdade.

---

# 40. Analytics Engine

Após publicação, coletar snapshots.

Exemplos:

```text
1h
6h
24h
72h
7d
30d
```

Guardar histórico.

---

# 41. Performance Baseline

Comparar conteúdo com:

- média do canal;
- conteúdo do mesmo formato;
- mesma duração;
- mesmo tema;
- mesmos períodos;
- conteúdos semelhantes.

---

# 42. Learning Engine

O sistema deverá aprender progressivamente.

Criar estrutura para:

```text
LearningEvent
```

Exemplo:

```text
Finding:
Shorts entre 20 e 28 segundos têm retenção superior.

Confidence:
0.84

Sample Size:
47

Effect:
+13%
```

Não alterar automaticamente toda a estratégia baseado em amostras pequenas.

---

# 43. Modos de Automação

Criar quatro níveis futuros:

## Manual

Sistema apenas auxilia.

## Assisted

Sistema cria, usuário aprova.

## Semi-Auto

Sistema produz automaticamente; usuário aprova publicação.

## Autopilot

Sistema:

```text
planeja
produz
avalia
corrige
agenda
publica
monitora
aprende
```

---

# 44. Workflow Engine

Criar estrutura explícita de workflows.

Exemplo:

```text
short.production.v1
```

Etapas:

```text
IDEA_SELECTED
RESEARCH
SCRIPT
SCRIPT_QA
STORYBOARD
PRODUCTION
ASSEMBLY
QUALITY
SEO
READY
SCHEDULED
PUBLISHED
```

---

# 45. Workflow Observability

Cada execução deverá registrar:

```text
WorkflowRun
WorkflowStep
WorkflowEvent
```

Guardar:

- início;
- fim;
- status;
- input;
- output;
- erros;
- retry;
- agente;
- provider;
- custo.

---

# 46. Dashboard do Usuário

A interface deve ser simples.

Página inicial deverá priorizar:

```text
Canal
Status
Conteúdos de hoje
Próximas publicações
Ideias sugeridas
Resultados
Recomendações
```

Evitar elementos técnicos.

---

# 47. Telas Principais

Planejar inicialmente:

```text
Login
Onboarding
Connect Channel
Channel Analysis
Dashboard
Ideas
Calendar
Content Project
Publications
Analytics
Settings
Billing
```

---

# 48. Control Center

Separado da interface comum.

Somente administrativo/técnico.

Deverá futuramente mostrar:

- jobs;
- workers;
- workflows;
- erros;
- filas;
- providers;
- health;
- custos;
- tokens;
- geração;
- retries;
- QA;
- publicação;
- quotas;
- logs.

---

# 49. Segurança

Desde o início implementar:

- isolamento por organização;
- isolamento por usuário;
- proteção OAuth;
- criptografia de tokens sensíveis;
- secrets via ambiente;
- logs sem credenciais;
- validação de uploads;
- autorização por recurso;
- rate limiting;
- audit logs.

---

# 50. Auditoria

Ações relevantes deverão ser rastreáveis.

Exemplos:

```text
User connected channel
System generated idea
User approved content
Agent regenerated scene
System scheduled publication
System published video
User changed autopilot
```

---

# 51. Event-Driven Architecture

Sempre que possível, eventos internos deverão representar mudanças relevantes.

Exemplos:

```text
channel.connected
channel.analyzed

idea.created
idea.approved

project.created

script.completed

media.generated

quality.failed
quality.passed

publication.scheduled
publication.completed

analytics.updated
```

Isso facilitará automações futuras.

---

# 52. Feature Flags

Criar suporte para ativar recursos progressivamente.

Exemplos:

```text
AUTOPILOT
AUTO_PUBLISH
TREND_ENGINE
MEDIA_ROUTER
LEARNING_ENGINE
```

---

# 53. APIs Internas

Utilizar APIs e serviços bem definidos.

Evitar acoplamento direto entre módulos.

Exemplo:

```text
ChannelService
StrategyService
IdeaService
ProjectService
WorkflowService
MediaService
QualityService
PublicationService
AnalyticsService
```

---

# 54. Testabilidade

A arquitetura deverá permitir:

- mocks de IA;
- mocks do YouTube;
- mocks dos providers;
- workflows de teste;
- testes unitários;
- integração;
- E2E.

Não exigir consumo real de créditos para executar testes básicos.

---

# 55. Desenvolvimento Local

O projeto deverá subir localmente com:

```bash
docker compose up
```

Ambiente local deverá possuir:

- frontend;
- backend;
- PostgreSQL;
- Redis;
- worker;
- storage local ou MinIO.

---

# 56. Documentação

Manter durante todo desenvolvimento:

```text
/docs
```

Com:

- architecture.md
- database.md
- workflows.md
- agents.md
- providers.md
- youtube.md
- security.md
- deployment.md
- roadmap.md

---

# 57. Regra Fundamental para Claude Code

Não tentar implementar todo o sistema de uma vez.

O projeto possui 20 fases.

Toda implementação deverá respeitar as interfaces, entidades e arquitetura previstas neste documento, mesmo quando determinado módulo ainda não estiver implementado.

Nunca implementar funcionalidades futuras de maneira improvisada dentro de módulos anteriores.

---

# 58. Fases de Implementação

## MACROETAPA A — FOUNDATION

### Fase 01 — Project Foundation

Criar:

- monorepo;
- frontend;
- backend;
- Docker;
- PostgreSQL;
- Redis;
- Celery;
- storage;
- configurações;
- logging;
- health checks.

---

### Fase 02 — Core Domain & Database

Criar:

- modelos principais;
- migrations;
- repositories;
- services;
- base multi-tenant;
- organizations;
- users;
- channels;
- projetos;
- eventos.

---

### Fase 03 — Authentication & Security

Implementar:

- autenticação;
- sessão;
- autorização;
- roles;
- secrets;
- segurança básica;
- auditoria.

---

### Fase 04 — YouTube Integration

Implementar:

- Google OAuth;
- conectar/desconectar canais;
- armazenamento seguro de tokens;
- leitura inicial do canal;
- abstração YouTube Gateway.

---

## MACROETAPA B — CONTENT INTELLIGENCE

### Fase 05 — Channel Importer

Importar:

- canal;
- vídeos;
- Shorts;
- playlists;
- métricas;
- histórico.

---

### Fase 06 — Channel Intelligence

Implementar:

- Channel Analyst;
- Audience Analyst;
- classificação;
- identificação de padrões.

---

### Fase 07 — Channel DNA

Implementar:

- estrutura;
- versionamento;
- perfil editorial;
- perfil de audiência;
- baseline.

---

### Fase 08 — Strategy Engine

Implementar:

- pilares;
- frequência;
- formatos;
- estratégia editorial;
- recomendações.

---

### Fase 09 — Ideas & Opportunity Engine

Implementar:

- geração de ideias;
- scoring;
- ranking;
- contextualização;
- histórico.

---

### Fase 10 — Content Calendar

Implementar:

- planejamento;
- calendário;
- sugestões de frequência;
- drag-and-drop futuro;
- aprovação.

---

## MACROETAPA C — CONTENT FACTORY

### Fase 11 — Workflow & Agent Engine

Implementar:

- Agent Registry;
- Agent Runs;
- Workflow Engine;
- Workflow Events;
- versões;
- schemas.

---

### Fase 12 — Script & Storyboard Engine

Implementar:

- pesquisa;
- roteiro;
- avaliação;
- storyboard;
- cenas;
- continuidade.

---

### Fase 13 — AI/MCP Media Gateway

Implementar:

- provider abstraction;
- MCP adapters;
- model registry;
- media jobs;
- status;
- geração.

---

### Fase 14 — Media Router & Cost Controller

Implementar:

- escolha de provider;
- escolha de modelo;
- custo;
- reliability;
- budgets;
- fallback.

---

### Fase 15 — Media Production Pipeline

Implementar:

- imagem;
- vídeo;
- voz;
- áudio;
- assets;
- FFmpeg;
- composição;
- renderização.

---

## MACROETAPA D — QUALITY & PUBLICATION

### Fase 16 — Quality Gate

Implementar:

- agentes avaliadores;
- scores;
- visual QA;
- áudio;
- continuidade;
- branding;
- safety;
- repair;
- retry.

---

### Fase 17 — SEO & Thumbnail Engine

Implementar:

- títulos;
- descrição;
- keywords;
- hashtags;
- thumbnails;
- opções;
- scores.

---

### Fase 18 — Scheduler & YouTube Publisher

Implementar:

- calendário real;
- agendamento;
- publicação;
- upload;
- thumbnail;
- metadata;
- retries;
- status.

---

## MACROETAPA E — OPTIMIZATION & AUTONOMY

### Fase 19 — Analytics & Learning Engine

Implementar:

- snapshots;
- métricas;
- comparação;
- baseline;
- aprendizado;
- insights;
- recomendações.

---

### Fase 20 — Autopilot, Billing & Control Center

Implementar:

- Manual;
- Assisted;
- Semi-Auto;
- Autopilot;
- billing;
- planos;
- limites;
- custos;
- painel administrativo;
- provider health;
- observabilidade;
- operação SaaS.

---

# 59. Mapa Resumido das 20 Fases

```text
01 Foundation
02 Core Domain
03 Authentication
04 YouTube Integration
05 Channel Importer
06 Channel Intelligence
07 Channel DNA
08 Strategy Engine
09 Ideas & Opportunities
10 Content Calendar
11 Workflow & Agents
12 Scripts & Storyboards
13 MCP / Media Gateway
14 Router & Costs
15 Production
16 Quality Gate
17 SEO & Thumbnail
18 Publishing
19 Analytics & Learning
20 Autopilot & SaaS
```

---

# 60. Resultado Final Esperado

Quando as 20 fases estiverem concluídas, a experiência deverá ser aproximadamente:

```text
Usuário cria conta
       ↓
Conecta YouTube
       ↓
Sistema importa o canal
       ↓
Sistema entende o canal
       ↓
Cria Channel DNA
       ↓
Sugere estratégia
       ↓
Sugere novos conteúdos
       ↓
Cria calendário
       ↓
Usuário aprova
       ↓
Sistema produz
       ↓
Agentes avaliam
       ↓
Sistema corrige
       ↓
Sistema prepara SEO
       ↓
Sistema agenda
       ↓
Sistema publica
       ↓
Sistema mede
       ↓
Sistema aprende
       ↓
Sistema melhora continuamente
```

No modo Autopilot:

```text
CONNECT CHANNEL
      ↓

      CONTENT OS

      ↓

PUBLICAÇÕES CONTÍNUAS
```

Esse deve ser o princípio de produto que orientará toda a arquitetura.