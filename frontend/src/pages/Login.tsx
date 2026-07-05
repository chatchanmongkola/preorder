import { useNavigate } from "react-router-dom";

import { devLogin } from "../api/auth";
import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";

const LINE_AUTHORIZE_URL = "https://access.line.me/oauth2/v2.1/authorize";

export default function Login() {
  const { setToken } = useAuth();
  const navigate = useNavigate();

  const handleLineLogin = () => {
    const clientId = import.meta.env.VITE_LINE_CLIENT_ID;
    const redirectUri = import.meta.env.VITE_LINE_REDIRECT_URI;
    const params = new URLSearchParams({
      response_type: "code",
      client_id: clientId,
      redirect_uri: redirectUri,
      state: crypto.randomUUID(),
      scope: "profile openid",
    });
    window.location.href = `${LINE_AUTHORIZE_URL}?${params.toString()}`;
  };

  const handleDevLogin = async (asAdmin: boolean) => {
    const token = await devLogin(asAdmin);
    setToken(token);
    navigate("/");
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <Card className="w-full max-w-sm text-center">
        <CardTitle>เข้าสู่ระบบพรีออเดอร์</CardTitle>
        <CardDescription className="mt-2">เข้าสู่ระบบด้วย LINE เพื่อเริ่มสั่งของ</CardDescription>

        <Button className="mt-6 w-full" onClick={handleLineLogin}>
          เข้าสู่ระบบด้วย LINE
        </Button>

        {import.meta.env.DEV && (
          <div className="mt-4 space-y-2 border-t border-orange-100 pt-4">
            <p className="text-xs text-neutral-400">
              โหมดพัฒนา — ยังไม่ได้ตั้งค่า LINE Login จริง ใช้ปุ่มนี้แทนได้
            </p>
            <Button variant="outline" className="w-full" onClick={() => handleDevLogin(false)}>
              Dev Login (ลูกค้า)
            </Button>
            <Button variant="outline" className="w-full" onClick={() => handleDevLogin(true)}>
              Dev Login (แอดมิน)
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}
