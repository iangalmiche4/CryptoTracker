/**
 * RefreshBar — Barre de progression du countdown avant le prochain refresh
 * 
 * Affiche une barre qui se remplit sur 60 secondes + le nombre de secondes restantes.
 * Déclenche onRefresh automatiquement quand le countdown atteint 1.
 * 
 * Pourquoi déclencher à remaining === 1 et non === 0 ?
 * useCountdown repart à REFRESH_INTERVAL quand il atteint 1.
 * La valeur 0 n'est jamais émise.
 */

import { useEffect } from 'react'
import { Box, LinearProgress, Typography } from '@mui/material'
import { useCountdown } from '../hooks/useCountdown'
import { REFRESH_INTERVAL } from '../config'

export default function RefreshBar({ onRefresh }) {
  const remaining = useCountdown(REFRESH_INTERVAL)

  // Déclenche le refresh quand remaining atteint 1
  useEffect(() => {
    if (remaining === 1) onRefresh()
  }, [remaining, onRefresh])

  // Calcul de la progression : (secondes écoulées / total) × 100
  const progress = ((REFRESH_INTERVAL - remaining) / REFRESH_INTERVAL) * 100

  return (
    <Box sx={{ width: '100%', mb: 3 }}>
      <Box display="flex" justifyContent="space-between" mb={0.5}>
        <Typography variant="caption" color="text.secondary">
          Prochain refresh
        </Typography>
        <Typography variant="caption" color="primary.main" fontWeight={700}>
          {remaining}s
        </Typography>
      </Box>

      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          height: 4,
          borderRadius: 2,
          backgroundColor: 'rgba(108,99,255,0.15)',
          '& .MuiLinearProgress-bar': {
            borderRadius: 2,
            background: 'linear-gradient(90deg, #6C63FF, #a78bfa)',
          },
        }}
      />
    </Box>
  )
}