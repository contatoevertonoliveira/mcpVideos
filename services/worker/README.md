# services/worker

Na Fase 01 (Project Foundation), o worker Celery **reutiliza o mesmo código e imagem de `apps/api`** — ele roda `celery -A app.core.celery_app.celery_app worker`, apenas com um comando de container diferente (ver `docker-compose.yml`, serviço `worker`). Não há código próprio aqui ainda.

Este diretório existe desde a Fase 01 para respeitar a estrutura de monorepo definida no Documento 02, e passará a ter conteúdo próprio quando o worker precisar de responsabilidades que não façam sentido dentro de `apps/api` (por exemplo, isolar dependências pesadas de processamento de mídia). Essa decisão será revisitada nas Fases 13–15 (Media Gateway / Production Pipeline).
