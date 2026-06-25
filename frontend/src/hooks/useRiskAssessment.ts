import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { calculateRisk, getLatestRiskAssessment } from "../api/risk";

export function useLatestRiskAssessment(dossierId: string) {
  return useQuery({
    queryKey: ["risk-assessment", dossierId, "latest"],
    queryFn: () => getLatestRiskAssessment(dossierId),
    enabled: !!dossierId,
  });
}

export function useCalculateRisk(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => calculateRisk(dossierId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["risk-assessment", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dossier", dossierId] });
    },
  });
}
