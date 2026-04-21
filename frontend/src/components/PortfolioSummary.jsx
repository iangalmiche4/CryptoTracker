import { Box, Card, CardContent, Typography, Grid } from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import { useTranslation } from '../contexts/LanguageContext'

export default function PortfolioSummary({ summary }) {
  const { t } = useTranslation()
  
  if (!summary) return null
  
  const isPositive = summary.total_gain_loss >= 0
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          {t('portfolio.summary')}
        </Typography>
        
        <Grid container spacing={3}>
          {/* Valeur actuelle */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {t('portfolio.currentValue')}
              </Typography>
              <Typography variant="h4">
                ${summary.current_value.toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          
          {/* Investi */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {t('portfolio.totalInvested')}
              </Typography>
              <Typography variant="h4">
                ${summary.total_invested.toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          
          {/* Gain/Perte */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {t('portfolio.gainLoss')}
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                {isPositive ? (
                  <TrendingUpIcon color="success" />
                ) : (
                  <TrendingDownIcon color="error" />
                )}
                <Typography 
                  variant="h4" 
                  color={isPositive ? 'success.main' : 'error.main'}
                >
                  ${Math.abs(summary.total_gain_loss).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Grid>
          
          {/* Pourcentage */}
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                {t('portfolio.percentage')}
              </Typography>
              <Typography 
                variant="h4" 
                color={isPositive ? 'success.main' : 'error.main'}
              >
                {isPositive ? '+' : ''}{summary.gain_loss_percentage.toFixed(2)}%
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
