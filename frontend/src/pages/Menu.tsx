import { useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

import BackButton from "../components/BackButton";
import { Button } from "../components/ui/button";
import { Card, CardTitle } from "../components/ui/card";
import { useCart } from "../context/CartContext";
import { useMenu } from "../hooks/useMenu";
import { useMyOrders } from "../hooks/useOrders";

export default function Menu() {
  const [searchParams] = useSearchParams();
  const roundId = Number(searchParams.get("round_id"));
  const navigate = useNavigate();

  const { data: menuItems, isLoading } = useMenu(roundId || undefined);
  const { data: myOrders } = useMyOrders();
  const { lines, addItem, setQuantity, total } = useCart();
  const hydratedForRound = useRef<number | null>(null);

  // If the user already has an order for this round (business rule: one order per
  // round, editable until close), pre-fill the cart with it so re-visiting the menu
  // doesn't start from empty and lead to an accidental duplicate-order attempt.
  useEffect(() => {
    if (!menuItems || !myOrders || lines.length > 0 || hydratedForRound.current === roundId) return;
    const existingOrder = myOrders.find((o) => o.round_id === roundId && o.status !== "cancelled");
    if (!existingOrder) return;
    hydratedForRound.current = roundId;
    for (const orderItem of existingOrder.items) {
      const menuItem = menuItems.find((m) => m.id === orderItem.menu_item_id);
      if (!menuItem) continue;
      setQuantity(menuItem, orderItem.quantity);
    }
  }, [menuItems, myOrders, roundId, lines.length, setQuantity]);

  const quantityFor = (menuItemId: number) =>
    lines.find((l) => l.item.id === menuItemId)?.quantity ?? 0;

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 p-6 pb-28">
      <div className="flex items-center gap-2">
        <BackButton />
        <h1 className="text-2xl font-bold text-primary">เมนู</h1>
      </div>

      {isLoading && <p className="text-neutral-500">กำลังโหลดเมนู...</p>}

      <div className="flex flex-col gap-3">
        {menuItems?.map((item) => {
          const qty = quantityFor(item.id);
          return (
            <Card key={item.id} className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">{item.name}</CardTitle>
                <p className="text-neutral-500">{item.price.toLocaleString()} บาท</p>
              </div>
              {qty === 0 ? (
                <Button size="sm" onClick={() => addItem(item)}>
                  เพิ่ม
                </Button>
              ) : (
                <div className="flex items-center gap-2">
                  <Button size="sm" variant="outline" onClick={() => setQuantity(item, qty - 1)}>
                    -
                  </Button>
                  <span className="w-6 text-center">{qty}</span>
                  <Button size="sm" variant="outline" onClick={() => setQuantity(item, qty + 1)}>
                    +
                  </Button>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {lines.length > 0 && (
        <div className="fixed inset-x-0 bottom-0 mx-auto max-w-md border-t border-orange-100 bg-white p-4">
          <Button className="w-full" size="lg" onClick={() => navigate(`/cart?round_id=${roundId}`)}>
            ดูตะกร้า ({total.toLocaleString()} บาท)
          </Button>
        </div>
      )}
    </div>
  );
}
