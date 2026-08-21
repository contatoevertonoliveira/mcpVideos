import { CalendarPlus, TrendingUp } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { ContentIdeaSummary } from "@/types/channel";

// Documento 08B sec. 37: "Não determinar cor diretamente no componente.
// Usar função getOpportunityScoreVariant(score)". Thresholds mirror the
// backend's own RECOMMEND_THRESHOLD=60 (app/services/opportunity_scoring.py).
function getOpportunityScoreVariant(score: number): "text-success" | "text-info" | "text-warning" {
  if (score >= 85) return "text-success";
  if (score >= 60) return "text-info";
  return "text-warning";
}

const ORIGIN_LABELS: Record<string, string> = {
  ai: "Análise de IA",
  trend: "Tendência",
  user: "Usuário",
  analytics: "Analytics",
  series: "Série",
  repurpose: "Reaproveitamento",
};

const FORMAT_LABELS: Record<string, string> = {
  short: "Short",
  long_form: "Vídeo",
  live: "Live",
  unknown: "Formato",
};

const STATUS_VARIANT: Record<string, "success" | "destructive" | "outline" | "info"> = {
  recommended: "success",
  approved: "success",
  rejected: "destructive",
  evaluating: "info",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Rascunho",
  evaluating: "Avaliando",
  recommended: "Recomendada",
  rejected: "Rejeitada",
  approved: "Aprovada",
  archived: "Arquivada",
};

export function OpportunityCard({
  idea,
  approveAction,
}: {
  idea: ContentIdeaSummary;
  approveAction: (formData: FormData) => void;
}) {
  return (
    <Card className="flex flex-col gap-3 py-5">
      <CardContent className="flex flex-1 flex-col gap-3">
        <div className="flex items-center justify-between">
          {idea.opportunity_score !== null ? (
            <div
              className={cn(
                "flex items-center gap-1 text-base font-bold",
                getOpportunityScoreVariant(idea.opportunity_score),
              )}
            >
              <TrendingUp className="size-4" />
              {Math.round(idea.opportunity_score)}
            </div>
          ) : (
            <span className="text-xs font-medium text-muted-foreground">Avaliando</span>
          )}
          <Badge variant="secondary" className="uppercase tracking-wide">
            {FORMAT_LABELS[idea.recommended_format ?? "unknown"] ?? idea.recommended_format}
          </Badge>
        </div>

        <div>
          <h3 className="text-lg leading-snug font-bold text-foreground">{idea.title}</h3>
          {idea.summary && (
            <p className="mt-1.5 line-clamp-2 text-sm text-muted-foreground">{idea.summary}</p>
          )}
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          {idea.idea_type && <span>Pilar: {idea.idea_type}</span>}
          <span>Fonte: {ORIGIN_LABELS[idea.origin] ?? idea.origin}</span>
        </div>

        {idea.reasoning_summary && (
          <div
            className={cn(
              "rounded-md border-l-2 bg-surface px-3 py-2 text-xs text-muted-foreground",
              idea.status === "rejected" ? "border-l-danger" : "border-l-primary",
            )}
          >
            <span className="font-medium text-foreground">Por quê: </span>
            {idea.reasoning_summary}
          </div>
        )}

        <div className="mt-auto flex items-center justify-between pt-1">
          {idea.status === "recommended" ? (
            <form action={approveAction}>
              <input type="hidden" name="channel_id" value={idea.channel_id} />
              <input type="hidden" name="idea_id" value={idea.id} />
              <Button type="submit" size="sm" className="gap-1.5">
                <CalendarPlus className="size-3.5" />
                Adicionar ao calendário
              </Button>
            </form>
          ) : (
            <Badge variant={STATUS_VARIANT[idea.status] ?? "outline"}>
              {STATUS_LABELS[idea.status] ?? idea.status}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
