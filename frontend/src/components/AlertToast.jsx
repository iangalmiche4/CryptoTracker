/**
 * AlertToast.jsx — Notifications toast des alertes de prix
 *
 * Affiche les alertes déclenchées en bas à droite de l'écran. Plusieurs alertes
 * peuvent être actives simultanément et sont empilées verticalement.
 *
 * Props :
 *  - triggered : tableau d'objets { id, coinId, type, threshold, price }
 *  - onDismiss : callback pour fermer un toast (retire l'alerte du tableau)
 */

import { Alert, Box } from '@mui/material'

export default function AlertToast({ triggered, onDismiss }) {
  return (
    /*
      position: fixed → se positionne par rapport au viewport (pas au parent DOM)
      Reste visible même au scroll. zIndex: 2000 pour passer par-dessus modales MUI.
      
      display: flex + flexDirection: column-reverse → empile les alertes de bas en haut
      Les nouvelles alertes apparaissent en bas, les anciennes remontent
    */
    <Box
      sx={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 2000,
        display: 'flex',
        flexDirection: 'column-reverse', // Empile de bas en haut
        gap: 1, // Espacement de 8px entre chaque alerte
        maxWidth: 400,
      }}
    >
      {triggered.map(t => (
        /*
          key = t.id (avec timestamp) pour unicité
          Chaque Alert est un élément indépendant dans le flex container
        */
        <Alert
          key={t.id}
          severity={t.type === 'high' ? 'success' : 'error'}
          onClose={() => onDismiss(t.id)}
          sx={{
            minWidth: 280,
            fontWeight: 600,
            // Animation d'apparition fluide
            animation: 'slideIn 0.3s ease-out',
            '@keyframes slideIn': {
              from: {
                transform: 'translateX(400px)',
                opacity: 0,
              },
              to: {
                transform: 'translateX(0)',
                opacity: 1,
              },
            },
          }}
        >
          {/* Message principal : "bitcoin ↑ a dépassé $80 000" */}
          {t.coinId} {t.type === 'high' ? '↑ a dépassé' : '↓ est passé sous'} ${t.threshold.toLocaleString()}
          <br />
          {/* Prix exact au moment du déclenchement */}
          <span style={{ fontWeight: 400, fontSize: 12 }}>
            Prix actuel : ${t.price.toLocaleString()}
          </span>
        </Alert>
      ))}
    </Box>
  )
}