import Link from "next/link";
import { redirect } from "next/navigation";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";

import { LoginForm } from "./login-form";

export default async function LoginPage() {
  const token = await getSessionToken();
  if (token) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-zinc-50 p-8 dark:bg-black">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Entrar</CardTitle>
          <CardDescription>Acesse sua conta mcp_videos.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <LoginForm />
          <p className="text-center text-sm text-muted-foreground">
            Não tem uma conta?{" "}
            <Link href="/register" className="font-medium underline underline-offset-4">
              Criar conta
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
