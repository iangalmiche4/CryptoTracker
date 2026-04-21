import { Card, CardContent, Typography, Box, IconButton, Chip } from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import { useTranslation } from '../contexts/LanguageContext'

export default function HoldingCard({ holding, onEdit, onDelete }) {
  const { t } = useTranslation()
  
  const isPositive = holding.total_gain_loss >= 0
  const purchaseDate = new Date(holding.purchase_date).toLocaleDateString()
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2.5}>
          <Typography variant="h6" textTransform="uppercase">
            {holding.coin_id}
          </Typography>
          <Box>
            <IconButton size="small" onClick={() => onEdit(holding)}>
              <EditIcon fontSize="small" />
            </IconButton>
            <IconButton size="small" onClick={() => onDelete(holding.id)} color="error">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>
        
        {/* Quantité */}
        <Typography variant="body2" color="text.secondary" mb={0.5}>
          {t('portfolio.quantity')}: {holding.quantity}
        </Typography>
        
        {/* Prix d'achat */}
        <Typography variant="body2" color="text.secondary" mb={0.5}>
          {t('portfolio.purchasePrice')}: ${holding.purchase_price.toLocaleString()}
        </Typography>
        
        {/* Date d'achat */}
        <Typography variant="body2" color="text.secondary" mb={2.5}>
          {t('portfolio.purchaseDate')}: {purchaseDate}
        </Typography>
        
        {/* Prix actuel */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="body2">
            {t('portfolio.currentPrice')}:
          </Typography>
          <Typography variant="h6">
            ${holding.current_price.toLocaleString()}
          </Typography>
        </Box>
        
        {/* Valeur actuelle */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="body2">
            {t('portfolio.currentValue')}:
          </Typography>
          <Typography variant="h6">
            ${holding.current_value.toLocaleString()}
          </Typography>
        </Box>
        
        {/* Gain/Perte */}
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          p={1.5}
          bgcolor={isPositive ? 'success.light' : 'error.light'}
          borderRadius={2}
        >
          <Box display="flex" alignItems="center" gap={1}>
            {isPositive ? (
              <TrendingUpIcon color="success" />
            ) : (
              <TrendingDownIcon color="error" />
            )}
            <Typography variant="body2" fontWeight="bold">
              {t('portfolio.gainLoss')}:
            </Typography>
          </Box>
          <Box textAlign="right">
            <Typography 
              variant="body1" 
              fontWeight="bold"
              color={isPositive ? 'success.dark' : 'error.dark'}
            >
              {isPositive ? '+' : ''}${Math.abs(holding.total_gain_loss).toLocaleString()}
            </Typography>
            <Typography 
              variant="body2"
              color={isPositive ? 'success.dark' : 'error.dark'}
            >
              ({isPositive ? '+' : ''}{holding.gain_loss_percentage.toFixed(2)}%)
            </Typography>
          </Box>
        </Box>
        
        {/* Notes */}
        {holding.notes && (
          <Box mt={2}>
            <Chip label={holding.notes} size="small" variant="outlined" />
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

