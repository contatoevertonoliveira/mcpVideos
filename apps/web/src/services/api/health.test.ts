import { afterEach, describe, expect, it, vi } from "vitest";
import { checkApiConnection } from "./health";

describe("checkApiConnection", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns ok with the parsed health payload when the API responds", async () => {
    const payload = { data: { status: "ok" }, meta: {} };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => payload,
      }),
    );

    const result = await checkApiConnection();

    expect(result).toEqual({ ok: true, health: payload });
  });

  it("returns ok:false when the API responds with a non-2xx status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 503 }),
    );

    const result = await checkApiConnection();

    expect(result).toEqual({ ok: false, error: "API respondeu com status 503" });
  });

  it("returns ok:false when the request throws (API unreachable)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));

    const result = await checkApiConnection();

    expect(result).toEqual({ ok: false, error: "Não foi possível conectar à API." });
  });
});
