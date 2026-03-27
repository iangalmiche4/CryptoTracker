/**
 * usePriceAlerts — Hook de détection des franchissements d'alertes
 *
 * Responsabilités :
 *  - Détecter les franchissements de seuil à chaque mise à jour des prix
 *  - Générer les notifications pour les alertes déclenchées
 *
 * Détection par franchissement (pas par état) :
 *  Une alerte se déclenche quand le prix TRAVERSE le seuil,
 *  pas quand il EST au-dessus/en-dessous.
 *  → Une seule notification par traversée (évite le spam)
 *
 * Note : Les alertes sont maintenant stockées dans le backend PostgreSQL
 */

import { useState, useEffect, useRef } from 'react'

// ── Hook principal ────────────────────────────────────────────────────────

export function usePriceAlerts(prices, backendAlerts = []) {
  // Tableau des alertes déclenchées : [{ id, coinId, type, threshold, price }, ...]
  const [triggered, setTriggered] = useState([])

  // Ref pour stocker les prix précédents (détection de franchissement)
  // useRef car la mise à jour ne doit pas déclencher de re-render
  const prevPricesRef = useRef({})

  // ── Effet : détection des franchissements ────────────────────────────

  useEffect(() => {
    if (!prices || backendAlerts.length === 0) return

    const newlyTriggered = []

    // Convertir les alertes backend en map pour accès rapide
    const alertsMap = {}
    backendAlerts.forEach(alert => {
      if (!alertsMap[alert.coin_id]) {
        alertsMap[alert.coin_id] = {}
      }
      alertsMap[alert.coin_id][alert.type] = {
        id: alert.id,
        threshold: alert.threshold,
      }
    })

    Object.entries(prices).forEach(([coinId, data]) => {
      const coinAlerts = alertsMap[coinId]
      if (!coinAlerts) return

      const currentPrice = data.usd
      const prevPrice = prevPricesRef.current[coinId]?.usd

      // Franchissement HAUT : prevPrice < seuil ET currentPrice >= seuil
      if (
        coinAlerts.high &&
        prevPrice &&
        prevPrice < coinAlerts.high.threshold &&
        currentPrice >= coinAlerts.high.threshold
      ) {
        newlyTriggered.push({
          id: `${coinId}-high-${Date.now()}`,
          coinId,
          type: 'high',
          threshold: coinAlerts.high.threshold,
          price: currentPrice,
        })
      }

      // Franchissement BAS : prevPrice > seuil ET currentPrice <= seuil
      if (
        coinAlerts.low &&
        prevPrice &&
        prevPrice > coinAlerts.low.threshold &&
        currentPrice <= coinAlerts.low.threshold
      ) {
        newlyTriggered.push({
          id: `${coinId}-low-${Date.now()}`,
          coinId,
          type: 'low',
          threshold: coinAlerts.low.threshold,
          price: currentPrice,
        })
      }
    })

    if (newlyTriggered.length > 0) {
      setTriggered(prev => [...prev, ...newlyTriggered])
    }

    // Mise à jour de la ref APRÈS la détection (ordre important)
    prevPricesRef.current = prices

  }, [prices, backendAlerts])

  // ── Fonctions de gestion ─────────────────────────────────────────────

  // Retire un toast de la liste des alertes déclenchées
  const dismissTriggered = (id) => {
    setTriggered(prev => prev.filter(t => t.id !== id))
  }

  return { triggered, dismissTriggered }
}