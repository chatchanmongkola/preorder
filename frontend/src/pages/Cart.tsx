import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Card, CardTitle } from "../components/ui/card";
import { useCart } from "../context/CartContext";
import { useCreateOrder, useMyOrders, useUpdateOrder } from "../hooks/useOrders";

export default function Cart() {
  const [searchParams] = useSearchParams();
  const roundId = Number(searchParams.get("round_id"));
  const navigate = useNavigate();

  const { lines, setQuantity, removeItem, clear, total } = useCart();
  const [note, setNote] = useState("");
  const createOrder = useCreateOrder();
  const updateOrder = useUpdateOrder();
  const { data: myOrders } = useMyOrders();

  // Users can only order once per round, but may edit the order until the round
  // closes. If one already exists for this round, submit should update it instead
  // of creating a new one (which the backend always rejects with 409).
  const existingOrder = myOrders?.find(
    (o) => o.round_id === roundId && o.status !== "cancelled"
  );
  const submitMutation = existingOrder ? updateOrder : createOrder;

  const handleConfirm = async () => {
    const items = lines.map((l) => ({ menu_item_id: l.item.id, quantity: l.quantity }));
    const order = existingOrder
      ? await updateOrder.mutateAsync({ orderId: existingOrder.id, items, note: note || undefined })
      : await createOrder.mutateAsync({ roundId, items, note: note || undefined });
    clear();
    navigate(`/order/${order.id}`);
  };

  if (lines.length === 0) {
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-4 p-6 text-center">
        <p className="text-neutral-500">ตะกร้าว่างเปล่า</p>
        <Button onClick={() => navigate(`/menu?round_id=${roundId}`)}>กลับไปเลือกเมนู</Button>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6 pb-28">
      <h1 className="text-2xl font-bold text-primary">ตะกร้าของฉัน</h1>

      {existingOrder && (
        <p className="rounded-2xl bg-orange-50 p-3 text-sm text-orange-700">
          คุณมีออเดอร์ในรอบนี้อยู่แล้ว การกดยืนยันจะเป็นการแก้ไขออเดอร์เดิม
        </p>
      )}

      <div className="flex flex-col gap-3">
        {lines.map((l) => (
          <Card key={l.item.id} className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">{l.item.name}</CardTitle>
              <p className="text-neutral-500">
                {l.item.price.toLocaleString()} x {l.quantity} = {(l.item.price * l.quantity).toLocaleString()} บาท
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" onClick={() => setQuantity(l.item, l.quantity - 1)}>
                -
              </Button>
              <span className="w-6 text-center">{l.quantity}</span>
              <Button size="sm" variant="outline" onClick={() => setQuantity(l.item, l.quantity + 1)}>
                +
              </Button>
              <Button size="sm" variant="ghost" onClick={() => removeItem(l.item.id)}>
                ลบ
              </Button>
            </div>
          </Card>
        ))}
      </div>

      <textarea
        className="rounded-2xl border border-orange-100 p-3 text-base"
        placeholder="หมายเหตุ (ถ้ามี)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />

      {submitMutation.isError && (
        <p className="text-sm text-red-500">{(submitMutation.error as Error).message}</p>
      )}

      <div className="fixed inset-x-0 bottom-0 mx-auto max-w-md border-t border-orange-100 bg-white p-4">
        <Button
          className="w-full"
          size="lg"
          disabled={submitMutation.isPending}
          onClick={handleConfirm}
        >
          {submitMutation.isPending
            ? "กำลังบันทึก..."
            : existingOrder
              ? `บันทึกการแก้ไข (${total.toLocaleString()} บาท)`
              : `ยืนยันออเดอร์ (${total.toLocaleString()} บาท)`}
        </Button>
      </div>
    </div>
  );
}
