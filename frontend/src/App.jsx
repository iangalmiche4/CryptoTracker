/**
 * App — Dashboard principal avec drag & drop des cartes crypto
 * 
 * Fonctionnalités :
 * - Affichage des prix en temps réel avec refresh auto (60s)
 * - Réorganisation des cartes par drag & drop
 * - Ajout/suppression de coins
 * - Gestion des alertes de prix
 * - Synchronisation avec le backend PostgreSQL
 */

import { useState, useEffect, useMemo } from 'react'
import { Skeleton } from '@mui/material'

// dnd-kit : librairie de drag & drop
import {
  DndContext,
  DragOverlay,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core'

import {
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable'

import {
  Grid, Container, Typography, Box, Alert, IconButton, Tooltip,
} from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'

import { useCryptoPrices } from './hooks/useCryptoPrices'
import { useUserCoins, useUserAlerts } from './hooks/useUserData'
import { usePriceAlerts } from './hooks/usePriceAlerts'

import Header from './components/Header'
import SortableCard from './components/SortableCard'
import DragOverlayCard from './components/DragOverlayCard'
import RefreshBar from './components/RefreshBar'
import CoinSearch from './components/CoinSearch'
import AlertToast from './components/AlertToast'

export default function App() {
  // ── État local ────────────────────────────────────────────────────────

  const [activeId, setActiveId] = useState(null) // ID du coin en cours de drag
  const [refreshKey, setRefreshKey] = useState(0) // Incrémenté pour forcer le re-mount des cartes

  // ── Hooks backend ─────────────────────────────────────────────────────

  // Charger les coins et alertes depuis le backend
  const { coins, addCoin, removeCoin, reorderCoins, isAddingCoin } = useUserCoins()
  const { alerts: backendAlerts, getAlertsForCoin, createAlert, updateAlert, deleteAlert } = useUserAlerts()

  // Extraire les coin_ids pour le fetch des prix
  const coinIds = useMemo(() => coins.map(coin => coin.coin_id), [coins])

  // Fetch des prix depuis CoinGecko (via backend proxy)
  const { prices, loading, error, lastUpdate, refetch } = useCryptoPrices(coinIds)

  // Gestion des alertes déclenchées (notifications)
  const { triggered, dismissTriggered } = usePriceAlerts(prices, backendAlerts)

  // ── Configuration drag & drop ─────────────────────────────────────────

  const sensors = useSensors(
    // Seuil de 8px : évite de déclencher le drag sur un simple clic
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // ── Gestionnaires drag ────────────────────────────────────────────────

  const handleDragStart = ({ active }) => setActiveId(active.id)

  const handleDragEnd = ({ active, over }) => {
    setActiveId(null)
    if (!over || active.id === over.id) return

    // Réorganiser localement
    const oldIndex = coinIds.indexOf(active.id)
    const newIndex = coinIds.indexOf(over.id)
    const newOrder = arrayMove(coinIds, oldIndex, newIndex)

    // Synchroniser avec le backend
    reorderCoins(newOrder)
  }

  // ── Gestionnaires métier ──────────────────────────────────────────────

  const handleRefresh = () => {
    refetch()
    setRefreshKey(k => k + 1) // Force le re-mount → animation fadeIn
  }

  const handleAddCoin = (id) => {
    if (!coinIds.includes(id)) {
      addCoin({ coinId: id, position: coins.length })
    }
  }

  const handleRemoveCoin = (id) => {
    removeCoin(id)
  }

  // Adapter les alertes backend pour le format attendu par les composants
  const alertsMap = useMemo(() => {
    const map = {}
    backendAlerts.forEach(alert => {
      if (!map[alert.coin_id]) {
        map[alert.coin_id] = {}
      }
      map[alert.coin_id][alert.type] = {
        id: alert.id,
        threshold: alert.threshold,
      }
    })
    return map
  }, [backendAlerts])

  const handleSetAlert = (coinId, type, threshold) => {
    const existingAlerts = getAlertsForCoin(coinId)
    const existingAlert = existingAlerts.find(a => a.type === type)

    if (existingAlert) {
      // Mettre à jour l'alerte existante
      updateAlert({ alertId: existingAlert.id, threshold })
    } else {
      // Créer une nouvelle alerte
      createAlert({ coinId, type, threshold })
    }
  }

  const handleRemoveAlert = (coinId, type) => {
    const existingAlerts = getAlertsForCoin(coinId)
    const existingAlert = existingAlerts.find(a => a.type === type)

    if (existingAlert) {
      deleteAlert(existingAlert.id)
    }
  }

  // ── Rendu ─────────────────────────────────────────────────────────────

  return (
    <>
      {/* Header avec info utilisateur et déconnexion */}
      <Header />

      <Container maxWidth="lg" sx={{ py: 6 }}>

        {/* ── En-tête : titre + dernière mise à jour + recherche + refresh ── */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight={800}>Dashboard</Typography>
            <Typography variant="body2" color="text.secondary">
              {lastUpdate
                ? `Mis à jour : ${lastUpdate.toLocaleTimeString()}`
                : 'Chargement…'}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={2}>
            <CoinSearch activeCoinIds={coinIds} onAdd={handleAddCoin} />
            <Tooltip title="Rafraîchir maintenant">
              <IconButton onClick={handleRefresh} color="primary">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Barre de progression du countdown */}
        <RefreshBar onRefresh={handleRefresh} />

        {/* ── États de chargement et d'erreur ── */}

        {/* Skeletons lors du premier fetch */}
        {loading && coinIds.length === 0 && (
          <Grid container spacing={3}>
            {[1, 2, 3].map(i => (
              <Grid item xs={12} sm={6} md={4} key={i}>
                <Skeleton
                  variant="rectangular"
                  height={280}
                  sx={{
                    borderRadius: 3,
                    animation: 'pulse 1.5s ease-in-out infinite',
                    '@keyframes pulse': {
                      '0%, 100%': { opacity: 0.4 },
                      '50%': { opacity: 0.6 },
                    },
                  }}
                />
              </Grid>
            ))}
          </Grid>
        )}

        {/* Message si aucun coin */}
        {!loading && coinIds.length === 0 && (
          <Alert severity="info" sx={{ mb: 3 }}>
            Aucune cryptomonnaie suivie. Utilisez la recherche pour en ajouter.
          </Alert>
        )}

        {/* Bandeau d'erreur */}
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

        {/* ── Grille de cartes avec drag & drop ── */}
        {prices && coinIds.length > 0 && (
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <SortableContext items={coinIds} strategy={rectSortingStrategy}>
              <Grid container spacing={3}>
                {coinIds
                  .filter(id => prices[id])
                  .map(coinId => (
                    // Key combine coinId + refreshKey pour forcer le re-mount
                    <Grid item xs={12} sm={6} md={4} key={`${coinId}-${refreshKey}`}>
                      <SortableCard
                        coinId={coinId}
                        data={prices[coinId]}
                        alerts={alertsMap[coinId] || {}}
                        onSetAlert={handleSetAlert}
                        onRemoveAlert={handleRemoveAlert}
                        onRemove={() => handleRemoveCoin(coinId)}
                      />
                    </Grid>
                  ))}
              </Grid>
            </SortableContext>

            {/* Fantôme qui suit le curseur pendant le drag */}
            <DragOverlay adjustScale={false}>
              {activeId && prices[activeId] && (
                <DragOverlayCard
                  coinId={activeId}
                  data={prices[activeId]}
                  alerts={alertsMap[activeId] || {}}
                />
              )}
            </DragOverlay>
          </DndContext>
        )}

        {/* Toasts des alertes déclenchées */}
        <AlertToast triggered={triggered} onDismiss={dismissTriggered} />

      </Container>
    </>
  )
}

