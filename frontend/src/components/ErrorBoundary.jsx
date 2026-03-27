/**
 * ErrorBoundary.jsx — Gestion des erreurs React
 *
 * Capture les erreurs JavaScript dans l'arbre de composants et affiche une UI
 * de secours au lieu de crasher toute l'application.
 *
 * Limitations : ne capture PAS les erreurs dans les event handlers, async code,
 * SSR, ou dans l'ErrorBoundary lui-même.
 *
 * Doit être un class component (les hooks ne supportent pas getDerivedStateFromError).
 */

import { Component } from 'react'
import { Alert, Button, Box, Typography } from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'

export default class ErrorBoundary extends Component {
  
  state = {
    hasError: false,
    error: null,
  }

  // Appelé pendant le rendu quand une erreur est lancée 
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  // Appelé après capture pour logging/monitoring (Sentry, etc.)
  componentDidCatch(error, errorInfo) {
    console.error('🚨 Error caught by ErrorBoundary:', error)
    console.error('📍 Component stack:', errorInfo.componentStack)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            p: 4,
            textAlign: 'center',
          }}
        >
          <Alert
            severity="error"
            sx={{
              mb: 3,
              maxWidth: 600,
              width: '100%',
            }}
          >
            <Typography variant="h6" fontWeight={700} mb={1}>
              Une erreur est survenue
            </Typography>
            <Typography variant="body2" color="text.secondary">
              L'application a rencontré un problème inattendu.
              Veuillez rafraîchir la page pour continuer.
            </Typography>
          </Alert>

          {/* Message d'erreur technique (dev uniquement) */}
          {import.meta.env.DEV && this.state.error && (
            <Box
              sx={{
                mb: 3,
                p: 2,
                backgroundColor: 'rgba(255,0,0,0.1)',
                borderRadius: 2,
                maxWidth: 600,
                width: '100%',
                textAlign: 'left',
              }}
            >
              <Typography
                variant="caption"
                component="pre"
                sx={{
                  fontFamily: 'monospace',
                  fontSize: 11,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {this.state.error.toString()}
              </Typography>
            </Box>
          )}

          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={this.handleReset}
            size="large"
          >
            Rafraîchir la page
          </Button>
        </Box>
      )
    }

    return this.props.children
  }
}