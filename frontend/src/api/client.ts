import axios, { AxiosError } from "axios";

export const TOKEN_STORAGE_KEY = "preorder_access_token";

export interface ApiEnvelope<T> {
  data: T | null;
  error: string | null;
  message: string;
}

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// The backend always responds with { data, error, message } even on 4xx/5xx errors.
// Axios rejects with an AxiosError for non-2xx responses before our call sites ever
// see the response body, so without this the UI only shows generic axios text like
// "Request failed with status code 409" instead of the real reason (e.g. duplicate order).
export function resolveApiErrorMessage(error: AxiosError<ApiEnvelope<unknown>>): string {
  const backendMessage = error.response?.data?.message || error.response?.data?.error;
  const fallback = error.response
    ? "เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง"
    : "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบอินเทอร์เน็ต";
  return backendMessage || fallback;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiEnvelope<unknown>>) => Promise.reject(new Error(resolveApiErrorMessage(error)))
);
