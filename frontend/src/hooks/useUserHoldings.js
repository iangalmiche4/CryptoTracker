import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { holdingsAPI } from '../api/holdings'

export function useUserHoldings() {
  const queryClient = useQueryClient()
  
  // Récupérer les holdings
  const { data: holdings = [], isLoading, error } = useQuery({
    queryKey: ['holdings'],
    queryFn: () => holdingsAPI.getAll().then(res => res.data)
  })
  
  // Récupérer le résumé
  const { data: summary } = useQuery({
    queryKey: ['holdings-summary'],
    queryFn: () => holdingsAPI.getSummary().then(res => res.data)
  })
  
  // Créer un holding
  const createMutation = useMutation({
    mutationFn: holdingsAPI.create,
    onSuccess: () => {
      queryClient.invalidateQueries(['holdings'])
      queryClient.invalidateQueries(['holdings-summary'])
    }
  })
  
  // Mettre à jour un holding
  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => holdingsAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['holdings'])
      queryClient.invalidateQueries(['holdings-summary'])
    }
  })
  
  // Supprimer un holding
  const deleteMutation = useMutation({
    mutationFn: holdingsAPI.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['holdings'])
      queryClient.invalidateQueries(['holdings-summary'])
    }
  })
  
  return {
    holdings,
    summary,
    isLoading,
    error,
    createHolding: createMutation.mutate,
    updateHolding: updateMutation.mutate,
    deleteHolding: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending
  }
}

