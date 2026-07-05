import { Link } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";
import { useCurrentRound } from "../hooks/useRounds";

export default function Home() {
  const { user, logout } = useAuth();
  const { data: round, isLoading, isError } = useCurrentRound();

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">พรีออเดอร์</h1>
        <button onClick={logout} className="text-sm text-neutral-400 underline">
          ออกจากระบบ
        </button>
      </div>

      {user && <p className="text-neutral-600">สวัสดี, {user.display_name}</p>}

      {isLoading && <p className="text-neutral-500">กำลังโหลดข้อมูลรอบ...</p>}

      {isError && (
        <Card>
          <CardTitle>ยังไม่มีรอบที่เปิดอยู่</CardTitle>
          <CardDescription>กรุณารอแอดมินเปิดรอบใหม่</CardDescription>
        </Card>
      )}

      {round && (
        <Card>
          <CardTitle>{round.name}</CardTitle>
          <CardDescription>ปิดรับออเดอร์: {new Date(round.closes_at).toLocaleString("th-TH")}</CardDescription>
          <Link to={`/menu?round_id=${round.id}`}>
            <Button className="mt-4 w-full" size="lg">
              สั่งของรอบนี้
            </Button>
          </Link>
        </Card>
      )}

      <Link to="/orders" className="text-center text-sm text-primary underline">
        ดูออเดอร์ของฉัน
      </Link>
    </div>
  );
}
