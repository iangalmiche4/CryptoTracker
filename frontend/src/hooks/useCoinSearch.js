/**
 * useCoinSearch — Hook de recherche de coins avec TanStack Query
 * 
 * Combine debounce (400ms) + TanStack Query :
 * - Debounce : stabilise la query key avant le fetch
 * - TanStack : cache 5min, déduplication, états automatiques
 * 
 * Sans debounce, taper "bitcoin" créerait 7 queries successives
 * ("b", "bi", "bit"...) → 7 appels réseau inutiles
 */

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { API_BASE_URL, DEBOUNCE_MS, SEARCH_MIN_LENGTH, STALE_TIME } from '../config'

export function useCoinSearch(query) {
  // Valeur stabilisée de query après 400ms sans frappe
  const [debouncedQuery, setDebouncedQuery] = useState(query)

  useEffect(() => {
    // Reset immédiat si le terme est trop court
    if (query.trim().length < SEARCH_MIN_LENGTH) {
      setDebouncedQuery('')
      return
    }
    const timer = setTimeout(() => setDebouncedQuery(query), DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [query])

  const { data, isPending } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () =>
      axios.get(`${API_BASE_URL}/api/search?q=${debouncedQuery}`).then(r => r.data),
    enabled: debouncedQuery.trim().length >= SEARCH_MIN_LENGTH,
    staleTime: STALE_TIME.SEARCH,
    placeholderData: [],
  })

  return {
    results: data ?? [],
    // searching : true pendant le debounce OU pendant le fetch
    searching: (query !== debouncedQuery && query.trim().length >= SEARCH_MIN_LENGTH) || isPending,
  }
}

