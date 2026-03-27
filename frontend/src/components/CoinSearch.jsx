/**
 * CoinSearch.jsx — Barre de recherche avec dropdown
 *
 * Affiche un champ de recherche avec indicateur de chargement et dropdown
 * des résultats. Permet l'ajout de coins au dashboard et signale ceux déjà présents.
 *
 * Séparation : UI ici, logique de recherche dans useCoinSearch, ajout dans App.jsx.
 * Pattern "Controlled Input" : React contrôle la valeur du champ.
 */

import { useState } from 'react'
import {
  Box,
  TextField,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  CircularProgress,
  Typography,
  InputAdornment,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import { useCoinSearch } from '../hooks/useCoinSearch'

export default function CoinSearch({ activeCoinIds, onAdd }) {

  const [query, setQuery] = useState('')
  const { results, searching } = useCoinSearch(query)

  const handleSelect = (coin) => {
    onAdd(coin.id)
    setQuery('') // Réinitialise pour feedback visuel et fermer le dropdown
  }

  return (
    // position: relative nécessaire pour que le dropdown (absolute) se positionne correctement
    <Box sx={{ position: 'relative', width: 320 }}>

      <TextField
        fullWidth
        size="small"
        placeholder="Rechercher un coin…"
        value={query}
        onChange={e => setQuery(e.target.value)}
        slotProps={{
          input: {
            // Affiche spinner pendant recherche, sinon icône loupe
            startAdornment: (
              <InputAdornment position="start">
                {searching
                  ? <CircularProgress size={16} />
                  : <SearchIcon fontSize="small" />}
              </InputAdornment>
            ),
          },
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            backgroundColor: 'background.paper',
          }
        }}
      />

      {/* Dropdown apparaît uniquement si résultats présents */}
      {results.length > 0 && (
        <Paper
          elevation={8}
          sx={{
            position: 'absolute',
            top: '110%',
            left: 0,
            right: 0,
            zIndex: 100, // Par-dessus les cartes
            borderRadius: 2,
            overflow: 'hidden',
          }}
        >
          <List dense disablePadding>
            {results.map(coin => {
              const alreadyAdded = activeCoinIds.includes(coin.id)

              return (
                <ListItemButton
                  key={coin.id}
                  // Double protection : disabled (UX) + condition (logique)
                  onClick={() => !alreadyAdded && handleSelect(coin)}
                  disabled={alreadyAdded}
                  sx={{ py: 1.2 }}
                >
                  <ListItemText
                    primary={coin.name}
                    secondary={coin.symbol.toUpperCase()}
                    slotProps={{
                      primary: { fontWeight: 600, fontSize: 14 },
                      secondary: { fontSize: 12 }
                    }}
                  />

                  {alreadyAdded && (
                    <Typography variant="caption" color="text.disabled">
                      Déjà ajouté
                    </Typography>
                  )}
                </ListItemButton>
              )
            })}
          </List>
        </Paper>
      )}
    </Box>
  )
}