/**
 * Header.jsx — En-tête de l'application avec info utilisateur et toggle de thème
 *
 * Fonctionnalités :
 * - Affiche l'email de l'utilisateur
 * - Toggle Dark/Light mode avec animation fluide
 * - Sélecteur de langue (FR/EN)
 * - Bouton de déconnexion
 */

import { AppBar, Toolbar, Typography, Box, IconButton, Tooltip, useTheme as useMuiTheme, ToggleButtonGroup, ToggleButton } from '@mui/material'
import LogoutIcon from '@mui/icons-material/Logout'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { useTranslation } from '../contexts/LanguageContext'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const { user, logout } = useAuth()
  const { mode, toggleTheme } = useTheme()
  const { language, changeLanguage, t } = useTranslation()
  const muiTheme = useMuiTheme()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: 1,
        borderColor: 'divider',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            color: 'text.primary',
            fontWeight: 800,
            display: 'flex',
            alignItems: 'center',
            gap: 1,
          }}
        >
          {t('header.appName')}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
            {user?.email}
          </Typography>
          
          {/* Sélecteur de langue */}
          <ToggleButtonGroup
            value={language}
            exclusive
            onChange={(_, newLang) => { if (newLang) changeLanguage(newLang) }}
            size="small"
            sx={{
              '& .MuiToggleButtonGroup-grouped': {
                border: 1,
                borderColor: 'divider',
                '&:not(:first-of-type)': {
                  marginLeft: 0,
                  borderLeft: 1,
                  borderLeftColor: 'divider',
                },
              },
              '& .MuiToggleButton-root': {
                px: 1.5,
                py: 0.5,
                fontSize: '0.75rem',
                fontWeight: 600,
                minWidth: '40px',
                transition: 'all 0.2s',
                '&.Mui-selected': {
                  bgcolor: 'primary.main',
                  color: 'white',
                  borderColor: 'primary.main !important',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                },
              },
            }}
          >
            <ToggleButton value="fr">FR</ToggleButton>
            <ToggleButton value="en">EN</ToggleButton>
          </ToggleButtonGroup>
          
          {/* Toggle Dark/Light Mode */}
          <Tooltip title={mode === 'light' ? t('header.darkMode') : t('header.lightMode')}>
            <IconButton
              onClick={toggleTheme}
              sx={{
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'rotate(180deg)',
                  bgcolor: mode === 'light' ? 'rgba(108, 99, 255, 0.08)' : 'rgba(139, 132, 255, 0.12)',
                },
                '&:active': {
                  transform: 'rotate(180deg) scale(0.95)',
                },
              }}
            >
              {mode === 'light' ? (
                <DarkModeIcon
                  sx={{
                    color: 'primary.main',
                    animation: 'fadeIn 0.3s ease-in-out',
                    '@keyframes fadeIn': {
                      from: { opacity: 0, transform: 'rotate(-180deg)' },
                      to: { opacity: 1, transform: 'rotate(0deg)' },
                    },
                  }}
                />
              ) : (
                <LightModeIcon
                  sx={{
                    color: 'primary.main',
                    animation: 'fadeIn 0.3s ease-in-out',
                    '@keyframes fadeIn': {
                      from: { opacity: 0, transform: 'rotate(-180deg)' },
                      to: { opacity: 1, transform: 'rotate(0deg)' },
                    },
                  }}
                />
              )}
            </IconButton>
          </Tooltip>
          
          {/* Bouton de déconnexion */}
          <Tooltip title={t('header.logout')}>
            <IconButton
              onClick={handleLogout}
              color="error"
              sx={{
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'scale(1.1)',
                },
              }}
            >
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  )
}
