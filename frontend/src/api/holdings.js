import client from './client'

export const holdingsAPI = {
  // Récupérer tous les holdings
  getAll: () => client.get('/api/holdings'),
  
  // Récupérer le résumé du portfolio
  getSummary: () => client.get('/api/holdings/summary'),
  
  // Créer un holding
  create: (data) => client.post('/api/holdings', data),
  
  // Mettre à jour un holding
  update: (id, data) => client.put(`/api/holdings/${id}`, data),
  
  // Supprimer un holding
  delete: (id) => client.delete(`/api/holdings/${id}`)
}
