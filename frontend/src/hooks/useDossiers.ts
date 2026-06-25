import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createDossier, deleteDossier, getDossierStats, listDossiers } from "../api/dossiers";
import type { DossierCreatePayload } from "../types";

export function useDossiers(params?: { status?: string; search?: string }) {
  return useQuery({
    queryKey: ["dossiers", params],
    queryFn: () => listDossiers(params),
  });
}

export function useDossierStats() {
  return useQuery({
    queryKey: ["dossiers", "stats"],
    queryFn: getDossierStats,
  });
}

export function useCreateDossier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DossierCreatePayload) => createDossier(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
    },
  });
}

export function useDeleteDossier() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteDossier(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dossiers"] });
    },
  });
}
