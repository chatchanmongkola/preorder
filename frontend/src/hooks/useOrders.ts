import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createOrder, deleteOrder, getMyOrders, updateOrder, type OrderItemInput } from "../api/orders";

export function useMyOrders() {
  return useQuery({ queryKey: ["orders", "my"], queryFn: getMyOrders });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ roundId, items, note }: { roundId: number; items: OrderItemInput[]; note?: string }) =>
      createOrder(roundId, items, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", "my"] });
    },
  });
}

export function useUpdateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      orderId,
      items,
      note,
    }: {
      orderId: number;
      items: OrderItemInput[];
      note?: string;
    }) => updateOrder(orderId, items, note),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", "my"] });
    },
  });
}

export function useDeleteOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (orderId: number) => deleteOrder(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", "my"] });
    },
  });
}
