import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Analyze from './pages/Analyze'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Pricing from './pages/Pricing'
import Account from './pages/Account'
import Terms from './pages/Terms'
import Contact from './pages/Contact'

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Full-page auth routes (no layout) */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Main layout routes */}
        <Route element={<Layout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/account" element={<Account />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/contact" element={<Contact />} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
