/**
 * useUserData.js — Hook pour gérer les données utilisateur (coins + alertes)
 * 
 * Utilise TanStack Query pour :
 * - Charger les données depuis le backend
 * - Synchroniser les mutations (ajout/suppression)
 * - Gérer le cache et les mises à jour optimistes
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getUserData, addCoin, removeCoin, reorderCoins, createAlert, updateAlert, deleteAlert } from '../api/user'
import { useAuth } from '../contexts/AuthContext'

/**
 * Hook pour récupérer toutes les données utilisateur
 */
export const useUserData = () => {
  const { isAuthenticated } = useAuth()

  return useQuery({
    queryKey: ['userData'],
    queryFn: getUserData,
    enabled: isAuthenticated, // Ne fetch que si connecté
    staleTime: 30_000, // 30s
    retry: 2,
  })
}

/**
 * Hook pour gérer les coins de l'utilisateur
 */
export const useUserCoins = () => {
  const queryClient = useQueryClient()
  const { data: userData } = useUserData()

  // Mutation pour ajouter un coin
  const addCoinMutation = useMutation({
    mutationFn: ({ coinId, position }) => addCoin(coinId, position),
    onSuccess: () => {
      // Invalider le cache pour recharger les données
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  // Mutation pour supprimer un coin
  const removeCoinMutation = useMutation({
    mutationFn: (coinId) => removeCoin(coinId),
    onMutate: async (coinId) => {
      // Annuler les requêtes en cours
      await queryClient.cancelQueries({ queryKey: ['userData'] })

      // Sauvegarder l'état précédent
      const previousData = queryClient.getQueryData(['userData'])

      // Mise à jour optimiste
      queryClient.setQueryData(['userData'], (old) => ({
        ...old,
        coins: old.coins.filter((coin) => coin.coin_id !== coinId),
      }))

      return { previousData }
    },
    onError: (err, coinId, context) => {
      // Rollback en cas d'erreur
      queryClient.setQueryData(['userData'], context.previousData)
    },
    onSettled: () => {
      // Recharger les données dans tous les cas
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  // Mutation pour réorganiser les coins
  const reorderCoinsMutation = useMutation({
    mutationFn: (coinIds) => reorderCoins(coinIds),
    onMutate: async (coinIds) => {
      await queryClient.cancelQueries({ queryKey: ['userData'] })
      const previousData = queryClient.getQueryData(['userData'])

      // Mise à jour optimiste
      queryClient.setQueryData(['userData'], (old) => {
        const reorderedCoins = coinIds.map((coinId, index) => {
          const coin = old.coins.find((c) => c.coin_id === coinId)
          return { ...coin, position: index }
        })
        return { ...old, coins: reorderedCoins }
      })

      return { previousData }
    },
    onError: (err, coinIds, context) => {
      queryClient.setQueryData(['userData'], context.previousData)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  return {
    coins: userData?.coins || [],
    addCoin: addCoinMutation.mutate,
    removeCoin: removeCoinMutation.mutate,
    reorderCoins: reorderCoinsMutation.mutate,
    isAddingCoin: addCoinMutation.isPending,
    isRemovingCoin: removeCoinMutation.isPending,
    isReordering: reorderCoinsMutation.isPending,
  }
}

/**
 * Hook pour gérer les alertes de l'utilisateur
 */
export const useUserAlerts = () => {
  const queryClient = useQueryClient()
  const { data: userData } = useUserData()

  // Mutation pour créer une alerte
  const createAlertMutation = useMutation({
    mutationFn: ({ coinId, type, threshold }) => createAlert(coinId, type, threshold),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  // Mutation pour modifier une alerte
  const updateAlertMutation = useMutation({
    mutationFn: ({ alertId, threshold }) => updateAlert(alertId, threshold),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  // Mutation pour supprimer une alerte
  const deleteAlertMutation = useMutation({
    mutationFn: (alertId) => deleteAlert(alertId),
    onMutate: async (alertId) => {
      await queryClient.cancelQueries({ queryKey: ['userData'] })
      const previousData = queryClient.getQueryData(['userData'])

      // Mise à jour optimiste
      queryClient.setQueryData(['userData'], (old) => ({
        ...old,
        alerts: old.alerts.filter((alert) => alert.id !== alertId),
      }))

      return { previousData }
    },
    onError: (err, alertId, context) => {
      queryClient.setQueryData(['userData'], context.previousData)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['userData'] })
    },
  })

  // Fonction helper pour obtenir les alertes d'un coin spécifique
  const getAlertsForCoin = (coinId) => {
    return (userData?.alerts || []).filter((alert) => alert.coin_id === coinId)
  }

  return {
    alerts: userData?.alerts || [],
    getAlertsForCoin,
    createAlert: createAlertMutation.mutate,
    updateAlert: updateAlertMutation.mutate,
    deleteAlert: deleteAlertMutation.mutate,
    isCreatingAlert: createAlertMutation.isPending,
    isUpdatingAlert: updateAlertMutation.isPending,
    isDeletingAlert: deleteAlertMutation.isPending,
  }
}

 
