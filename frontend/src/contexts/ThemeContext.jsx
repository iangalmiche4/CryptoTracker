/**
 * ThemeContext — Gestion du mode Dark/Light
 * 
 * Fonctionnalités :
 * - Détection automatique des préférences système
 * - Persistance dans localStorage
 * - Transitions fluides entre les modes
 * - Support des thèmes personnalisés MUI
 * - Synchronisation entre onglets
 */

import { createContext, useContext, useState, useEffect, useMemo } from 'react'
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles'
import { CssBaseline } from '@mui/material'

const ThemeContext = createContext()

// ── Configuration des thèmes ──────────────────────────────────────────

const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // ── Light Mode ──
          primary: {
            main: '#6C63FF',
            light: '#8B84FF',
            dark: '#5449CC',
            contrastText: '#FFFFFF',
          },
          secondary: {
            main: '#FF6584',
            light: '#FF8BA0',
            dark: '#CC5169',
            contrastText: '#FFFFFF',
          },
          background: {
            default: '#F8F9FA',
            paper: '#FFFFFF',
            elevated: '#FFFFFF',
          },
          text: {
            primary: '#1A1A1A',
            secondary: '#6B7280',
            disabled: '#9CA3AF',
          },
          divider: '#E5E7EB',
          success: {
            main: '#10B981',
            light: '#34D399',
            dark: '#059669',
          },
          error: {
            main: '#EF4444',
            light: '#F87171',
            dark: '#DC2626',
          },
          warning: {
            main: '#F59E0B',
            light: '#FBBF24',
            dark: '#D97706',
          },
          info: {
            main: '#3B82F6',
            light: '#60A5FA',
            dark: '#2563EB',
          },
        }
      : {
          // ── Dark Mode ──
          primary: {
            main: '#8B84FF',
            light: '#A39FFF',
            dark: '#6C63FF',
            contrastText: '#FFFFFF',
          },
          secondary: {
            main: '#FF8BA0',
            light: '#FFA5B8',
            dark: '#FF6584',
            contrastText: '#FFFFFF',
          },
          background: {
            default: '#0F0F0F',
            paper: '#1A1A1A',
            elevated: '#242424',
          },
          text: {
            primary: '#F9FAFB',
            secondary: '#D1D5DB',
            disabled: '#6B7280',
          },
          divider: '#374151',
          success: {
            main: '#34D399',
            light: '#6EE7B7',
            dark: '#10B981',
          },
          error: {
            main: '#F87171',
            light: '#FCA5A5',
            dark: '#EF4444',
          },
          warning: {
            main: '#FBBF24',
            light: '#FCD34D',
            dark: '#F59E0B',
          },
          info: {
            main: '#60A5FA',
            light: '#93C5FD',
            dark: '#3B82F6',
          },
        }),
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 800,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 700,
    },
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: mode === 'light' 
    ? [
        'none',
        '0px 2px 4px rgba(0,0,0,0.05)',
        '0px 4px 8px rgba(0,0,0,0.08)',
        '0px 8px 16px rgba(0,0,0,0.1)',
        '0px 12px 24px rgba(0,0,0,0.12)',
        '0px 16px 32px rgba(0,0,0,0.14)',
        '0px 20px 40px rgba(0,0,0,0.16)',
        '0px 24px 48px rgba(0,0,0,0.18)',
        '0px 28px 56px rgba(0,0,0,0.2)',
        '0px 32px 64px rgba(0,0,0,0.22)',
        '0px 36px 72px rgba(0,0,0,0.24)',
        '0px 40px 80px rgba(0,0,0,0.26)',
        '0px 44px 88px rgba(0,0,0,0.28)',
        '0px 48px 96px rgba(0,0,0,0.3)',
        '0px 52px 104px rgba(0,0,0,0.32)',
        '0px 56px 112px rgba(0,0,0,0.34)',
        '0px 60px 120px rgba(0,0,0,0.36)',
        '0px 64px 128px rgba(0,0,0,0.38)',
        '0px 68px 136px rgba(0,0,0,0.4)',
        '0px 72px 144px rgba(0,0,0,0.42)',
        '0px 76px 152px rgba(0,0,0,0.44)',
        '0px 80px 160px rgba(0,0,0,0.46)',
        '0px 84px 168px rgba(0,0,0,0.48)',
        '0px 88px 176px rgba(0,0,0,0.5)',
        '0px 92px 184px rgba(0,0,0,0.52)',
      ]
    : [
        'none',
        '0px 2px 4px rgba(0,0,0,0.3)',
        '0px 4px 8px rgba(0,0,0,0.35)',
        '0px 8px 16px rgba(0,0,0,0.4)',
        '0px 12px 24px rgba(0,0,0,0.45)',
        '0px 16px 32px rgba(0,0,0,0.5)',
        '0px 20px 40px rgba(0,0,0,0.55)',
        '0px 24px 48px rgba(0,0,0,0.6)',
        '0px 28px 56px rgba(0,0,0,0.65)',
        '0px 32px 64px rgba(0,0,0,0.7)',
        '0px 36px 72px rgba(0,0,0,0.75)',
        '0px 40px 80px rgba(0,0,0,0.8)',
        '0px 44px 88px rgba(0,0,0,0.85)',
        '0px 48px 96px rgba(0,0,0,0.9)',
        '0px 52px 104px rgba(0,0,0,0.95)',
        '0px 56px 112px rgba(0,0,0,1)',
        '0px 60px 120px rgba(0,0,0,1)',
        '0px 64px 128px rgba(0,0,0,1)',
        '0px 68px 136px rgba(0,0,0,1)',
        '0px 72px 144px rgba(0,0,0,1)',
        '0px 76px 152px rgba(0,0,0,1)',
        '0px 80px 160px rgba(0,0,0,1)',
        '0px 84px 168px rgba(0,0,0,1)',
        '0px 88px 176px rgba(0,0,0,1)',
        '0px 92px 184px rgba(0,0,0,1)',
      ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          transition: 'background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1), color 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          scrollbarWidth: 'thin',
          scrollbarColor: mode === 'light' ? '#CBD5E1 #F1F5F9' : '#4B5563 #1F2937',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: mode === 'light' ? '#F1F5F9' : '#1F2937',
          },
          '&::-webkit-scrollbar-thumb': {
            background: mode === 'light' ? '#CBD5E1' : '#4B5563',
            borderRadius: '4px',
            '&:hover': {
              background: mode === 'light' ? '#94A3B8' : '#6B7280',
            },
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: mode === 'light' 
              ? '0px 12px 24px rgba(0,0,0,0.12)' 
              : '0px 12px 24px rgba(0,0,0,0.45)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '10px 24px',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          transition: 'background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
  },
})

// ── Provider Component ────────────────────────────────────────────────

export function ThemeProvider({ children }) {
  // Détection des préférences système
  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches

  // État du mode (avec persistance localStorage)
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem('theme-mode')
    return savedMode || (prefersDarkMode ? 'dark' : 'light')
  })

  // Créer le thème MUI
  const theme = useMemo(() => createTheme(getDesignTokens(mode)), [mode])

  // Toggle entre light et dark
  const toggleTheme = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme-mode', newMode)
      return newMode
    })
  }

  // Setter direct du mode
  const setThemeMode = (newMode) => {
    if (newMode === 'light' || newMode === 'dark') {
      setMode(newMode)
      localStorage.setItem('theme-mode', newMode)
    }
  }

  // Écouter les changements de préférences système
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e) => {
      // Ne changer que si l'utilisateur n'a pas de préférence sauvegardée
      const savedMode = localStorage.getItem('theme-mode')
      if (!savedMode) {
        setMode(e.matches ? 'dark' : 'light')
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // Synchronisation entre onglets
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'theme-mode' && e.newValue) {
        setMode(e.newValue)
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  // Ajouter une classe au body pour les transitions CSS globales
  useEffect(() => {
    document.body.classList.add('theme-transition')
    document.documentElement.setAttribute('data-theme', mode)
    
    // Retirer la classe après la transition pour éviter les ralentissements
    const timer = setTimeout(() => {
      document.body.classList.remove('theme-transition')
    }, 300)

    return () => clearTimeout(timer)
  }, [mode])

  const value = {
    mode,
    toggleTheme,
    setThemeMode,
    isDark: mode === 'dark',
    isLight: mode === 'light',
  }

  return (
    <ThemeContext.Provider value={value}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  )
}

// ── Hook personnalisé ─────────────────────────────────────────────────

export function useTheme() {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

