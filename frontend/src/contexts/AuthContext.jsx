/**
 * AuthContext.jsx — Contexte d'authentification global
 * 
 * Fournit l'état d'authentification à toute l'application :
 * - Utilisateur connecté
 * - Token JWT
 * - Fonctions de login/logout/register
 * - État de chargement
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { login as apiLogin, register as apiRegister, getCurrentUser, logout as apiLogout } from '../api/auth'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Charger l'utilisateur au montage si un token existe
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const userData = await getCurrentUser()
          setUser(userData)
        } catch (err) {
          console.error('Failed to load user:', err)
          // Token invalide ou expiré
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    loadUser()
  }, [token])

  /**
   * Inscription d'un nouvel utilisateur
   */
  const register = async (email, password) => {
    try {
      setError(null)
      setLoading(true)
      
      // 1. Créer le compte
      await apiRegister(email, password)
      
      // 2. Se connecter automatiquement
      const { access_token } = await apiLogin(email, password)
      
      // 3. Sauvegarder le token
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // 4. Charger les données utilisateur
      const userData = await getCurrentUser()
      setUser(userData)
      
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed'
      setError(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  /**
   * Connexion d'un utilisateur
   */
  const login = async (email, password) => {
    try {
      setError(null)
      setLoading(true)
      
      // 1. Se connecter
      const { access_token } = await apiLogin(email, password)
      
      // 2. Sauvegarder le token
      localStorage.setItem('token', access_token)
      setToken(access_token)
      
      // 3. Charger les données utilisateur
      const userData = await getCurrentUser()
      setUser(userData)
      
      return { success: true }
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed'
      setError(message)
      return { success: false, error: message }
    } finally {
      setLoading(false)
    }
  }

  /**
   * Déconnexion
   */
  const logout = () => {
    apiLogout()
    setToken(null)
    setUser(null)
    setError(null)
  }

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

 
