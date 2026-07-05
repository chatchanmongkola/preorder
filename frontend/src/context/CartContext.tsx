import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import type { MenuItem } from "../api/types";

interface CartLine {
  item: MenuItem;
  quantity: number;
}

interface CartContextValue {
  lines: CartLine[];
  addItem: (item: MenuItem) => void;
  removeItem: (menuItemId: number) => void;
  setQuantity: (item: MenuItem, quantity: number) => void;
  clear: () => void;
  total: number;
}

const CartContext = createContext<CartContextValue | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);

  const addItem = useCallback((item: MenuItem) => {
    setLines((prev) => {
      const existing = prev.find((l) => l.item.id === item.id);
      if (existing) {
        return prev.map((l) => (l.item.id === item.id ? { ...l, quantity: l.quantity + 1 } : l));
      }
      return [...prev, { item, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((menuItemId: number) => {
    setLines((prev) => prev.filter((l) => l.item.id !== menuItemId));
  }, []);

  // Accepts the full item (not just its id) so it can add a brand-new line -
  // not just update the quantity of a line that already exists in the cart.
  const setQuantity = useCallback((item: MenuItem, quantity: number) => {
    setLines((prev) => {
      if (quantity <= 0) return prev.filter((l) => l.item.id !== item.id);
      const existing = prev.find((l) => l.item.id === item.id);
      if (existing) {
        return prev.map((l) => (l.item.id === item.id ? { ...l, quantity } : l));
      }
      return [...prev, { item, quantity }];
    });
  }, []);

  const clear = useCallback(() => setLines([]), []);

  const total = useMemo(
    () => lines.reduce((sum, l) => sum + l.item.price * l.quantity, 0),
    [lines]
  );

  const value = useMemo<CartContextValue>(
    () => ({ lines, addItem, removeItem, setQuantity, clear, total }),
    [lines, addItem, removeItem, setQuantity, clear, total]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
