/**
 * useCryptoPrices — Hook de fetch des prix crypto via TanStack Query
 * 
 * Responsabilités :
 *  - Fetcher les prix depuis /api/prices avec cache automatique
 *  - Filtrer immédiatement les coins supprimés (mise à jour optimiste)
 *  - Exposer refetch() pour le refresh manuel
 * 
 * Stratégie anti-rate-limit :
 *  - Backend : cache 30s + fallback données périmées si 429
 *  - Frontend : staleTime 90s + retry exponentiel (1s → 2s → 4s)
 *  - Suppression : filtre optimiste sans refetch
 */

import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { API_BASE_URL, STALE_TIME, RETRY_CONFIG } from '../config'

export function useCryptoPrices(coins) {
  // Clé de cache normalisée : ['ethereum', 'bitcoin'] === ['bitcoin', 'ethereum']
  // Évite un double fetch pour la même combinaison de coins
  const coinsKey = [...coins].sort().join(',')

  const {
    data,          // { bitcoin: {...}, ethereum: {...} }
    isPending,     // true avant le premier fetch réussi
    isError,       // true si échec après les retries
    dataUpdatedAt, // Timestamp du dernier fetch réussi
    refetch,       // Fonction pour forcer un fetch immédiat
  } = useQuery({
    queryKey: ['prices', coinsKey],
    
    queryFn: async () => {
      const startTime = performance.now()
      const response = await axios.get(`${API_BASE_URL}/api/prices?coins=${coinsKey}`)
      
      // Log des performances en dev uniquement
      if (import.meta.env.DEV) {
        console.log(`[useCryptoPrices] Fetch: ${(performance.now() - startTime).toFixed(0)}ms`)
      }
      
      return response.data
    },

    // Désactive la query si la liste est vide (évite erreur 422)
    enabled: coins.length > 0,
    
    // Données considérées fraîches pendant 90s
    staleTime: STALE_TIME.PRICES,
    
    // Retry avec backoff exponentiel : 1s → 2s → 4s (max 30s)
    // Améliore la résilience face aux erreurs réseau temporaires
    retry: RETRY_CONFIG.attempts,
    retryDelay: (attemptIndex) =>
      Math.min(
        RETRY_CONFIG.initialDelay * Math.pow(2, attemptIndex),
        RETRY_CONFIG.maxDelay
      ),
  })

  // Filtre optimiste : retire immédiatement les coins supprimés de l'UI
  // sans attendre le prochain fetch (évite 90s de latence visuelle)
  // useMemo évite de recréer l'objet à chaque render
  const prices = useMemo(() => {
    if (!data) return null
    const activeCoins = new Set(coins)
    return Object.fromEntries(
      Object.entries(data).filter(([id]) => activeCoins.has(id))
    )
  }, [data, coins])

  return {
    prices,
    loading: isPending && coins.length > 0,
    error: isError ? 'Impossible de contacter le backend.' : null,
    lastUpdate: dataUpdatedAt ? new Date(dataUpdatedAt) : null,
    refetch,
  }
}

