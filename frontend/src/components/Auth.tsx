import { useEffect, useState, createContext, useContext } from 'react'
import { supabase } from '../lib/supabase'
import { Auth as SupabaseAuth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import Dialog from '@mui/material/Dialog'

const AuthContext = createContext<any>(null)

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session }, error }) => {
      if (error) {
        console.error('Error getting session:', error)
        setError(error.message)
      } else {
        setSession(session)
      }
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setModalOpen(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const openModal = () => setModalOpen(true)
  const closeModal = () => setModalOpen(false)
  const handleSignOut = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) {
        console.error('Error signing out:', error)
        setError(error.message)
      }
    } catch (err) {
      console.error('Unexpected error during sign out:', err)
      setError('An unexpected error occurred during sign out')
    }
  }

  return (
    <AuthContext.Provider value={{ session, openModal, closeModal, modalOpen, handleSignOut }}>
      {children}
      <AuthModal open={modalOpen} onClose={closeModal} error={error} />
    </AuthContext.Provider>
  )
}

export function AuthModal({ open, onClose, error }: { open: boolean, onClose: () => void, error?: string | null }) {
  // Get the correct redirect URL based on environment
  const getRedirectUrl = () => {
    // Check for explicit redirect URL from environment variables
    const envRedirectUrl = import.meta.env.VITE_SUPABASE_REDIRECT_URL
    if (envRedirectUrl) {
      return envRedirectUrl
    }
    
    if (typeof window !== 'undefined') {
      // Use the current origin (works for both dev and production)
      return window.location.origin
    }
    return 'http://localhost:3000' // Fallback for SSR
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <div className="auth-modal-content" style={{ padding: 24, background: '#181c24' }}>
        {error && <div className="auth-error">{error}</div>}
        <SupabaseAuth
          supabaseClient={supabase}
          appearance={{ theme: ThemeSupa }}
          providers={['google']}
          theme="dark"
          redirectTo={getRedirectUrl()}
          localization={{
            variables: {
              sign_in: {
                email_label: 'Email address',
                password_label: 'Your password',
              },
              sign_up: {
                email_label: 'Email address',
                password_label: 'Your password',
              },
            },
          }}
        />
      </div>
    </Dialog>
  )
} 