import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './components/Home';
import PDFConverter from './components/PDFConverter';
import { AuthProvider, useAuth } from './components/Auth';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#181c24',
      paper: '#23272f',
    },
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <NavBar />
          <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #181c24 0%, #23272f 100%)' }}>
            <AppRoutes />
            <ToastContainer position="bottom-right" />
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

function AppRoutes() {
  const { session } = useAuth();
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/convert" element={session ? <PDFConverter /> : <SignInRequired />} />
    </Routes>
  );
}

function SignInRequired() {
  const { openModal } = useAuth();
  return (
    <div style={{ textAlign: 'center', marginTop: 80 }}>
      <h2>You must be signed in to use the PDF Converter.</h2>
      <button onClick={openModal} className="sign-in-button">Sign In</button>
    </div>
  );
}

export default App;
