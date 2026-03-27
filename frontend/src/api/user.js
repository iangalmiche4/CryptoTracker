/**
 * user.js — API des données utilisateur
 * 
 * Fonctions pour gérer les coins et alertes de l'utilisateur
 */

import apiClient from './client'

// ── Données utilisateur ────────────────────────────────────────────────

/**
 * Récupérer toutes les données utilisateur (coins + alertes)
 * @returns {Promise<Object>} { user, coins, alerts }
 */
export const getUserData = async () => {
  const response = await apiClient.get('/api/user/data')
  return response.data
}

// ── Gestion des coins ──────────────────────────────────────────────────

/**
 * Ajouter un coin à suivre
 * @param {string} coinId - ID CoinGecko (ex: "bitcoin")
 * @param {number} position - Position dans la liste (optionnel)
 * @returns {Promise<Object>} Coin créé
 */
export const addCoin = async (coinId, position = null) => {
  const response = await apiClient.post('/api/user/coins', {
    coin_id: coinId,
    position,
  })
  return response.data
}

/**
 * Réorganiser les coins (après drag & drop)
 * @param {string[]} coinIds - Liste ordonnée des coin_ids
 * @returns {Promise<Object>} Message de succès
 */
export const reorderCoins = async (coinIds) => {
  const response = await apiClient.put('/api/user/coins/reorder', {
    coin_ids: coinIds,
  })
  return response.data
}

/**
 * Supprimer un coin
 * @param {string} coinId - ID CoinGecko
 * @returns {Promise<Object>} Message de succès
 */
export const removeCoin = async (coinId) => {
  const response = await apiClient.delete(`/api/user/coins/${coinId}`)
  return response.data
}

// ── Gestion des alertes ────────────────────────────────────────────────

/**
 * Créer une alerte de prix
 * @param {string} coinId - ID CoinGecko
 * @param {string} type - "high" ou "low"
 * @param {number} threshold - Seuil de prix en USD
 * @returns {Promise<Object>} Alerte créée
 */
export const createAlert = async (coinId, type, threshold) => {
  const response = await apiClient.post('/api/user/alerts', {
    coin_id: coinId,
    type,
    threshold,
  })
  return response.data
}

/**
 * Modifier le seuil d'une alerte
 * @param {number} alertId - ID de l'alerte
 * @param {number} threshold - Nouveau seuil
 * @returns {Promise<Object>} Alerte mise à jour
 */
export const updateAlert = async (alertId, threshold) => {
  const response = await apiClient.put(`/api/user/alerts/${alertId}`, {
    threshold,
  })
  return response.data
}

/**
 * Supprimer une alerte
 * @param {number} alertId - ID de l'alerte
 * @returns {Promise<Object>} Message de succès
 */
export const deleteAlert = async (alertId) => {
  const response = await apiClient.delete(`/api/user/alerts/${alertId}`)
  return response.data
}

 
