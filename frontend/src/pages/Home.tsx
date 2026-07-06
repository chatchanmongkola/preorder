import { Link } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";
import { useCurrentRound } from "../hooks/useRounds";
import { formatThaiDate, formatThaiDatetime } from "../lib/format";

export default function Home() {
  const { user } = useAuth();
  const { data: round, isLoading, isError } = useCurrentRound();

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">สั่งออเดอร์</h1>
        <Link to="/orders" className="text-sm text-primary underline">
          ดูออเดอร์ทั้งหมด
        </Link>
      </div>

      {user && <p className="text-neutral-600">สวัสดี, {user.display_name}</p>}

      {isLoading && <p className="text-neutral-500">กำลังโหลดข้อมูลรอบ...</p>}

      {isError && (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 text-center">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-neutral-300">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          <p className="text-lg text-neutral-400">ไม่มีข้อมูลสำหรับรอบใหม่</p>
          <p className="text-sm text-neutral-400">กรุณารอสักครู</p>
        </div>
      )}

      {round && (
        <Card>
          <CardTitle>{formatThaiDate(round.closes_at)}</CardTitle>
          <CardDescription>ปิดรับออเดอร์: {formatThaiDatetime(round.closes_at)}</CardDescription>
          <Link to={`/menu?round_id=${round.id}`}>
            <Button className="mt-4 w-full" size="lg">
              สั่งของรอบนี้
            </Button>
          </Link>
        </Card>
      )}
    </div>
  );
}
