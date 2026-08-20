"use client";

import { Moon, Sun } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";

const STORAGE_KEY = "mcp-videos-theme";

function readInitialTheme(): "dark" | "light" {
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

function applyTheme(theme: "dark" | "light") {
  document.documentElement.classList.toggle("dark", theme === "dark");
  window.localStorage.setItem(STORAGE_KEY, theme);
}

// Rendered client-only (see app-shell.tsx's dynamic import with ssr:false):
// the inline no-FOUC script in layout.tsx runs before hydration and may
// have already removed the server-default "dark" class, so reading DOM
// state during a real SSR pass here would risk a hydration mismatch.
export function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">(readInitialTheme);

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={theme === "dark" ? "Mudar para tema claro" : "Mudar para tema escuro"}
      onClick={() => {
        const next = theme === "dark" ? "light" : "dark";
        applyTheme(next);
        setTheme(next);
      }}
    >
      {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
}
