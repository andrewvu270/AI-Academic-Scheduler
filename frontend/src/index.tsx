import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import App from './App';

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
    // Responsive typography
    h1: {
      fontSize: '1.75rem',
      '@media (min-width:600px)': {
        fontSize: '2.125rem',
      },
      '@media (min-width:960px)': {
        fontSize: '2.5rem',
      },
    },
    h2: {
      fontSize: '1.5rem',
      '@media (min-width:600px)': {
        fontSize: '1.875rem',
      },
      '@media (min-width:960px)': {
        fontSize: '2rem',
      },
    },
    h3: {
      fontSize: '1.25rem',
      '@media (min-width:600px)': {
        fontSize: '1.5rem',
      },
    },
    body1: {
      fontSize: '0.875rem',
      '@media (min-width:600px)': {
        fontSize: '1rem',
      },
    },
  },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 960,
      lg: 1280,
      xl: 1920,
    },
  },
  components: {
    // Global responsive styles
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingLeft: '16px',
          paddingRight: '16px',
          '@media (min-width: 600px)': {
            paddingLeft: '24px',
            paddingRight: '24px',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: '44px', // Touch-friendly size
          fontSize: '0.875rem',
          '@media (min-width: 600px)': {
            fontSize: '1rem',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          margin: '8px 0',
          '@media (min-width: 600px)': {
            margin: '16px 0',
          },
        },
      },
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);