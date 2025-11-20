import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  Menu,
  MenuItem,
  IconButton,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Home as HomeIcon,
  CheckCircle as TasksIcon,
  DateRange as CalendarIcon,
  Logout as LogoutIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const userEmail = localStorage.getItem('user_email');
  const isLoggedIn = !!localStorage.getItem('access_token');
  const isGuest = !isLoggedIn && !!localStorage.getItem('guest_session_id');

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [savingData, setSavingData] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_id');
    handleMenuClose();
    navigate('/auth');
  };

  const handleSaveToCloud = () => {
    setSaveDialogOpen(true);
    setSaveError(null);
  };

  const handleConfirmSaveToCloud = async () => {
    setSavingData(true);
    setSaveError(null);
    try {
      navigate('/auth');
      setSaveDialogOpen(false);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSavingData(false);
    }
  };

  return (
    <>
      <AppBar position="sticky" sx={{ backgroundColor: '#667eea' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            📚 AI Academic Scheduler
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Button
              color="inherit"
              startIcon={<HomeIcon />}
              component={RouterLink}
              to="/"
              sx={{ textTransform: 'none', fontSize: '1rem' }}
            >
              Dashboard
            </Button>
            <Button
              color="inherit"
              startIcon={<TasksIcon />}
              component={RouterLink}
              to="/tasks"
              sx={{ textTransform: 'none', fontSize: '1rem' }}
            >
              Tasks
            </Button>
            <Button
              color="inherit"
              startIcon={<CalendarIcon />}
              component={RouterLink}
              to="/schedule"
              sx={{ textTransform: 'none', fontSize: '1rem' }}
            >
              Calendar
            </Button>

            {isGuest && (
              <Button
                color="inherit"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                onClick={handleSaveToCloud}
                sx={{
                  textTransform: 'none',
                  fontSize: '0.9rem',
                  borderColor: 'rgba(255,255,255,0.5)',
                  '&:hover': { borderColor: 'white' },
                }}
              >
                Save to Cloud
              </Button>
            )}

            {isLoggedIn && (
              <>
                <IconButton
                  onClick={handleMenuOpen}
                  sx={{
                    width: 40,
                    height: 40,
                    bgcolor: 'rgba(255,255,255,0.2)',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' },
                  }}
                >
                  <Avatar
                    sx={{
                      width: 32,
                      height: 32,
                      bgcolor: '#764ba2',
                      fontSize: '0.9rem',
                    }}
                  >
                    {userEmail?.charAt(0).toUpperCase()}
                  </Avatar>
                </IconButton>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <MenuItem disabled>
                    <Typography variant="body2">{userEmail}</Typography>
                  </MenuItem>
                  <MenuItem onClick={handleLogout}>
                    <LogoutIcon sx={{ mr: 1 }} />
                    Logout
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Save to Cloud Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
        <DialogTitle>Save to Cloud</DialogTitle>
        <DialogContent sx={{ minWidth: 400 }}>
          {saveError && <Alert severity="error" sx={{ mb: 2 }}>{saveError}</Alert>}
          <Typography>
            To save your data to the cloud and access it from any device, please create an account or log in.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmSaveToCloud}
            variant="contained"
            disabled={savingData}
          >
            {savingData ? <CircularProgress size={24} /> : 'Continue to Login'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default Navigation;
