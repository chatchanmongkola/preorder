import { useParams } from "react-router-dom";

import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useRoundSummary } from "../hooks/useRounds";

export default function Summary() {
  const { roundId } = useParams();
  const { data: summary, isLoading, isError } = useRoundSummary(Number(roundId) || undefined);

  if (isLoading) return <p className="p-6 text-center text-neutral-500">กำลังโหลด...</p>;
  if (isError || !summary) return <p className="p-6 text-center text-neutral-500">ไม่พบข้อมูลสรุปยอด</p>;

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6">
      <h1 className="text-2xl font-bold text-primary">สรุปยอด {summary.round_name}</h1>
      <CardDescription>สถานะ: {summary.status}</CardDescription>

      <div className="flex flex-col gap-2">
        {summary.items.map((item) => (
          <Card key={item.menu_item_id} className="flex items-center justify-between">
            <span>{item.name}</span>
            <span>
              {item.quantity} ชิ้น = {item.subtotal.toLocaleString()} บาท
            </span>
          </Card>
        ))}
      </div>

      <Card className="text-right">
        <CardTitle>จำนวนออเดอร์: {summary.total_orders}</CardTitle>
        <CardTitle>ยอดรวมทั้งหมด: {summary.total_amount.toLocaleString()} บาท</CardTitle>
      </Card>
    </div>
  );
}
