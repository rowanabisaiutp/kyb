import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getFiscalListsStatus, listFiscalChecks, runFiscalCheck } from "../api/fiscal";

export function useFiscalChecks(dossierId: string) {
  return useQuery({
    queryKey: ["fiscal-checks", dossierId],
    queryFn: () => listFiscalChecks(dossierId),
    enabled: !!dossierId,
  });
}

export function useRunFiscalCheck(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => runFiscalCheck(dossierId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fiscal-checks", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dossier", dossierId] });
    },
  });
}

export function useFiscalListsStatus() {
  return useQuery({
    queryKey: ["fiscal-lists-status"],
    queryFn: getFiscalListsStatus,
  });
}
