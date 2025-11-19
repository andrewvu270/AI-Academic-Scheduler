import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  LinearProgress,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  School as SchoolIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    setUploading(true);
    setUploadMessage(null);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.type !== 'application/pdf') {
          setUploadMessage({ type: 'error', text: 'Only PDF files are supported' });
          setUploading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // TODO: Replace with actual API endpoint
        // const response = await fetch('/api/upload', { method: 'POST', body: formData });
        // if (!response.ok) throw new Error('Upload failed');

        setUploadedFiles([...uploadedFiles, file.name]);
      }

      setUploadMessage({ type: 'success', text: 'Files uploaded successfully!' });
    } catch (error) {
      setUploadMessage({ type: 'error', text: 'Failed to upload files' });
    } finally {
      setUploading(false);
    }
  };

  const stats = [
    { label: 'Active Courses', value: '4', icon: SchoolIcon, color: '#1976d2' },
    { label: 'Tasks Due', value: '12', icon: ScheduleIcon, color: '#f57c00' },
    { label: 'Study Hours', value: '24.5', icon: TrendingUpIcon, color: '#388e3c' },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Welcome to AI Academic Scheduler
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Manage your courses, track deadlines, and optimize your study schedule
        </Typography>
      </Box>

      {/* Upload Section */}
      <Paper
        sx={{
          p: 4,
          mb: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 2,
          textAlign: 'center',
        }}
      >
        <CloudUploadIcon sx={{ fontSize: 48, mb: 2 }} />
        <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
          Upload Your Syllabus
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, opacity: 0.9 }}>
          Upload PDF syllabi to automatically extract deadlines and course information
        </Typography>
        <Button
          variant="contained"
          component="label"
          sx={{
            backgroundColor: 'white',
            color: '#667eea',
            fontWeight: 'bold',
            '&:hover': { backgroundColor: '#f5f5f5' },
          }}
          disabled={uploading}
        >
          {uploading ? <CircularProgress size={24} /> : 'Choose PDF Files'}
          <input
            type="file"
            multiple
            accept=".pdf"
            hidden
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </Button>
      </Paper>

      {/* Upload Message */}
      {uploadMessage && (
        <Alert severity={uploadMessage.type} sx={{ mb: 3 }}>
          {uploadMessage.text}
        </Alert>
      )}

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Icon sx={{ fontSize: 32, color: stat.color, mr: 1 }} />
                    <Typography color="textSecondary" variant="body2">
                      {stat.label}
                    </Typography>
                  </Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: stat.color }}>
                    {stat.value}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
            Uploaded Syllabi ({uploadedFiles.length})
          </Typography>
          <Grid container spacing={2}>
            {uploadedFiles.map((file, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {file}
                    </Typography>
                    <LinearProgress variant="determinate" value={100} sx={{ mb: 1 }} />
                    <Typography variant="caption" color="textSecondary">
                      Processing complete
                    </Typography>
                  </CardContent>
                  <CardActions>
                    <Button size="small" color="primary">
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              sx={{ py: 2 }}
              href="/courses"
            >
              View Courses
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              sx={{ py: 2 }}
              href="/tasks"
            >
              View Tasks
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              sx={{ py: 2 }}
              href="/schedule"
            >
              View Schedule
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              sx={{ py: 2 }}
            >
              Generate Plan
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;