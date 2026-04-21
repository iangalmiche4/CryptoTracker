import { useState } from 'react'
import {
  Container, Typography, Box, Button, Grid, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, CircularProgress, Alert
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import Header from '../components/Header'
import PortfolioSummary from '../components/PortfolioSummary'
import HoldingCard from '../components/HoldingCard'
import { useUserHoldings } from '../hooks/useUserHoldings'
import { useTranslation } from '../contexts/LanguageContext'

export default function Portfolio() {
  const { t } = useTranslation()
  const {
    holdings,
    summary,
    isLoading,
    error,
    createHolding,
    updateHolding,
    deleteHolding,
    isCreating,
    isUpdating
  } = useUserHoldings()
  
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingHolding, setEditingHolding] = useState(null)
  const [formData, setFormData] = useState({
    coin_id: '',
    quantity: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0],
    notes: ''
  })
  
  const handleOpenDialog = (holding = null) => {
    if (holding) {
      setEditingHolding(holding)
      setFormData({
        coin_id: holding.coin_id,
        quantity: holding.quantity,
        purchase_price: holding.purchase_price,
        purchase_date: new Date(holding.purchase_date).toISOString().split('T')[0],
        notes: holding.notes || ''
      })
    } else {
      setEditingHolding(null)
      setFormData({
        coin_id: '',
        quantity: '',
        purchase_price: '',
        purchase_date: new Date().toISOString().split('T')[0],
        notes: ''
      })
    }
    setDialogOpen(true)
  }
  
  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingHolding(null)
  }
  
  const handleSubmit = () => {
    const data = {
      ...formData,
      quantity: parseFloat(formData.quantity),
      purchase_price: parseFloat(formData.purchase_price),
      purchase_date: new Date(formData.purchase_date).toISOString()
    }
    
    if (editingHolding) {
      updateHolding({ id: editingHolding.id, data })
    } else {
      createHolding(data)
    }
    
    handleCloseDialog()
  }
  
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }
  
  if (error) {
    return (
      <Container>
        <Alert severity="error">{t('common.error')}: {error.message}</Alert>
      </Container>
    )
  }
  
  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Titre */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">
            {t('portfolio.title')}
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            {t('portfolio.addHolding')}
          </Button>
        </Box>
        
        {/* Résumé */}
        <PortfolioSummary summary={summary} />
        
        {/* Liste des holdings */}
        {holdings.length === 0 ? (
          <Alert severity="info">
            {t('portfolio.empty')}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {holdings.map(holding => (
              <Grid item xs={12} sm={6} md={6} lg={4} key={holding.id}>
                <HoldingCard
                  holding={holding}
                  onEdit={handleOpenDialog}
                  onDelete={deleteHolding}
                />
              </Grid>
            ))}
          </Grid>
        )}
        
        {/* Dialog Ajout/Édition */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingHolding ? t('portfolio.editHolding') : t('portfolio.addHolding')}
          </DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column" gap={2} mt={1}>
              <TextField
                label={t('portfolio.coinId')}
                value={formData.coin_id}
                onChange={(e) => setFormData({ ...formData, coin_id: e.target.value })}
                disabled={!!editingHolding}
                fullWidth
                helperText="Ex: bitcoin, ethereum, cardano"
              />
              <TextField
                label={t('portfolio.quantity')}
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                fullWidth
                inputProps={{ step: "0.00000001", min: "0" }}
              />
              <TextField
                label={t('portfolio.purchasePrice')}
                type="number"
                value={formData.purchase_price}
                onChange={(e) => setFormData({ ...formData, purchase_price: e.target.value })}
                fullWidth
                inputProps={{ step: "0.01", min: "0" }}
              />
              <TextField
                label={t('portfolio.purchaseDate')}
                type="date"
                value={formData.purchase_date}
                onChange={(e) => setFormData({ ...formData, purchase_date: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& input[type="date"]::-webkit-calendar-picker-indicator': {
                    filter: 'invert(var(--date-picker-invert, 0))',
                    cursor: 'pointer'
                  }
                }}
              />
              <TextField
                label={t('portfolio.notes')}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                multiline
                rows={3}
                fullWidth
                placeholder="Ex: Achat DCA mensuel"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSubmit}
              variant="contained"
              disabled={isCreating || isUpdating || !formData.coin_id || !formData.quantity || !formData.purchase_price}
            >
              {editingHolding ? t('common.save') : t('common.add')}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </>
  )
}

