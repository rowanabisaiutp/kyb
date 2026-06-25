import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getReconciliation, runReconciliation } from "../api/reconciliation";

export function useReconciliation(dossierId: string) {
  return useQuery({
    queryKey: ["reconciliation", dossierId],
    queryFn: () => getReconciliation(dossierId),
    enabled: !!dossierId,
  });
}

export function useRunReconciliation(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => runReconciliation(dossierId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reconciliation", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dossier", dossierId] });
    },
  });
}
