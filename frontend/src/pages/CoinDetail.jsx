/**
 * CoinDetail — Page de détail d'une cryptomonnaie
 *
 * Affiche :
 * - Graphique historique interactif (7/14/30/90 jours)
 * - Métriques de marché (market cap, volume, ATH, supply)
 * - Variations de prix (24h, 7j, 30j)
 * - Sentiment communautaire
 * - Description du coin
 */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { API_BASE_URL, STALE_TIME } from '../config'
import {
  Container, Box, Typography, Button, Grid,
  Card, CardContent, Chip, Divider,
  CircularProgress, Avatar, Skeleton,
  ToggleButton, ToggleButtonGroup, Alert,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import TwitterIcon from '@mui/icons-material/Twitter'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts'
import Header from '../components/Header'
import { useTranslation } from '../contexts/LanguageContext'

// ── Utilitaires ───────────────────────────────────────────────────────────

// Formate les grands nombres : 1 327 000 000 000 → "$1.41T"
function formatLarge(n) {
  if (!n) return '—'
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9)  return `$${(n / 1e9).toFixed(2)}B`
  if (n >= 1e6)  return `$${(n / 1e6).toFixed(2)}M`
  return `$${n.toLocaleString()}`
}

// ── Composants internes ───────────────────────────────────────────────────

// Badge coloré pour les variations de prix
function ChangeChip({ value }) {
  if (value == null) return <Typography color="text.disabled">—</Typography>
  const pos = value >= 0
  return (
    <Chip
      label={`${pos ? '+' : ''}${value.toFixed(2)}%`}
      color={pos ? 'success' : 'error'}
      size="small"
    />
  )
}

// Carte métrique avec label et valeur
function StatCard({ label, value, sub }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Typography variant="caption" color="text.secondary" display="block" mb={1}>
          {label}
        </Typography>
        <Typography variant="h6" fontWeight={700}>
          {value}
        </Typography>
        {sub && (
          <Typography variant="caption" color="text.secondary">{sub}</Typography>
        )}
      </CardContent>
    </Card>
  )
}

// Tooltip personnalisé pour le graphique Recharts
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <Box sx={{
      background: 'background.paper',
      border: '1px solid',
      borderColor: 'primary.main',
      borderRadius: 2,
      p: 1.5,
      boxShadow: 3,
    }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography variant="body2" fontWeight={700} color="primary.main">
        ${payload[0].value.toLocaleString()}
      </Typography>
    </Box>
  )
}

// ── Composant principal ───────────────────────────────────────────────────

export default function CoinDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [days, setDays] = useState(7)

  // Query détail : infos complètes du coin
  const {
    data: detail,
    isPending: loadingDetail,
  } = useQuery({
    queryKey: ['detail', id],
    queryFn: () => axios.get(`${API_BASE_URL}/api/detail/${id}`).then(r => r.data),
    staleTime: STALE_TIME.DETAIL,
  })

  // Query historique : points de prix sur N jours
  const { data: history = [] } = useQuery({
    queryKey: ['history', id, days],
    queryFn: () =>
      axios.get(`${API_BASE_URL}/api/history/${id}?days=${days}`).then(r => r.data),
    staleTime: STALE_TIME.DETAIL,
  })

  const hasValidData = detail && detail.market && detail.name

  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 6 }}>
        {/* Bouton retour */}
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/')}
          sx={{ mb: 4, borderRadius: 3 }}
          variant="outlined"
          color="inherit"
        >
          {t('coinDetail.backToDashboard')}
        </Button>

      {/* Spinner pendant le chargement */}
      {loadingDetail && (
        <Box display="flex" justifyContent="center" mt={8}>
          <CircularProgress />
        </Box>
      )}

      {/* Message si données invalides (rate limit sans cache) */}
      {!loadingDetail && detail && !hasValidData && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {t('coinDetail.loadError')}
        </Alert>
      )}

      {hasValidData && (
        <>
          {/* ── En-tête : logo + nom + prix + liens ── */}
          <Box display="flex" alignItems="center" gap={3} mb={5} flexWrap="wrap">
            <Avatar src={detail.image} sx={{ width: 72, height: 72 }} />

            <Box flex={1}>
              <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
                <Typography variant="h3" fontWeight={800}>{detail.name}</Typography>
                <Chip label={detail.symbol} variant="outlined" size="small" />
                <ChangeChip value={detail.market.change_24h} />
              </Box>
              <Typography variant="h4" fontWeight={800} mt={1}>
                ${detail.market.price_usd?.toLocaleString()}
              </Typography>
            </Box>

            {/* Liens externes */}
            <Box display="flex" gap={1} flexWrap="wrap">
              {detail.links.homepage && (
                <Button
                  size="small" variant="outlined" endIcon={<OpenInNewIcon />}
                  href={detail.links.homepage} target="_blank"
                  sx={{ borderRadius: 3 }}
                >
                  {t('coinDetail.officialWebsite')}
                </Button>
              )}
              {detail.links.twitter && (
                <Button
                  size="small" variant="outlined" startIcon={<TwitterIcon />}
                  href={`https://twitter.com/${detail.links.twitter}`}
                  target="_blank" sx={{ borderRadius: 3 }}
                >
                  @{detail.links.twitter}
                </Button>
              )}
            </Box>
          </Box>

          {/* ── Graphique historique ── */}
          <Card sx={{ mb: 4 }}>
            <CardContent sx={{ p: 3 }}>
              <Box display="flex" justifyContent="space-between"
                alignItems="center" mb={3} flexWrap="wrap" gap={2}>
                <Typography variant="h6" fontWeight={700}>
                  {t('coinDetail.priceHistory')}
                </Typography>

                {/* Sélecteur de période */}
                <ToggleButtonGroup
                  value={days}
                  exclusive
                  onChange={(_, v) => { if (v) setDays(v) }}
                  size="small"
                >
                  {[7, 14, 30, 90].map(d => (
                    <ToggleButton key={d} value={d} sx={{ px: 2, borderRadius: 2 }}>
                      {d}{t('coinDetail.days')}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
              </Box>

              {history.length > 0 ? (
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={history} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                    <defs>
                      {/* Dégradé violet sous la courbe */}
                      <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6C63FF" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6C63FF" stopOpacity={0} />
                      </linearGradient>
                    </defs>

                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    
                    <XAxis
                      dataKey="date"
                      tick={{ fill: '#888', fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    
                    <YAxis
                      domain={['auto', 'auto']}
                      tick={{ fill: '#888', fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={v => v >= 1000 ? `$${(v / 1000).toFixed(0)}k` : `$${v}`}
                      width={70}
                    />
                    
                    <RechartsTooltip content={<CustomTooltip />} />
                    
                    <Area
                      type="monotone"
                      dataKey="price"
                      stroke="#6C63FF"
                      strokeWidth={2.5}
                      fill="url(#priceGrad)"
                      dot={false}
                      activeDot={{ r: 5, fill: '#6C63FF' }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 2 }} />
              )}
            </CardContent>
          </Card>

          {/* ── Métriques de marché ── */}
          <Typography variant="h6" fontWeight={700} mb={2}>
            {t('coinDetail.marketMetrics')}
          </Typography>
          <Grid container spacing={2} mb={4}>
            {[
              { label: t('coinDetail.marketCap'), value: formatLarge(detail.market.market_cap) },
              { label: t('coinDetail.volume24h'), value: formatLarge(detail.market.volume_24h) },
              { label: t('coinDetail.fullyDilutedVal'), value: formatLarge(detail.market.fully_diluted_val) },
              {
                label: t('coinDetail.ath'),
                value: formatLarge(detail.market.ath),
                sub: detail.market.ath_change_pct
                  ? `${detail.market.ath_change_pct.toFixed(1)}% ${t('coinDetail.athChange')}`
                  : ''
              },
              {
                label: t('coinDetail.circulatingSupply'),
                value: detail.market.circulating_supply
                  ? `${(detail.market.circulating_supply / 1e6).toFixed(2)}M ${detail.symbol}`
                  : '—'
              },
            ].map(stat => (
              <Grid item xs={12} sm={6} md={4} key={stat.label}>
                <StatCard {...stat} />
              </Grid>
            ))}
          </Grid>

          {/* ── Variations de prix ── */}
          <Typography variant="h6" fontWeight={700} mb={2}>
            {t('coinDetail.priceChanges')}
          </Typography>
          <Card sx={{ mb: 4 }}>
            <CardContent sx={{ p: 3 }}>
              <Grid container spacing={4}>
                {[
                  { label: t('coinDetail.hours24'), value: detail.market.change_24h },
                  { label: t('coinDetail.days7'), value: detail.market.change_7d },
                  { label: t('coinDetail.days30'), value: detail.market.change_30d },
                ].map(({ label, value }) => (
                  <Grid item xs={12} sm={4} key={label}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" gap={1}>
                      <Typography color="text.secondary">{label}</Typography>
                      <ChangeChip value={value} />
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* ── Sentiment communautaire ── */}
          {detail.sentiment_up_pct != null && (
            <>
              <Typography variant="h6" fontWeight={700} mb={2}>
                {t('coinDetail.communitySentiment')}
              </Typography>
              <Card sx={{ mb: 4 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box display="flex" justifyContent="space-between" mb={1}>
                    <Typography variant="body2" color="success.main" fontWeight={600}>
                      {t('coinDetail.bullish')} {detail.sentiment_up_pct.toFixed(0)}%
                    </Typography>
                    <Typography variant="body2" color="error.main" fontWeight={600}>
                      {t('coinDetail.bearish')} {(100 - detail.sentiment_up_pct).toFixed(0)}%
                    </Typography>
                  </Box>
                  {/* Barre bicolore avec frontière nette */}
                  <Box sx={{
                    height: 10,
                    borderRadius: 5,
                    background: `linear-gradient(90deg,
                      #22c55e ${detail.sentiment_up_pct}%,
                      #ef4444 ${detail.sentiment_up_pct}%)`,
                  }} />
                </CardContent>
              </Card>
            </>
          )}

          {/* ── Description ── */}
          {detail.description && (
            <>
              <Divider sx={{ mb: 4, borderColor: 'rgba(255,255,255,0.07)' }} />
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Typography variant="h6" fontWeight={700}>
                  {t('coinDetail.about')} {detail.name}
                </Typography>
                <Typography variant="caption" color="text.disabled" sx={{ fontStyle: 'italic' }}>
                  {t('coinDetail.descriptionNote')}
                </Typography>
              </Box>
              <Typography
                variant="body2"
                color="text.secondary"
                lineHeight={1.8}
                sx={{ maxWidth: 800 }}
              >
                {detail.description}
              </Typography>
            </>
          )}
        </>
      )}
      </Container>
    </>
  )
}
