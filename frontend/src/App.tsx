import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useEffect } from 'react';

import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Schedule from './pages/Schedule';
import Survey from './pages/Survey';
import Auth from './pages/Auth';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import { getOrCreateGuestSession } from './utils/guestMode';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
      light: '#8b9ef8',
    },
    secondary: {
      main: '#764ba2',
      light: '#9b6db8',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", sans-serif',
  },
});

function App() {
  useEffect(() => {
    // Initialize guest session if not logged in
    const token = localStorage.getItem('access_token');
    if (!token) {
      getOrCreateGuestSession();
    }
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<Auth />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <>
                  <Navigation />
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/tasks" element={<Tasks />} />
                    <Route path="/schedule" element={<Schedule />} />
                    <Route path="/survey" element={<Survey />} />
                  </Routes>
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/tasks"
            element={
              <ProtectedRoute>
                <>
                  <Navigation />
                  <Tasks />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/schedule"
            element={
              <ProtectedRoute>
                <>
                  <Navigation />
                  <Schedule />
                </>
              </ProtectedRoute>
            }
          />
          <Route
            path="/survey"
            element={
              <ProtectedRoute>
                <Survey />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;