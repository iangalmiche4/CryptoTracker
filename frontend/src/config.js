/**
 * config.js — Configuration centralisée de l'application
 * 
 * Centralise toutes les constantes et variables d'environnement pour :
 *  1. Faciliter les changements de configuration (un seul fichier à modifier)
 *  2. Permettre des configurations différentes par environnement (dev/prod)
 *  3. Éviter la duplication de valeurs magiques dans le code
 * 
 * Les variables d'environnement sont préfixées par VITE_ pour être exposées
 * au client (convention Vite). Elles sont définies dans .env ou .env.local.
 */

// URL de base de l'API backend
// En développement : http://localhost:8000
// En production : remplacer par l'URL du backend déployé
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Intervalle de rafraîchissement automatique des prix en secondes
// Doit être aligné avec le TTL du cache backend (60s)
export const REFRESH_INTERVAL = 60

// Délai de debounce pour la recherche de coins en millisecondes
export const DEBOUNCE_MS = 400

// Longueur minimale de la requête de recherche avant de déclencher l'appel API
export const SEARCH_MIN_LENGTH = 2

// Durées de cache (staleTime) pour TanStack Query en millisecondes
// Pendant ce délai, les données sont considérées "fraîches" et ne sont pas re-fetchées
export const STALE_TIME = {
  // Prix : 90s — les prix changent rapidement mais le backend cache déjà 30s
  PRICES: 90_000,
  
  // Recherche : 5min — les coins disponibles sur CoinGecko changent rarement
  SEARCH: 5 * 60 * 1000,
  
  // Détail et historique : 5min — les métriques de marché évoluent lentement
  DETAIL: 5 * 60 * 1000,
}

// Coins affichés par défaut au premier chargement de l'application
export const DEFAULT_COINS = ['bitcoin', 'ethereum', 'solana']

// Configuration des retries pour les appels API
export const RETRY_CONFIG = {
  // Nombre de tentatives en cas d'échec
  attempts: 3,
  
  // Délai initial entre les tentatives en ms (doublé à chaque retry)
  initialDelay: 1000,
  
  // Délai maximum entre les tentatives en ms
  maxDelay: 30000,
}
