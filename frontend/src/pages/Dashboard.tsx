import React, { useCallback, useEffect, useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Box,
  Typography,
  Button,
  LinearProgress,
  Alert,
  CircularProgress,
  Fab,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  TaskAlt as CompletedIcon,
  HourglassEmpty as PendingIcon,
  AccessTime as DueSoonIcon,
  Dashboard as DashboardIcon,
  Analytics as AnalyticsIcon,
  Timer as TimerIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL } from '../config/api';
import NaturalLanguageQuery from '../components/NaturalLanguageQuery';
import StressVisualization from '../components/StressVisualization';
import LearningStyleProfile from '../components/LearningStyleProfile';
import PomodoroTimer from '../components/PomodoroTimer';
import AnalyticsDashboard from '../components/AnalyticsDashboard';
import SmartTaskAssistant from '../components/SmartTaskAssistant';
import IntelligentRecommendations from '../components/IntelligentRecommendations';

interface StoredTask {
  id: string;
  title: string;
  due_date?: string;
  status?: string;
}

const getLocalTasks = (): StoredTask[] => {
  const tasks: StoredTask[] = [];
  for (let i = 0; i < localStorage.length; i += 1) {
    const key = localStorage.key(i);
    if (key && key.startsWith('task_')) {
      try {
        const task = JSON.parse(localStorage.getItem(key) || '{}');
        // Only include guest tasks (same logic as fetchAllTasks)
        if (task && task.id && task.user_id === 'guest') {
          tasks.push(task);
        }
      } catch (e) {
        // Ignore malformed task entries
      }
    }
  }
  return tasks;
};

const computeStats = (tasks: StoredTask[]) => {
  const now = new Date();
  const dueSoonThreshold = new Date(now);
  dueSoonThreshold.setDate(now.getDate() + 7);

  let completed = 0;
  let pending = 0;
  let dueSoon = 0;

  tasks.forEach((task) => {
    const status = (task.status || '').toLowerCase();
    if (status === 'completed') {
      completed += 1;
    } else {
      pending += 1;
      if (task.due_date) {
        const dueDate = new Date(task.due_date);
        if (!Number.isNaN(dueDate.getTime()) && dueDate >= now && dueDate <= dueSoonThreshold) {
          dueSoon += 1;
        }
      }
    }
  });

  return {
    completed,
    pending,
    dueSoon,
  };
};

const fetchSupabaseTasks = async (): Promise<StoredTask[] | null> => {
  try {
    // Use the same fetchAllTasks function as the Tasks page for consistency
    const { fetchAllTasks } = await import('../utils/taskStorage');
    const data = await fetchAllTasks();

    return (data.tasks || []).map((task: any) => ({
      id: task.id,
      title: task.title,
      due_date: task.due_date,
      status: task.status,
    }));
  } catch (error) {
    console.error('Error fetching tasks:', error);
    return null;
  }
};

const Dashboard = () => {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [statsSnapshot, setStatsSnapshot] = useState(() => computeStats(getLocalTasks()));
  const [activeView, setActiveView] = useState<'overview' | 'analytics' | 'focus'>('overview');
  const [showFab, setShowFab] = useState(false);

  const refreshStats = useCallback(async () => {
    const token = localStorage.getItem('access_token');

    if (token) {
      const supabaseTasks = await fetchSupabaseTasks();
      if (supabaseTasks && supabaseTasks.length > 0) {
        setStatsSnapshot(computeStats(supabaseTasks));
        return;
      }
    }

    setStatsSnapshot(computeStats(getLocalTasks()));
  }, []);

  useEffect(() => {
    refreshStats();
    // Show FAB after a delay
    setTimeout(() => setShowFab(true), 1000);
  }, [refreshStats]);

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

        // Extract text from PDF using the existing upload endpoint first
        const formData = new FormData();
        formData.append('file', file);
        formData.append('course_id', file.name.replace('.pdf', ''));

        const uploadResponse = await fetch(`${API_BASE_URL}/api/upload/syllabus`, {
          method: 'POST',
          headers: {
            'Authorization': localStorage.getItem('access_token') ? 
              `Bearer ${localStorage.getItem('access_token')}` : '',
          },
          body: formData,
        });

        if (!uploadResponse.ok) {
          const error = await uploadResponse.json();
          throw new Error(error.detail || 'Failed to extract text from PDF');
        }

        const uploadData = await uploadResponse.json();
        
        // Store the extracted tasks directly
        if (uploadData.tasks && uploadData.tasks.length > 0) {
          const courseName = file.name.replace('.pdf', '').replace(/_/g, ' ');
          const userId = localStorage.getItem('access_token') ? 'registered' : 'guest';
          
          // Create course first
          let courseId: string | null = null;
          try {
            const courseHeaders: HeadersInit = { 'Content-Type': 'application/json' };
            const accessToken = localStorage.getItem('access_token');
            if (accessToken) {
              courseHeaders['Authorization'] = `Bearer ${accessToken}`;
            }

            const courseResponse = await fetch(`${API_BASE_URL}/api/courses/`, {
              method: 'POST',
              headers: courseHeaders,
              body: JSON.stringify({
                name: courseName,
                code: courseName.substring(0, 10).toUpperCase(),
                description: `Course from ${file.name}`,
              }),
            });
            
            if (courseResponse.ok) {
              const courseData = await courseResponse.json();
              courseId = courseData.id;
            }
          } catch (err) {
            console.error('Error creating course:', err);
            // Generate fallback course ID for guest mode
            courseId = `course_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          }

          // Store course data for guest mode
          if (userId === 'guest' && courseId) {
            const courseData = {
              id: courseId,
              name: courseName,
              code: courseName.substring(0, 10).toUpperCase(),
              description: `Course from ${file.name}`,
              user_id: 'guest',
              created_at: new Date().toISOString(),
            };
            localStorage.setItem(`course_${courseId}`, JSON.stringify(courseData));
          }

          // Store tasks directly from upload response
          uploadData.tasks.forEach((task: any) => {
            const enhancedTask = {
              ...task,
              user_id: userId,
              course_id: courseId,
            };
            
            if (userId === 'guest') {
              localStorage.setItem(`task_${task.id}`, JSON.stringify(enhancedTask));
            }
          });

          // Store course tasks list for guest mode
          if (userId === 'guest' && courseId) {
            const courseTaskIds = uploadData.tasks.map((t: any) => t.id);
            localStorage.setItem(`course_${courseId}_tasks`, JSON.stringify(courseTaskIds));
          }
        }

        setUploadedFiles((prev) => [...prev, file.name]);
      }

      setUploadMessage({ 
        type: 'success', 
        text: 'Files processed successfully! Tasks extracted with AI-powered workload predictions and prioritization.' 
      });
      await refreshStats();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload files';
      setUploadMessage({ type: 'error', text: errorMessage });
    } finally {
      setUploading(false);
    }
  };

  const stats = [
    { 
      label: 'Completed', 
      value: statsSnapshot.completed, 
      icon: CompletedIcon, 
      color: '#388e3c',
      bgGradient: 'linear-gradient(135deg, #4caf50, #66bb6a)'
    },
    { 
      label: 'Pending', 
      value: statsSnapshot.pending, 
      icon: PendingIcon, 
      color: '#f57c00',
      bgGradient: 'linear-gradient(135deg, #ff9800, #ffb74d)'
    },
    { 
      label: 'Due Soon', 
      value: statsSnapshot.dueSoon, 
      icon: DueSoonIcon, 
      color: '#d32f2f',
      bgGradient: 'linear-gradient(135deg, #f44336, #ef5350)'
    },
  ];

  return (
    <>
      {/* Floating Action Button for Quick Actions */}
      <AnimatePresence>
        {showFab && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            transition={{ type: "spring", duration: 0.5 }}
            style={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              zIndex: 1000
            }}
          >
            <Fab
              color="primary"
              aria-label="quick-actions"
              sx={{
                background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1565c0, #2196f3)',
                }
              }}
            >
              <DashboardIcon />
            </Fab>
          </motion.div>
        )}
      </AnimatePresence>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Enhanced Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{ mb: 6 }} className="animate-fade-in">
            <Typography variant="h2" component="h1" sx={{ mb: 1, fontWeight: 700 }}>
              Welcome to MyDesk
            </Typography>
            <Typography variant="body1" color="textSecondary" sx={{ fontSize: '1.1rem' }}>
              Your intelligent productivity companion for work and learning
            </Typography>
            
            {/* View Switcher */}
            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              {[
                { id: 'overview', label: 'Overview', icon: <DashboardIcon /> },
                { id: 'analytics', label: 'Analytics', icon: <AnalyticsIcon /> },
                { id: 'focus', label: 'Focus Mode', icon: <TimerIcon /> },
              ].map((view) => (
                <motion.div
                  key={view.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    variant={activeView === view.id ? 'contained' : 'outlined'}
                    startIcon={view.icon}
                    onClick={() => setActiveView(view.id as any)}
                    sx={{
                      borderRadius: '20px',
                      px: 3,
                      py: 1,
                    }}
                  >
                    {view.label}
                  </Button>
                </motion.div>
              ))}
            </Box>
          </Box>
        </motion.div>

        {/* Animated Stats Grid */}
        <AnimatePresence mode="wait">
          {activeView === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Smart Task Assistant */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
              >
                <SmartTaskAssistant />
              </motion.div>

              {/* AI Assistant */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <NaturalLanguageQuery />
              </motion.div>

              {/* Intelligent Recommendations */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <IntelligentRecommendations />
              </motion.div>

              {/* Learning Style Profile */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <LearningStyleProfile />
              </motion.div>

              {/* Stress Visualization */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
              >
                <StressVisualization />
              </motion.div>

              {/* Enhanced Upload Section */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <Paper
                  className="bento-card animate-fade-in delay-200"
                  sx={{
                    p: 6,
                    mb: 6,
                    textAlign: 'center',
                    border: '2px dashed #e0e0e0',
                    bgcolor: 'transparent',
                    background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.02), rgba(66, 165, 245, 0.05))',
                    '&:hover': {
                      borderColor: 'primary.main',
                      bgcolor: 'rgba(25, 118, 210, 0.05)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 24px rgba(0,0,0,0.1)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  <motion.div
                    animate={{ y: [0, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    <CloudUploadIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
                  </motion.div>
                  <Typography variant="h4" sx={{ mb: 2, fontWeight: 600 }}>
                    Upload to MyDesk
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 4, maxWidth: '500px', mx: 'auto' }}>
                    Drop your PDF syllabus or documents here to automatically extract deadlines and create your intelligent study plan.
                  </Typography>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      variant="contained"
                      component="label"
                      size="large"
                      disabled={uploading}
                      sx={{ 
                        minWidth: '200px',
                        py: 1.5,
                        background: 'linear-gradient(135deg, #1976d2, #42a5f5)',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #1565c0, #2196f3)',
                        }
                      }}
                    >
                      {uploading ? <CircularProgress size={24} color="inherit" /> : 'Select PDF'}
                      <input
                        type="file"
                        multiple
                        accept=".pdf"
                        hidden
                        onChange={handleFileUpload}
                        disabled={uploading}
                      />
                    </Button>
                  </motion.div>
                </Paper>
              </motion.div>

              {/* Uploaded Files */}
              {uploadedFiles.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="animate-fade-in delay-300"
                >
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
                    Recent Uploads
                  </Typography>
                  <Grid container spacing={3}>
                    {uploadedFiles.map((file, index) => (
                      <Grid item xs={12} sm={6} md={4} key={index}>
                        <motion.div
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.1 + index * 0.1 }}
                          whileHover={{ scale: 1.02, y: -5 }}
                        >
                          <Paper className="bento-card" sx={{ p: 3 }}>
                            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                              {file}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={100}
                              sx={{
                                mb: 2,
                                height: 6,
                                borderRadius: 3,
                                bgcolor: '#f0f0f0',
                                '& .MuiLinearProgress-bar': {
                                  borderRadius: 3,
                                  background: 'linear-gradient(90deg, #4caf50, #66bb6a)'
                                }
                              }}
                            />
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="caption" color="textSecondary">
                                Processed
                              </Typography>
                              <Button size="small" color="primary">
                                View
                              </Button>
                            </Box>
                          </Paper>
                        </motion.div>
                      </Grid>
                    ))}
                  </Grid>
                </motion.div>
              )}
            </motion.div>
          )}

          {activeView === 'analytics' && (
            <motion.div
              key="analytics-content"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3 }}
            >
              <AnalyticsDashboard />
            </motion.div>
          )}

          {activeView === 'focus' && (
            <motion.div
              key="focus-content"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Box sx={{ mb: 4 }}>
                <Typography variant="h5" sx={{ mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TimerIcon color="primary" />
                  Focus Mode
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Boost your productivity with gamified focus sessions and achievement tracking
                </Typography>
              </Box>
              <PomodoroTimer 
                taskTitle="Focus Session" 
                learningStyle="visual" 
                studyTips={["Take regular breaks", "Stay hydrated", "Minimize distractions"]}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Upload Message */}
        <AnimatePresence>
          {uploadMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Alert severity={uploadMessage.type} sx={{ mb: 4, borderRadius: '16px' }}>
                {uploadMessage.text}
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

      </Container>
    </>
  );
};

export default Dashboard;