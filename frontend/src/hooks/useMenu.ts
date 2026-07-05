import { useQuery } from "@tanstack/react-query";

import { getMenu } from "../api/menu";

export function useMenu(roundId: number | undefined) {
  return useQuery({
    queryKey: ["menu", roundId],
    queryFn: () => getMenu(roundId as number),
    enabled: roundId !== undefined,
  });
}
