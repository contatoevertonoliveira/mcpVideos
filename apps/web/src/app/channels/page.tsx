import Link from "next/link";
import { redirect } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { getChannelIntelligence, listChannels, listChannelVideos } from "@/services/api/channels";

import { disconnectChannelAction, triggerAnalysisAction, triggerSyncAction } from "./actions";

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
    redirect("/login");
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

  return (
    <div className="mx-auto flex min-h-svh max-w-3xl flex-col gap-6 p-8">
      <header className="flex items-center justify-between">
        <div>
          <Link href="/dashboard" className="text-sm text-muted-foreground underline">
            ← Dashboard
          </Link>
          <h1 className="text-lg font-semibold">Canais</h1>
        </div>
        <Button render={<a href="/oauth/youtube/start" />}>Conectar YouTube</Button>
      </header>

      {connected && (
        <p className="rounded-md border border-green-600/30 bg-green-600/10 px-4 py-2 text-sm text-green-700 dark:text-green-400">
          Canal conectado com sucesso.
        </p>
      )}
      {error && (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
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
                <Badge variant={channel.connection_status === "connected" ? "default" : "outline"}>
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
                    <div className="flex gap-2">
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
                  <div className="mt-1 rounded-md border border-border bg-muted/30 p-3">
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
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
