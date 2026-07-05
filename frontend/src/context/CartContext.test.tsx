import { describe, expect, it } from "vitest";
import { renderHook, act } from "@testing-library/react";
import type { ReactNode } from "react";

import { CartProvider, useCart } from "./CartContext";
import type { MenuItem } from "../api/types";

const wrapper = ({ children }: { children: ReactNode }) => <CartProvider>{children}</CartProvider>;

const itemA: MenuItem = { id: 1, round_id: 1, sku: "A", name: "ข้าวกะเพราหมู", price: 50 };
const itemB: MenuItem = { id: 2, round_id: 1, sku: "B", name: "ชาไทยเย็น", price: 25 };

describe("CartContext", () => {
  it("addItem adds a new line, then increments quantity on repeat calls", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA));
    expect(result.current.lines).toEqual([{ item: itemA, quantity: 1 }]);

    act(() => result.current.addItem(itemA));
    expect(result.current.lines).toEqual([{ item: itemA, quantity: 2 }]);
  });

  it("setQuantity adds a brand-new line for an item not yet in the cart (regression: used to silently no-op)", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.setQuantity(itemA, 3));

    expect(result.current.lines).toEqual([{ item: itemA, quantity: 3 }]);
  });

  it("setQuantity updates the quantity of an existing line", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA));
    act(() => result.current.setQuantity(itemA, 5));

    expect(result.current.lines).toEqual([{ item: itemA, quantity: 5 }]);
  });

  it("setQuantity to zero or below removes the line", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA));
    act(() => result.current.setQuantity(itemA, 0));

    expect(result.current.lines).toEqual([]);
  });

  it("removeItem removes a line entirely", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA));
    act(() => result.current.addItem(itemB));
    act(() => result.current.removeItem(itemA.id));

    expect(result.current.lines).toEqual([{ item: itemB, quantity: 1 }]);
  });

  it("total sums price * quantity across all lines", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA)); // 50
    act(() => result.current.setQuantity(itemA, 2)); // 100
    act(() => result.current.addItem(itemB)); // +25

    expect(result.current.total).toBe(125);
  });

  it("clear empties the cart", () => {
    const { result } = renderHook(() => useCart(), { wrapper });

    act(() => result.current.addItem(itemA));
    act(() => result.current.clear());

    expect(result.current.lines).toEqual([]);
    expect(result.current.total).toBe(0);
  });
});
