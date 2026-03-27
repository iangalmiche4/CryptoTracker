/**
 * auth.js — API d'authentification
 * 
 * Fonctions pour interagir avec les endpoints d'authentification du backend
 */

import apiClient from './client'

/**
 * Inscription d'un nouvel utilisateur
 * @param {string} email - Email de l'utilisateur
 * @param {string} password - Mot de passe (min 8 caractères)
 * @returns {Promise<Object>} Données de l'utilisateur créé
 */
export const register = async (email, password) => {
  const response = await apiClient.post('/api/auth/register', {
    email,
    password,
  })
  return response.data
}

/**
 * Connexion d'un utilisateur
 * @param {string} email - Email de l'utilisateur
 * @param {string} password - Mot de passe
 * @returns {Promise<Object>} Token JWT et type
 */
export const login = async (email, password) => {
  // L'endpoint login attend form-data, pas JSON
  const formData = new URLSearchParams()
  formData.append('username', email) // OAuth2 utilise 'username' même pour l'email
  formData.append('password', password)

  const response = await apiClient.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
  return response.data
}

/**
 * Récupérer les informations de l'utilisateur courant
 * @returns {Promise<Object>} Données de l'utilisateur
 */
export const getCurrentUser = async () => {
  const response = await apiClient.get('/api/auth/me')
  return response.data
}

/**
 * Déconnexion (côté client uniquement, pas d'endpoint backend)
 */
export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}
