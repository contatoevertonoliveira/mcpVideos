import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { checkApiConnection } from "@/services/api/health";

export default async function Home() {
  const connection = await checkApiConnection();

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-zinc-50 p-8 dark:bg-black">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>mcp_videos</CardTitle>
          <CardDescription>Fase 01 — Project Foundation</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Conexão com a API</span>
          {connection.ok ? (
            <Badge>Conectado</Badge>
          ) : (
            <Badge variant="destructive">{connection.error}</Badge>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
