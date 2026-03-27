/**
 * SortableCard — Wrapper drag & drop + navigation autour de CryptoCard
 * 
 * Rend CryptoCard "draggable" via dnd-kit
 * Affiche un handle de drag (⠿) et un chip de suppression
 * Navigue vers /coin/:id au clic sur la carte
 * Bloque la navigation pendant un drag
 */

import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useNavigate } from 'react-router-dom'
import { Box, Chip } from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import CryptoCard from './CryptoCard'

export default function SortableCard({
  coinId, data, alerts, onSetAlert, onRemoveAlert, onRemove
}) {
  const navigate = useNavigate()

  // ── Intégration dnd-kit ───────────────────────────────────────────────

  const {
    attributes,  // Props d'accessibilité (aria-*, role, tabIndex)
    listeners,   // Gestionnaires d'événements pour démarrer le drag
    setNodeRef,  // Ref pour mesurer position/dimensions
    transform,   // Transformation calculée pendant le drag
    transition,  // Transition CSS pour l'animation
    isDragging,  // true si cette carte est actuellement draguée
  } = useSortable({ id: coinId })

  // ── Style dynamique ───────────────────────────────────────────────────

  const style = {
    // Convertit l'objet transform en chaîne CSS (translate3d pour GPU)
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 999 : 'auto',
    opacity: isDragging ? 0.4 : 1, // Fantôme transparent à l'origine
  }

  // ── Rendu ─────────────────────────────────────────────────────────────

  return (
    <Box ref={setNodeRef} style={style} sx={{ pt: 4 }}>
      {/* Barre de contrôle : handle + chip suppression */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5} px={0.5}>
        {/* Handle de drag : {...listeners} appliqué ICI uniquement */}
        <Box
          {...attributes}
          {...listeners}
          sx={{
            display: 'flex',
            alignItems: 'center',
            cursor: isDragging ? 'grabbing' : 'grab',
            color: 'text.disabled',
            borderRadius: 1,
            px: 0.5,
            '&:hover': { color: 'text.secondary' },
            transition: 'color 0.15s',
          }}
        >
          <DragIndicatorIcon fontSize="small" />
        </Box>

        {/* Chip de suppression : cliquable partout (pas seulement sur ✕) */}
        <Chip
          label={coinId}
          size="small"
          onClick={onRemove}
          onDelete={onRemove}
          deleteIcon={<CloseIcon />}
          sx={{ fontSize: 11, opacity: 0.6, cursor: 'pointer' }}
        />
      </Box>

      {/* Zone de navigation : vérifie !isDragging avant de naviguer */}
      <Box
        onClick={() => { if (!isDragging) navigate(`/coin/${coinId}`) }}
        sx={{ cursor: isDragging ? 'grabbing' : 'pointer' }}
      >
        <CryptoCard
          coinId={coinId}
          data={data}
          alerts={alerts}
          onSetAlert={onSetAlert}
          onRemoveAlert={onRemoveAlert}
        />
      </Box>
    </Box>
  )
}

