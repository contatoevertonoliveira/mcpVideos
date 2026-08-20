import Link from "next/link";
import { redirect } from "next/navigation";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { listChannels } from "@/services/api/channels";

import { disconnectChannelAction } from "./actions";

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
          {channels.map((channel) => (
            <Card key={channel.id}>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-base">{channel.name}</CardTitle>
                <Badge variant={channel.connection_status === "connected" ? "default" : "outline"}>
                  {statusLabel(channel.connection_status ?? channel.status)}
                </Badge>
              </CardHeader>
              <CardContent className="flex items-center justify-between text-sm text-muted-foreground">
                <span>Automação: {channel.automation_mode}</span>
                {channel.connection_status === "connected" && (
                  <form action={disconnectChannelAction}>
                    <input type="hidden" name="channel_id" value={channel.id} />
                    <Button type="submit" variant="outline" size="sm">
                      Desconectar
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
