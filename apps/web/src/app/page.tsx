import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
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
          <CardDescription>Fase 03 — Authentication & Security</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Conexão com a API</span>
          {connection.ok ? (
            <Badge>Conectado</Badge>
          ) : (
            <Badge variant="destructive">{connection.error}</Badge>
          )}
        </CardContent>
        <CardFooter className="flex gap-2">
          <Button render={<Link href="/register" />} className="flex-1">
            Criar conta
          </Button>
          <Button render={<Link href="/login" />} variant="outline" className="flex-1">
            Entrar
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
