import { useQuery } from "@tanstack/react-query";

import { getCurrentRound, getRound, getRoundSummary } from "../api/rounds";

export function useCurrentRound() {
  return useQuery({ queryKey: ["rounds", "current"], queryFn: getCurrentRound, retry: false });
}

export function useRound(roundId: number | undefined) {
  return useQuery({
    queryKey: ["rounds", roundId],
    queryFn: () => getRound(roundId as number),
    enabled: roundId !== undefined,
  });
}

export function useRoundSummary(roundId: number | undefined) {
  return useQuery({
    queryKey: ["rounds", roundId, "summary"],
    queryFn: () => getRoundSummary(roundId as number),
    enabled: roundId !== undefined,
  });
}
