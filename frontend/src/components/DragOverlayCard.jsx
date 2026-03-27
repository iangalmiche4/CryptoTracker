/**
 * DragOverlayCard.jsx — Carte "fantôme" pendant le drag & drop
 *
 * Affiche une version stylisée de CryptoCard qui suit le curseur. Rendu via
 * <DragOverlay> (portail React sous <body>) pour s'afficher par-dessus tout.
 *
 * Pendant le drag : carte source devient transparente, ce composant suit le curseur.
 * Purement visuel (pas d'interactions alertes/navigation).
 */

import { Box } from '@mui/material'
import CryptoCard from './CryptoCard'

export default function DragOverlayCard({ coinId, data, alerts }) {
  return (
    <Box
      sx={{
        // pt: 4 reproduit l'espace du chip de suppression dans SortableCard
        pt: 4,

        // drop-shadow() suit le contour réel (coins arrondis) vs box-shadow (rectangle)
        // Ombre violette pour renforcer l'identité visuelle
        filter: 'drop-shadow(0 20px 40px rgba(108,99,255,0.35))',

        // rotate(2deg) : simule l'effet de "soulever" une carte
        // scale(1.03) : zoom de 3% pour impression d'élévation
        transform: 'rotate(2deg) scale(1.03)',
        transition: 'transform 0.15s',
        cursor: 'grabbing',
      }}
    >
      {/*
        Réutilise CryptoCard (DRY). Callbacks vides car purement visuel.
        Fonctions vides vs null pour éviter "null is not a function" si clic pendant drag.
      */}
      <CryptoCard
        coinId={coinId}
        data={data}
        alerts={alerts}
        onSetAlert={() => {}}
        onRemoveAlert={() => {}}
      />
    </Box>
  )
}