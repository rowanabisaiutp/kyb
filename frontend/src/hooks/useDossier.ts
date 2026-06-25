import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getDossier, updateDossierStatus } from "../api/dossiers";
import type { DossierStatusUpdatePayload } from "../types";

export function useDossier(id: string) {
  return useQuery({
    queryKey: ["dossier", id],
    queryFn: () => getDossier(id),
    enabled: !!id,
  });
}

export function useUpdateDossierStatus(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DossierStatusUpdatePayload) => updateDossierStatus(dossierId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dossier", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
    },
  });
}
