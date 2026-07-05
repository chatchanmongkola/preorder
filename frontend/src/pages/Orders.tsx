import { Link } from "react-router-dom";

import BackButton from "../components/BackButton";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useMyOrders } from "../hooks/useOrders";

export default function Orders() {
  const { data: orders, isLoading } = useMyOrders();

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6">
      <div className="flex items-center gap-2">
        <BackButton />
        <h1 className="text-2xl font-bold text-primary">ออเดอร์ของฉัน</h1>
      </div>

      {isLoading && <p className="text-neutral-500">กำลังโหลด...</p>}
      {orders?.length === 0 && <p className="text-neutral-500">ยังไม่มีออเดอร์</p>}

      <div className="flex flex-col gap-3">
        {orders?.map((order) => (
          <Link key={order.id} to={`/order/${order.id}`}>
            <Card>
              <CardTitle>ออเดอร์ #{order.id}</CardTitle>
              <CardDescription>
                สถานะ: {order.status} — รวม {order.total_amount.toLocaleString()} บาท
              </CardDescription>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
