/**
 * useCountdown — Hook de compte à rebours en secondes
 * 
 * Décompte de `seconds` jusqu'à 1, puis repart de `seconds` en boucle.
 * Nettoie l'intervalle au démontage (évite les memory leaks).
 * 
 * Pourquoi s'arrêter à 1 et non 0 ?
 * Un setInterval à 1000ms n'est pas précis à la milliseconde.
 * S'arrêter à 1 et repartir immédiatement est plus prévisible.
 */

import { useState, useEffect } from 'react'
import { REFRESH_INTERVAL } from '../config'

export function useCountdown(seconds = REFRESH_INTERVAL) {
  const [remaining, setRemaining] = useState(seconds)

  useEffect(() => {
    // Reset immédiat si la durée change
    setRemaining(seconds)

    const id = setInterval(() => {
      setRemaining(prev => {
        // Repart de `seconds` quand on atteint 1 → boucle infinie
        if (prev <= 1) return seconds
        return prev - 1
      })
    }, 1000)

    // Cleanup : annule l'intervalle au démontage ou si `seconds` change
    return () => clearInterval(id)

  }, [seconds])

  return remaining
}
