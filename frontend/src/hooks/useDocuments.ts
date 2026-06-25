import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  deleteDocument,
  getDocumentChecklist,
  listDocuments,
  uploadDocument,
} from "../api/documents";

export function useDocuments(dossierId: string) {
  return useQuery({
    queryKey: ["documents", dossierId],
    queryFn: () => listDocuments(dossierId),
    enabled: !!dossierId,
  });
}

export function useDocumentChecklist(dossierId: string) {
  return useQuery({
    queryKey: ["documents", dossierId, "checklist"],
    queryFn: () => getDocumentChecklist(dossierId),
    enabled: !!dossierId,
  });
}

export function useUploadDocument(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      file,
      documentType,
      fechaEmision,
      fechaVencimiento,
    }: {
      file: File;
      documentType: string;
      fechaEmision?: string;
      fechaVencimiento?: string;
    }) =>
      uploadDocument(dossierId, file, documentType, {
        fecha_emision: fechaEmision,
        fecha_vencimiento: fechaVencimiento,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", dossierId] });
      queryClient.invalidateQueries({ queryKey: ["dossier", dossierId] });
    },
  });
}

export function useDeleteDocument(dossierId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) => deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents", dossierId] });
    },
  });
}
