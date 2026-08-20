import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import {
  getChannelDNA,
  getChannelIntelligence,
  getChannelStrategyStatus,
  listChannelIdeas,
  listChannels,
  listChannelVideos,
} from "@/services/api/channels";

import {
  approveIdeaAction,
  approveStrategyAction,
  disconnectChannelAction,
  triggerAnalysisAction,
  triggerDNAGenerationAction,
  triggerIdeaGenerationAction,
  triggerStrategyGenerationAction,
  triggerSyncAction,
} from "./actions";

function ideaStatusVariant(status: string): "success" | "destructive" | "outline" | "info" {
  if (status === "recommended" || status === "approved") return "success";
  if (status === "rejected") return "destructive";
  if (status === "evaluating") return "info";
  return "outline";
}

function ideaStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    draft: "Rascunho",
    evaluating: "Avaliando",
    recommended: "Recomendada",
    rejected: "Rejeitada",
    approved: "Aprovada",
    archived: "Arquivada",
  };
  return labels[status] ?? status;
}

function formatLastSynced(lastSyncedAt: string | null): string {
  if (!lastSyncedAt) {
    return "Nunca sincronizado";
  }
  return `Última sincronização: ${new Date(lastSyncedAt).toLocaleString("pt-BR")}`;
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    connected: "Conectado",
    needs_reauthorization: "Reconexão necessária",
    syncing: "Sincronizando",
    error: "Erro",
    disconnected: "Desconectado",
  };
  return labels[status] ?? status;
}

export default async function ChannelsPage(props: PageProps<"/channels">) {
  const token = await getSessionToken();
  if (!token) {
    return null;
  }

  const searchParams = await props.searchParams;
  const connected = searchParams.connected === "1";
  const error = typeof searchParams.error === "string" ? searchParams.error : null;

  const channels = await listChannels(token);
  const videoCounts = await Promise.all(
    channels.map((channel) => listChannelVideos(token, channel.id).then((videos) => videos.length)),
  );
  const intelligence = await Promise.all(
    channels.map((channel) => getChannelIntelligence(token, channel.id)),
  );
  const dna = await Promise.all(channels.map((channel) => getChannelDNA(token, channel.id)));
  const strategy = await Promise.all(
    channels.map((channel) => getChannelStrategyStatus(token, channel.id)),
  );
  const ideas = await Promise.all(channels.map((channel) => listChannelIdeas(token, channel.id)));

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 p-6 md:p-8">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">Canais</h1>
        <Button render={<a href="/oauth/youtube/start" />}>Conectar YouTube</Button>
      </header>

      {connected && (
        <p className="rounded-lg border border-success/30 bg-success/10 px-4 py-2 text-sm text-success">
          Canal conectado com sucesso.
        </p>
      )}
      {error && (
        <p className="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">
          Não foi possível conectar o canal: {error}
        </p>
      )}

      {channels.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nenhum canal conectado ainda. Clique em &ldquo;Conectar YouTube&rdquo; para começar.
          </CardContent>
        </Card>
      ) : (
        <div className="flex flex-col gap-3">
          {channels.map((channel, index) => (
            <Card key={channel.id}>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base">{channel.name}</CardTitle>
                <Badge variant={channel.connection_status === "connected" ? "success" : "outline"}>
                  {statusLabel(channel.connection_status ?? channel.status)}
                </Badge>
              </CardHeader>
              <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <span>Automação: {channel.automation_mode}</span>
                  <span>{videoCounts[index]} vídeos importados</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>{formatLastSynced(channel.last_synced_at)}</span>
                  {channel.connection_status === "connected" && (
                    <div className="flex flex-wrap justify-end gap-2">
                      <form action={triggerSyncAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Sincronizar agora
                        </Button>
                      </form>
                      <form action={triggerAnalysisAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Analisar canal
                        </Button>
                      </form>
                      <form action={triggerDNAGenerationAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Gerar DNA
                        </Button>
                      </form>
                      <form action={triggerStrategyGenerationAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Gerar estratégia
                        </Button>
                      </form>
                      <form action={triggerIdeaGenerationAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Gerar ideias
                        </Button>
                      </form>
                      <form action={disconnectChannelAction}>
                        <input type="hidden" name="channel_id" value={channel.id} />
                        <Button type="submit" variant="outline" size="sm">
                          Desconectar
                        </Button>
                      </form>
                    </div>
                  )}
                </div>
                {intelligence[index].channel_profile && (
                  <div className="mt-1 rounded-lg border border-border bg-surface p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-foreground">
                      Diagnóstico
                    </p>
                    <p className="mt-1">
                      {intelligence[index].channel_profile?.primary_category ?? "Categoria não identificada"}
                      {" · "}
                      {intelligence[index].channel_profile?.primary_language ?? "Idioma não identificado"}
                      {" · confiança "}
                      {Math.round((intelligence[index].channel_profile?.confidence ?? 0) * 100)}%
                    </p>
                    {intelligence[index].channel_profile?.estimated_audience && (
                      <p className="mt-1">
                        Audiência estimada: {intelligence[index].channel_profile?.estimated_audience}
                      </p>
                    )}
                    {intelligence[index].channel_profile?.content_summary && (
                      <p className="mt-1">{intelligence[index].channel_profile?.content_summary}</p>
                    )}
                  </div>
                )}
                {dna[index] && (
                  <div className="mt-1 rounded-lg border border-border bg-surface p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-foreground">
                      DNA do Canal — v{dna[index]?.version} ({dna[index]?.status}) · confiança{" "}
                      {Math.round((dna[index]?.confidence ?? 0) * 100)}%
                    </p>
                    {!!dna[index]?.content_patterns_json.content_patterns?.length && (
                      <div className="mt-2">
                        <p className="font-medium text-foreground">Pilares de conteúdo</p>
                        <ul className="ml-4 list-disc">
                          {dna[index]?.content_patterns_json.content_patterns?.map((pattern) => (
                            <li key={pattern}>{pattern}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {!!dna[index]?.performance_patterns_json.high_performing_patterns?.length && (
                      <div className="mt-2">
                        <p className="font-medium text-foreground">O que performa bem</p>
                        <ul className="ml-4 list-disc">
                          {dna[index]?.performance_patterns_json.high_performing_patterns?.map(
                            (pattern) => <li key={pattern}>{pattern}</li>,
                          )}
                        </ul>
                      </div>
                    )}
                    {!!dna[index]?.publishing_patterns_json.publishing_patterns?.length && (
                      <div className="mt-2">
                        <p className="font-medium text-foreground">Padrão de publicação</p>
                        <ul className="ml-4 list-disc">
                          {dna[index]?.publishing_patterns_json.publishing_patterns?.map(
                            (pattern) => <li key={pattern}>{pattern}</li>,
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
                {strategy[index].active && (
                  <div className="mt-1 rounded-lg border border-border bg-surface p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-foreground">
                      Estratégia atual — v{strategy[index].active?.version}
                    </p>
                    <p className="mt-1">{strategy[index].active?.objective}</p>
                    <p className="mt-1">
                      Shorts {Math.round((strategy[index].active?.shorts_ratio ?? 0) * 100)}% ·
                      Long-form {Math.round((strategy[index].active?.long_form_ratio ?? 0) * 100)}% ·
                      Experimental {Math.round((strategy[index].active?.experimental_ratio ?? 0) * 100)}%
                    </p>
                    <ul className="ml-4 mt-1 list-disc">
                      {strategy[index].active?.pillars.map((pillar) => (
                        <li key={pillar.id}>
                          {pillar.name} ({Math.round(pillar.target_ratio * 100)}%)
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {strategy[index].pending_draft && (
                  <div className="mt-1 rounded-lg border border-warning/40 bg-warning/10 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-foreground">
                      Recomendação de estratégia — v{strategy[index].pending_draft?.version} (aguardando
                      aprovação)
                    </p>
                    <p className="mt-1">{strategy[index].pending_draft?.objective}</p>
                    <p className="mt-1">
                      Shorts {Math.round((strategy[index].pending_draft?.shorts_ratio ?? 0) * 100)}% ·
                      Long-form{" "}
                      {Math.round((strategy[index].pending_draft?.long_form_ratio ?? 0) * 100)}% ·
                      Experimental{" "}
                      {Math.round((strategy[index].pending_draft?.experimental_ratio ?? 0) * 100)}%
                    </p>
                    <ul className="ml-4 mt-1 list-disc">
                      {strategy[index].pending_draft?.pillars.map((pillar) => (
                        <li key={pillar.id}>
                          {pillar.name} ({Math.round(pillar.target_ratio * 100)}%)
                        </li>
                      ))}
                    </ul>
                    {!!strategy[index].pending_draft?.strategy_json.recommendations?.length && (
                      <div className="mt-2">
                        <p className="font-medium text-foreground">Recomendações</p>
                        <ul className="ml-4 list-disc">
                          {strategy[index].pending_draft?.strategy_json.recommendations?.map((rec) => (
                            <li key={rec}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <form action={approveStrategyAction} className="mt-2">
                      <input type="hidden" name="channel_id" value={channel.id} />
                      <input
                        type="hidden"
                        name="strategy_id"
                        value={strategy[index].pending_draft?.id}
                      />
                      <Button type="submit" size="sm">
                        Aprovar estratégia
                      </Button>
                    </form>
                  </div>
                )}
                {!!ideas[index].length && (
                  <div className="mt-1 rounded-lg border border-border bg-surface p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-foreground">
                      Ideias de conteúdo
                    </p>
                    <div className="mt-2 flex flex-col gap-2">
                      {ideas[index].map((idea) => (
                        <div
                          key={idea.id}
                          className="rounded-lg border border-border bg-background p-3"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <p className="font-medium text-foreground">{idea.title}</p>
                            <Badge variant={ideaStatusVariant(idea.status)}>
                              {ideaStatusLabel(idea.status)}
                            </Badge>
                          </div>
                          <p className="mt-1 text-xs">
                            {idea.opportunity_score !== null
                              ? `Score ${idea.opportunity_score.toFixed(1)}`
                              : "Ainda não avaliada"}
                            {idea.recommended_format && ` · ${idea.recommended_format}`}
                          </p>
                          {idea.summary && <p className="mt-1">{idea.summary}</p>}
                          {idea.reasoning_summary && (
                            <p className="mt-1 italic">{idea.reasoning_summary}</p>
                          )}
                          {idea.status === "recommended" && (
                            <form action={approveIdeaAction} className="mt-2">
                              <input type="hidden" name="channel_id" value={channel.id} />
                              <input type="hidden" name="idea_id" value={idea.id} />
                              <Button type="submit" variant="outline" size="sm">
                                Adicionar
                              </Button>
                            </form>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
