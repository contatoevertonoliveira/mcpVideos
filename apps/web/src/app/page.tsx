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
    <div className="relative flex min-h-svh flex-col items-center justify-center gap-8 overflow-hidden bg-background p-8">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,color-mix(in_oklch,var(--primary),transparent_85%),transparent_60%)]"
      />
      <div className="relative flex flex-col items-center gap-2 text-center">
        <h1 className="text-3xl font-semibold tracking-tight">mcp_videos</h1>
        <p className="max-w-sm text-balance text-muted-foreground">
          Seu conteúdo. Planejado, criado e otimizado por IA.
        </p>
      </div>
      <Card className="relative w-full max-w-md shadow-(--shadow-lg)">
        <CardHeader>
          <CardTitle>Status da plataforma</CardTitle>
          <CardDescription>Content Intelligence + Production + Growth Automation</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Conexão com a API</span>
          {connection.ok ? (
            <Badge variant="success">Conectado</Badge>
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
