import { describe, expect, it } from "vitest";
import type { AxiosError } from "axios";

import { resolveApiErrorMessage, type ApiEnvelope } from "./client";

function fakeError(partial: Partial<AxiosError<ApiEnvelope<unknown>>>): AxiosError<ApiEnvelope<unknown>> {
  return partial as AxiosError<ApiEnvelope<unknown>>;
}

describe("resolveApiErrorMessage", () => {
  it("prefers the backend's `message` field from the error envelope", () => {
    const error = fakeError({
      response: {
        data: { data: null, error: "duplicate_order", message: "คุณสั่งออเดอร์ในรอบนี้ไปแล้ว" },
      } as AxiosError<ApiEnvelope<unknown>>["response"],
    });

    expect(resolveApiErrorMessage(error)).toBe("คุณสั่งออเดอร์ในรอบนี้ไปแล้ว");
  });

  it("falls back to the `error` field when `message` is empty", () => {
    const error = fakeError({
      response: {
        data: { data: null, error: "ไม่พบรอบนี้", message: "" },
      } as AxiosError<ApiEnvelope<unknown>>["response"],
    });

    expect(resolveApiErrorMessage(error)).toBe("ไม่พบรอบนี้");
  });

  it("falls back to a generic Thai message when the response has no envelope body", () => {
    const error = fakeError({
      response: { data: undefined } as unknown as AxiosError<ApiEnvelope<unknown>>["response"],
    });

    expect(resolveApiErrorMessage(error)).toBe("เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง");
  });

  it("falls back to a network-error message when there is no response at all (e.g. server unreachable)", () => {
    const error = fakeError({ response: undefined });

    expect(resolveApiErrorMessage(error)).toBe(
      "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาตรวจสอบอินเทอร์เน็ต"
    );
  });
});
