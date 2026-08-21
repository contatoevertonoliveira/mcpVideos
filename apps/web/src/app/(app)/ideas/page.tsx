import { FilterChips } from "@/components/filter-chips";
import { OpportunityCard } from "@/components/opportunity-card";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getSessionToken } from "@/lib/session-cookie";
import { listChannelIdeas, listChannels } from "@/services/api/channels";

import { approveIdeaAction, triggerIdeaGenerationAction } from "../channels/actions";

const STATUS_FILTERS = [
  { label: "Todas", value: "all" },
  { label: "Recomendadas", value: "recommended" },
  { label: "Aprovadas", value: "approved" },
  { label: "Rejeitadas", value: "rejected" },
];

export default async function IdeasPage(props: PageProps<"/ideas">) {
  const token = await getSessionToken();
  if (!token) {
    return null;
  }

  const searchParams = await props.searchParams;
  const statusFilter = typeof searchParams.status === "string" ? searchParams.status : "all";

  const channels = await listChannels(token);
  // No multi-channel selector built yet (Documento 08 sec. 12's "Channel
  // Selector" is deferred, same scope trim as previous phases) - Ideas and
  // Calendar operate on the user's primary connected channel.
  const channel = channels.find((item) => item.connection_status === "connected") ?? channels[0];

  if (!channel) {
    return (
      <div className="mx-auto flex max-w-5xl flex-col gap-6 p-6 md:p-8">
        <PageHeader title="Ideias" subtitle="Novas oportunidades para o seu canal." />
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Conecte um canal em <a href="/channels" className="underline">Canais</a> para começar a
            gerar ideias.
          </CardContent>
        </Card>
      </div>
    );
  }

  const allIdeas = await listChannelIdeas(token, channel.id);
  const ideas =
    statusFilter === "all" ? allIdeas : allIdeas.filter((idea) => idea.status === statusFilter);

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 p-6 md:p-8">
      <PageHeader
        title="Ideias"
        subtitle={`Novas oportunidades encontradas para ${channel.name}.`}
        action={
          <form action={triggerIdeaGenerationAction}>
            <input type="hidden" name="channel_id" value={channel.id} />
            <Button type="submit">Gerar novas ideias</Button>
          </form>
        }
      />

      <FilterChips
        basePath="/ideas"
        paramName="status"
        options={STATUS_FILTERS}
        activeValue={statusFilter}
      />

      {ideas.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nenhuma ideia encontrada. Clique em &ldquo;Gerar novas ideias&rdquo; para começar.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {ideas.map((idea) => (
            <OpportunityCard key={idea.id} idea={idea} approveAction={approveIdeaAction} />
          ))}
        </div>
      )}
    </div>
  );
}
