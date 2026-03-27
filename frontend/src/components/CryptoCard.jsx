/**
 * CryptoCard — Carte d'affichage d'une cryptomonnaie
 * 
 * Affiche : nom, prix, variation 24h, market cap
 * Adapte son apparence selon la tendance (vert/rouge)
 * Intègre le bouton d'alerte (AlertDialog)
 * Animation fadeIn à chaque (re)montage
 */

import {
  Card, CardContent, Typography, Box, Chip, Divider,
} from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import AlertDialog from './AlertDialog'

// ── Constantes ────────────────────────────────────────────────────────────

// Symboles typographiques des principales cryptos
const COIN_EMOJI = {
  bitcoin: '₿',
  ethereum: 'Ξ',
  solana: '◎',
}

// ── Utilitaires ───────────────────────────────────────────────────────────

// Formate les grands nombres : 1 327 000 000 000 → "$1.41T"
function formatLarge(n) {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`
  return `$${n.toLocaleString()}`
}

// ── Composant principal ───────────────────────────────────────────────────

export default function CryptoCard({ coinId, data, alerts, onSetAlert, onRemoveAlert }) {
  const change = data.usd_24h_change
  const isPositive = change >= 0

  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: isPositive ? 'success.dark' : 'error.dark',
        transition: 'transform 0.2s, opacity 0.3s',
        
        // Animation fadeIn à chaque montage (refreshKey change dans App.jsx)
        animation: 'fadeIn 0.4s ease-in-out',
        '@keyframes fadeIn': {
          from: { opacity: 0, transform: 'translateY(8px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        
        '&:hover': { transform: 'translateY(-4px)' },
      }}
    >
      <CardContent sx={{ p: 4 }}>
        {/* En-tête : nom + cloche + variation */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} gap={2}>
          <Typography variant="h5" fontWeight={700} textTransform="capitalize">
            {COIN_EMOJI[coinId] ?? '🪙'} {coinId}
          </Typography>

          <Box display="flex" alignItems="center" gap={1}>
            <AlertDialog
              coinId={coinId}
              currentPrice={data.usd}
              alerts={alerts}
              onSet={onSetAlert}
              onRemove={onRemoveAlert}
            />

            <Chip
              icon={isPositive ? <TrendingUpIcon /> : <TrendingDownIcon />}
              label={`${isPositive ? '+' : ''}${change.toFixed(2)}%`}
              color={isPositive ? 'success' : 'error'}
              size="small"
            />
          </Box>
        </Box>

        {/* Prix principal */}
        <Typography variant="h3" fontWeight={800} mb={3}>
          ${data.usd.toLocaleString()}
        </Typography>

        <Divider sx={{ mb: 3, borderColor: 'rgba(255,255,255,0.07)' }} />

        {/* Market cap */}
        <MetricRow label="Market cap" value={formatLarge(data.usd_market_cap)} />
      </CardContent>
    </Card>
  )
}

// ── Composant interne ─────────────────────────────────────────────────────

// Ligne label/valeur pour les métriques
function MetricRow({ label, value }) {
  return (
    <Box display="flex" justifyContent="space-between" alignItems="center">
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={600}>{value}</Typography>
    </Box>
  )
}
