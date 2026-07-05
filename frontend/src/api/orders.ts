import { apiClient, type ApiEnvelope } from "./client";
import type { Order } from "./types";

export interface OrderItemInput {
  menu_item_id: number;
  quantity: number;
}

export async function createOrder(
  roundId: number,
  items: OrderItemInput[],
  note?: string
): Promise<Order> {
  const res = await apiClient.post<ApiEnvelope<Order>>("/orders", {
    round_id: roundId,
    items,
    note,
  });
  if (!res.data.data) throw new Error(res.data.error ?? "สั่งออเดอร์ไม่สำเร็จ");
  return res.data.data;
}

export async function getMyOrders(): Promise<Order[]> {
  const res = await apiClient.get<ApiEnvelope<Order[]>>("/orders/my");
  return res.data.data ?? [];
}

export async function updateOrder(
  orderId: number,
  items: OrderItemInput[],
  note?: string
): Promise<Order> {
  const res = await apiClient.patch<ApiEnvelope<Order>>(`/orders/${orderId}`, { items, note });
  if (!res.data.data) throw new Error(res.data.error ?? "แก้ไขออเดอร์ไม่สำเร็จ");
  return res.data.data;
}

export async function deleteOrder(orderId: number): Promise<void> {
  await apiClient.delete<ApiEnvelope<null>>(`/orders/${orderId}`);
}
