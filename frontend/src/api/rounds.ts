import { apiClient, type ApiEnvelope } from "./client";
import type { Round, RoundSummary } from "./types";

export async function getCurrentRound(): Promise<Round> {
  const res = await apiClient.get<ApiEnvelope<Round>>("/rounds/current");
  if (!res.data.data) throw new Error(res.data.error ?? "ไม่มีรอบที่เปิดอยู่");
  return res.data.data;
}

export async function getRound(roundId: number): Promise<Round> {
  const res = await apiClient.get<ApiEnvelope<Round>>(`/rounds/${roundId}`);
  if (!res.data.data) throw new Error(res.data.error ?? "ไม่พบรอบนี้");
  return res.data.data;
}

export async function getRoundSummary(roundId: number): Promise<RoundSummary> {
  const res = await apiClient.get<ApiEnvelope<RoundSummary>>(`/rounds/${roundId}/summary`);
  if (!res.data.data) throw new Error(res.data.error ?? "ไม่พบข้อมูลสรุปยอด");
  return res.data.data;
}
