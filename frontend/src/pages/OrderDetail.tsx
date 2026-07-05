import { useParams } from "react-router-dom";

import BackButton from "../components/BackButton";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useMyOrders } from "../hooks/useOrders";

export default function OrderDetail() {
  const { orderId } = useParams();
  const { data: orders, isLoading } = useMyOrders();

  const order = orders?.find((o) => o.id === Number(orderId));

  if (isLoading) return <p className="p-6 text-center text-neutral-500">กำลังโหลด...</p>;
  if (!order) return <p className="p-6 text-center text-neutral-500">ไม่พบออเดอร์นี้</p>;

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6">
      <div className="flex items-center gap-2">
        <BackButton to="/" />
        <h1 className="text-2xl font-bold text-primary">ออเดอร์ #{order.id}</h1>
      </div>
      <Card>
        <CardTitle>สถานะ: {order.status}</CardTitle>
        {order.note && <CardDescription>หมายเหตุ: {order.note}</CardDescription>}
      </Card>

      <div className="flex flex-col gap-2">
        {order.items.map((item) => (
          <Card key={item.id} className="flex items-center justify-between">
            <span>{item.name}</span>
            <span>
              {item.quantity} x {item.price_snapshot.toLocaleString()} บาท
            </span>
          </Card>
        ))}
      </div>

      <Card className="text-right">
        <CardTitle>รวม {order.total_amount.toLocaleString()} บาท</CardTitle>
      </Card>
    </div>
  );
}
