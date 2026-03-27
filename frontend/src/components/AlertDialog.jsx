/**
 * AlertDialog — Bouton + modale de configuration des alertes de prix
 * 
 * Responsabilités :
 *  - Afficher un bouton cloche (🔔) sur chaque carte crypto
 *  - Ouvrir une modale pour définir un seuil haut et/ou bas
 *  - Afficher et supprimer les alertes actives
 *  - Remonter les nouvelles alertes au parent via callbacks
 * 
 * Composant "semi-contrôlé" :
 *  - État d'ouverture (open) : local
 *  - Valeurs des alertes : viennent du parent (usePriceAlerts)
 */

import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Box, Typography, IconButton, Stack, Chip,
} from '@mui/material'
import NotificationsIcon from '@mui/icons-material/Notifications'
import { useState } from 'react'

export default function AlertDialog({ coinId, currentPrice, alerts, onSet, onRemove }) {
  // ── État local ────────────────────────────────────────────────────────

  const [open, setOpen] = useState(false)
  
  // Valeurs saisies (strings car inputs type="number" retournent des strings)
  const [highVal, setHighVal] = useState('')
  const [lowVal, setLowVal] = useState('')

  // ── Données dérivées ──────────────────────────────────────────────────

  // alerts contient déjà les alertes pour ce coin spécifique (format: { high: {...}, low: {...} })
  const coinAlerts = alerts ?? {}
  
  // true si au moins une alerte est configurée
  const hasAnyAlert = coinAlerts.high || coinAlerts.low

  // ── Gestionnaires ─────────────────────────────────────────────────────

  const handleSave = () => {
    // Envoie uniquement les valeurs renseignées
    if (highVal) onSet(coinId, 'high', highVal)
    if (lowVal) onSet(coinId, 'low', lowVal)
    
    // Réinitialise les champs
    setHighVal('')
    setLowVal('')
    setOpen(false)
  }

  // ── Rendu ─────────────────────────────────────────────────────────────

  return (
    <>
      {/* Bouton cloche */}
      <IconButton
        size="small"
        onClick={(e) => {
          // stopPropagation : empêche la navigation vers la page détail
          // (la carte entière est cliquable via SortableCard)
          e.stopPropagation()
          setOpen(true)
        }}
        // Opacité réduite si aucune alerte configurée
        sx={{ opacity: hasAnyAlert ? 1 : 0.4 }}
        // Couleur orange si alerte active
        color={hasAnyAlert ? 'warning' : 'default'}
      >
        <NotificationsIcon fontSize="small" />
      </IconButton>

      {/* Modale de configuration */}
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        // stopPropagation : sécurité supplémentaire pour les clics dans la modale
        onClick={(e) => e.stopPropagation()}
        PaperProps={{ sx: { borderRadius: 3, minWidth: 340 } }}
      >
        <DialogTitle sx={{ pb: 1 }}>
          <Typography fontWeight={700}>🔔 Alertes — {coinId}</Typography>
          {/* Optional chaining : protège si currentPrice est undefined */}
          <Typography variant="body2" color="text.secondary">
            Prix actuel : ${currentPrice?.toLocaleString()}
          </Typography>
        </DialogTitle>

        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            {/* Section des alertes actives (rendu conditionnel) */}
            {(coinAlerts.high || coinAlerts.low) && (
              <Box>
                <Typography variant="caption" color="text.secondary" mb={1} display="block">
                  Alertes actives
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap">
                  {/* Chip seuil haut */}
                  {coinAlerts.high && (
                    <Chip
                      label={`↑ $${coinAlerts.high.threshold.toLocaleString()}`}
                      color="success"
                      size="small"
                      onDelete={() => onRemove(coinId, 'high')}
                    />
                  )}
                  
                  {/* Chip seuil bas */}
                  {coinAlerts.low && (
                    <Chip
                      label={`↓ $${coinAlerts.low.threshold.toLocaleString()}`}
                      color="error"
                      size="small"
                      onDelete={() => onRemove(coinId, 'low')}
                    />
                  )}
                </Stack>
              </Box>
            )}

            {/* Champ seuil haut : placeholder suggère +5% du prix actuel */}
            <TextField
              label="Alerte prix haut ($)"
              placeholder={`ex: ${Math.round((currentPrice ?? 0) * 1.05).toLocaleString()}`}
              value={highVal}
              onChange={(e) => setHighVal(e.target.value)}
              type="number"
              size="small"
              fullWidth
              slotProps={{
                input: {
                  startAdornment: <Typography sx={{ mr: 1 }}>↑</Typography>,
                },
              }}
            />

            {/* Champ seuil bas : placeholder suggère -5% du prix actuel */}
            <TextField
              label="Alerte prix bas ($)"
              placeholder={`ex: ${Math.round((currentPrice ?? 0) * 0.95).toLocaleString()}`}
              value={lowVal}
              onChange={(e) => setLowVal(e.target.value)}
              type="number"
              size="small"
              fullWidth
              slotProps={{
                input: {
                  startAdornment: <Typography sx={{ mr: 1 }}>↓</Typography>,
                },
              }}
            />
          </Stack>
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpen(false)} color="inherit">
            Annuler
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            // Désactivé si aucun champ n'est rempli
            disabled={!highVal && !lowVal}
          >
            Enregistrer
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
