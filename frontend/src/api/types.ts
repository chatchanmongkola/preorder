export interface User {
  id: number;
  line_user_id: string;
  display_name: string;
  picture_url: string | null;
  role: string;
}

export interface Round {
  id: number;
  name: string;
  opens_at: string;
  closes_at: string;
  status: "draft" | "open" | "closed";
}

export interface MenuItem {
  id: number;
  round_id: number;
  sku: string;
  name: string;
  price: number;
}

export interface OrderItem {
  id: number;
  menu_item_id: number;
  name: string;
  quantity: number;
  price_snapshot: number;
}

export interface Order {
  id: number;
  round_id: number;
  status: "pending" | "confirmed" | "cancelled";
  note: string | null;
  total_amount: number;
  items: OrderItem[];
}

export interface RoundSummaryItem {
  menu_item_id: number;
  name: string;
  quantity: number;
  subtotal: number;
}

export interface RoundSummary {
  round_id: number;
  round_name: string;
  status: string;
  total_orders: number;
  total_amount: number;
  items: RoundSummaryItem[];
}
