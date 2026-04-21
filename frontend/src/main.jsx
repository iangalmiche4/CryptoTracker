import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App.jsx'
import CoinDetail from './pages/CoinDetail.jsx'
import Portfolio from './pages/Portfolio.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import { AuthProvider } from './contexts/AuthContext.jsx'
import { ThemeProvider } from './contexts/ThemeContext.jsx'
import { LanguageProvider } from './contexts/LanguageContext.jsx'
import { RETRY_CONFIG } from './config'
import './theme.css'

/**
 * QueryClient — instance globale de TanStack Query.
 *
 * defaultOptions s'appliquent à toutes les queries de l'app :
 *
 * staleTime: 60_000 — pendant 60s après un fetch réussi, TanStack considère
 *   les données "fraîches" et ne refetch PAS, même si le composant se remonte
 *   ou si l'utilisateur change d'onglet et revient.
 *
 * retry: 1 — en cas d'erreur, TanStack retente UNE fois avant d'exposer
 *   l'erreur au composant. Évite les faux négatifs sur coupures réseau brèves.
 *
 * refetchOnWindowFocus: false — par défaut TanStack refetch quand l'utilisateur
 *   revient sur l'onglet. On désactive car CoinGecko rate-limite agressivement
 *   et notre staleTime gère déjà la fraîcheur des données.
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime:           60_000,
      retry:               RETRY_CONFIG.attempts,
      retryDelay:          (attemptIndex) =>
        Math.min(
          RETRY_CONFIG.initialDelay * Math.pow(2, attemptIndex),
          RETRY_CONFIG.maxDelay
        ),
      refetchOnWindowFocus: false,
    },
  },
})

// Gestion globale des erreurs non capturées
window.addEventListener('unhandledrejection', event => {
  console.error('🚨 Unhandled promise rejection:', event.reason)
  // En production, envoyer à un service de monitoring (Sentry, LogRocket...)
  // Sentry.captureException(event.reason)
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/*
      QueryClientProvider injecte le queryClient dans tout l'arbre React
      via un Context — tous les useQuery() de l'app y accèdent sans prop drilling.
      Doit envelopper l'app entière, y compris le router.
    */}
    <QueryClientProvider client={queryClient}>
      {/*
        LanguageProvider gère le multi-langues (FR/EN)
        Système léger sans bibliothèque externe
      */}
      <LanguageProvider>
        {/*
          ThemeProvider personnalisé avec gestion Dark/Light mode
          Inclut automatiquement MUI ThemeProvider et CssBaseline
          Gère la persistance localStorage et les préférences système
        */}
        <ThemeProvider>
          {/*
            ErrorBoundary enveloppe toute l'application pour capturer les erreurs
            React qui se produisent n'importe où dans l'arbre de composants.
            Si une erreur survient, l'utilisateur voit une UI de secours au lieu
            d'un écran blanc.
          */}
          <ErrorBoundary>
            <BrowserRouter>
              {/*
                AuthProvider fournit le contexte d'authentification à toute l'app.
                Doit être à l'intérieur du Router pour pouvoir utiliser useNavigate.
              */}
              <AuthProvider>
              <Routes>
                {/* Routes publiques */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Routes protégées */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <App />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/coin/:id"
                  element={
                    <ProtectedRoute>
                      <CoinDetail />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/portfolio"
                  element={
                    <ProtectedRoute>
                      <Portfolio />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </AuthProvider>
          </BrowserRouter>
        </ErrorBoundary>
      </ThemeProvider>
      </LanguageProvider>
    </QueryClientProvider>
  </React.StrictMode>
)