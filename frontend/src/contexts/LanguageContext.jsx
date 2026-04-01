/**
 * LanguageContext.jsx — Gestion du multi-langues
 * 
 * Système léger sans bibliothèque externe :
 * - Stockage de la langue dans localStorage
 * - Traductions chargées depuis des fichiers JSON
 * - Hook useTranslation pour accéder aux traductions
 */

import { createContext, useContext, useState, useEffect } from 'react'
import fr from '../locales/fr.json'
import en from '../locales/en.json'

const translations = { fr, en }

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    // Récupérer la langue depuis localStorage ou utiliser 'fr' par défaut
    return localStorage.getItem('language') || 'fr'
  })

  useEffect(() => {
    // Sauvegarder la langue dans localStorage à chaque changement
    localStorage.setItem('language', language)
  }, [language])

  const t = (key) => {
    // Fonction de traduction : t('auth.login') → 'Connexion' (fr) ou 'Login' (en)
    const keys = key.split('.')
    let value = translations[language]
    
    for (const k of keys) {
      value = value?.[k]
    }
    
    // Retourner la clé si la traduction n'existe pas (fallback)
    return value || key
  }

  const changeLanguage = (lang) => {
    if (translations[lang]) {
      setLanguage(lang)
    }
  }

  return (
    <LanguageContext.Provider value={{ language, changeLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

// Hook personnalisé pour utiliser les traductions
export function useTranslation() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider')
  }
  return context
}
