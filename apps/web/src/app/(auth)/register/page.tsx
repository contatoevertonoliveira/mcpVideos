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

import { RegisterForm } from "./register-form";

export default async function RegisterPage() {
  const token = await getSessionToken();
  if (token) {
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-6 bg-zinc-50 p-8 dark:bg-black">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Criar conta</CardTitle>
          <CardDescription>
            Sua organização é criada automaticamente e você entra como owner.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <RegisterForm />
          <p className="text-center text-sm text-muted-foreground">
            Já tem uma conta?{" "}
            <Link href="/login" className="font-medium underline underline-offset-4">
              Entrar
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
