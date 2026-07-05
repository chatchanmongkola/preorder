import { apiClient, type ApiEnvelope } from "./client";
import type { User } from "./types";

export async function devLogin(asAdmin = false): Promise<string> {
  const res = await apiClient.post<ApiEnvelope<{ access_token: string }>>("/auth/dev-login", {
    as_admin: asAdmin,
  });
  if (!res.data.data) throw new Error(res.data.error ?? "Dev login failed");
  return res.data.data.access_token;
}

export async function lineLoginCallback(code: string, redirectUri: string): Promise<string> {
  const res = await apiClient.post<ApiEnvelope<{ access_token: string }>>("/auth/line/callback", {
    code,
    redirect_uri: redirectUri,
  });
  if (!res.data.data) throw new Error(res.data.error ?? "LINE login failed");
  return res.data.data.access_token;
}

export async function getMe(): Promise<User> {
  const res = await apiClient.get<ApiEnvelope<User>>("/auth/me");
  if (!res.data.data) throw new Error(res.data.error ?? "ไม่พบข้อมูลผู้ใช้");
  return res.data.data;
}
