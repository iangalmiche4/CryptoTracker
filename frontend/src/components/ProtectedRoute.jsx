/**
 * ProtectedRoute.jsx — Composant pour protéger les routes
 * 
 * Redirige vers /login si l'utilisateur n'est pas authentifié
 * Affiche un loader pendant la vérification de l'authentification
 */

import { Navigate } from 'react-router-dom'
import { Box, CircularProgress } from '@mui/material'
import { useAuth } from '../contexts/AuthContext'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()

  // Afficher un loader pendant la vérification
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress size={60} />
      </Box>
    )
  }

  // Rediriger vers login si non authentifié
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Afficher le contenu si authentifié
  return children
}

 
