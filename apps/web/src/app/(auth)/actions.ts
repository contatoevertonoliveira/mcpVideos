"use server";

import { redirect } from "next/navigation";

import type { AuthFormState } from "@/app/(auth)/auth-form-state";
import { clearSessionToken, getSessionToken, setSessionToken } from "@/lib/session-cookie";
import { loginUser, logoutUser, registerUser } from "@/services/api/auth";

export async function registerAction(
  _prevState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const email = String(formData.get("email") ?? "").trim();
  const name = String(formData.get("name") ?? "").trim();
  const password = String(formData.get("password") ?? "");
  const organizationName = String(formData.get("organization_name") ?? "").trim();

  if (!email || !name || !password || !organizationName) {
    return { error: "Preencha todos os campos." };
  }

  const result = await registerUser({
    email,
    name,
    password,
    organization_name: organizationName,
  });
  if (!result.ok) {
    return { error: result.message };
  }

  await setSessionToken(result.data.token);
  redirect("/dashboard");
}

export async function loginAction(
  _prevState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const email = String(formData.get("email") ?? "").trim();
  const password = String(formData.get("password") ?? "");

  if (!email || !password) {
    return { error: "Informe e-mail e senha." };
  }

  const result = await loginUser({ email, password });
  if (!result.ok) {
    return { error: result.message };
  }
  if (!result.data.token) {
    return { error: "Não foi possível concluir o login." };
  }

  await setSessionToken(result.data.token);
  redirect("/dashboard");
}

export async function logoutAction(): Promise<void> {
  const token = await getSessionToken();
  if (token) {
    await logoutUser(token);
  }
  await clearSessionToken();
  redirect("/login");
}
