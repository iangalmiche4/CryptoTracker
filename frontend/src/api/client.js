/**
 * client.js — Client Axios configuré avec intercepteurs pour l'authentification
 * 
 * Fonctionnalités :
 * - Ajoute automatiquement le token JWT aux requêtes
 * - Gère l'expiration du token (redirection vers login)
 * - Centralise la configuration de base (URL, headers)
 */

import axios from 'axios'
import { API_BASE_URL } from '../config'

// Créer une instance Axios avec configuration de base
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur de requête : ajouter le token JWT si disponible
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur de réponse : gérer les erreurs d'authentification
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Si 401 Unauthorized, supprimer le token et rediriger vers login
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Rediriger vers login seulement si pas déjà sur la page de login
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient

