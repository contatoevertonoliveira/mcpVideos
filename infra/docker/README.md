# infra/docker

Os `Dockerfile` de cada app/serviço ficam colocados junto ao próprio código (`apps/web/Dockerfile`, `apps/api/Dockerfile`) — mais simples de manter sincronizado com as dependências de cada um. Este diretório fica reservado para assets Docker compartilhados entre serviços (ex.: uma imagem base comum) caso essa necessidade surja; não obrigatório na Fase 01.
