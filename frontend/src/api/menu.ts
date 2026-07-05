import { apiClient, type ApiEnvelope } from "./client";
import type { MenuItem } from "./types";

export async function getMenu(roundId: number): Promise<MenuItem[]> {
  const res = await apiClient.get<ApiEnvelope<MenuItem[]>>("/menu", {
    params: { round_id: roundId },
  });
  return res.data.data ?? [];
}
