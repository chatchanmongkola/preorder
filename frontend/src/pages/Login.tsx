import { useEffect, useState } from "react";
import liff from "@line/liff";
import { useNavigate } from "react-router-dom";

import { devLogin, liffLogin } from "../api/auth";
import { Button } from "../components/ui/button";
import { Card, CardDescription, CardTitle } from "../components/ui/card";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { setToken, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [liffReady, setLiffReady] = useState(false);
  const [liffLoggedIn, setLiffLoggedIn] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/", { replace: true });
      return;
    }

    const liffId = import.meta.env.VITE_LIFF_ID;
    if (!liffId) {
      setLiffReady(false);
      return;
    }

    liff
      .init({ liffId })
      .then(() => {
        setLiffReady(true);
        const loggedIn = liff.isLoggedIn();
        setLiffLoggedIn(loggedIn);
        
        if (loggedIn) {
          const idToken = liff.getIDToken();
          if (idToken) {
            liffLogin(idToken)
              .then((token) => {
                setToken(token);
                navigate("/orders", { replace: true });
              })
              .catch((err) => setError(err instanceof Error ? err.message : "LIFF login failed"));
          } else {
            setError("ไม่สามารถรับ idToken จาก LINE ได้");
          }
        }
      })
      .catch(() => {
        setLiffReady(false);
      });
  }, [isAuthenticated, navigate, setToken]);

  const handleLiffLogin = () => {
    liff.login();
  };

  const handleDevLogin = async (asAdmin: boolean) => {
    const token = await devLogin(asAdmin);
    setToken(token);
    navigate("/");
  };

  if (isAuthenticated) return null;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-6">
      <Card className="w-full max-w-sm text-center">
        <CardTitle>เข้าสู่ระบบพรีออเดอร์</CardTitle>
        <CardDescription className="mt-2">เข้าสู่ระบบด้วย LINE เพื่อเริ่มสั่งของ</CardDescription>

        {error && <p className="mt-4 text-sm text-red-500">{error}</p>}

        {liffReady && !liffLoggedIn && (
          <Button className="mt-6 w-full" onClick={handleLiffLogin}>
            เข้าสู่ระบบด้วย LINE
          </Button>
        )}

        {liffReady && liffLoggedIn && (
          <p className="mt-6 text-sm text-neutral-500">กำลังเข้าสู่ระบบด้วย LINE...</p>
        )}

        {!liffReady && import.meta.env.DEV && (
          <div className="mt-4 space-y-2 border-t border-orange-100 pt-4">
            <p className="text-xs text-neutral-400">
              ไม่พบ LIFF environment — ใช้ Dev Login แทน
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
