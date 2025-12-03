import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Button,
  LinearProgress,
  Alert,
  Avatar,
  IconButton,
  Tooltip,
  useTheme,
  Badge,
} from '@mui/material';
import {
  Lightbulb as InsightIcon,
  TrendingUp as TrendingIcon,
  Schedule as ScheduleIcon,
  Psychology as PsychologyIcon,
  Speed as SpeedIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  CheckCircle as CompletedIcon,
  PlayArrow as ActionIcon,
  BookmarkBorder as SaveIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Recommendation {
  id: string;
  type: 'productivity' | 'wellness' | 'learning' | 'scheduling' | 'focus';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  actionable: boolean;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
  category: string;
  reasoning: string;
  applied?: boolean;
  dismissed?: boolean;
}

interface UserPattern {
  peakProductivityHours: number[];
  averageFocusSession: number;
  preferredBreakDuration: number;
  taskCompletionRate: number;
  stressTriggers: string[];
  learningStyle: string;
  weeklyGoals: {
    target: number;
    achieved: number;
  };
}

const IntelligentRecommendations: React.FC = () => {
  const theme = useTheme();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [userPatterns, setUserPatterns] = useState<UserPattern | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [appliedCount, setAppliedCount] = useState(0);

  useEffect(() => {
    loadUserPatterns();
    generateRecommendations();
  }, []);

  const loadUserPatterns = () => {
    // Load user patterns from localStorage or analytics
    const storedPatterns = localStorage.getItem('userPatterns');
    const pomodoroStats = localStorage.getItem('pomodoroStats');
    const learningStyle = localStorage.getItem('learningStyle');

    let patterns: UserPattern = {
      peakProductivityHours: [9, 10, 14, 15], // Default morning and early afternoon
      averageFocusSession: 25,
      preferredBreakDuration: 5,
      taskCompletionRate: 0.75,
      stressTriggers: ['deadlines', 'complex_tasks'],
      learningStyle: 'visual',
      weeklyGoals: {
        target: 20,
        achieved: 15
      }
    };

    if (storedPatterns) {
      try {
        patterns = { ...patterns, ...JSON.parse(storedPatterns) };
      } catch (error) {
        console.error('Error loading user patterns:', error);
      }
    }

    // Update with real data from other components
    if (pomodoroStats) {
      try {
        const stats = JSON.parse(pomodoroStats);
        patterns.weeklyGoals.achieved = stats.totalSessions || 0;
        patterns.averageFocusSession = 25; // Default Pomodoro length
      } catch (error) {
        console.error('Error parsing pomodoro stats:', error);
      }
    }

    if (learningStyle) {
      try {
        const profile = JSON.parse(learningStyle);
        if (profile.style) {
          const dominantStyle = Object.entries(profile.style).reduce((a: any, b: any) => 
            profile.style[a[0]] > profile.style[b[0]] ? a : b
          )[0];
          patterns.learningStyle = dominantStyle;
        }
      } catch (error) {
        console.error('Error parsing learning style:', error);
      }
    }

    setUserPatterns(patterns);
  };

  const generateRecommendations = async () => {
    setIsLoading(true);
    
    // Generate intelligent recommendations based on user patterns
    const newRecommendations: Recommendation[] = [];

    if (!userPatterns) {
      setIsLoading(false);
      return;
    }

    // Productivity recommendations
    if (userPatterns.averageFocusSession < 20) {
      newRecommendations.push({
        id: 'focus-duration',
        type: 'productivity',
        priority: 'high',
        title: 'Optimize Focus Sessions',
        description: `Your average focus session is ${userPatterns.averageFocusSession} minutes. Try gradually increasing to 25 minutes for better productivity.`,
        actionable: true,
        impact: 'high',
        effort: 'medium',
        category: 'Focus Optimization',
        reasoning: 'Based on your current focus patterns, extending sessions could improve task completion'
      });
    }

    // Scheduling recommendations
    if (userPatterns.peakProductivityHours.length > 0) {
      newRecommendations.push({
        id: 'peak-hours',
        type: 'scheduling',
        priority: 'high',
        title: 'Schedule Important Tasks During Peak Hours',
        description: `Your most productive hours are ${userPatterns.peakProductivityHours.join(', ')}:00. Schedule complex tasks during these times.`,
        actionable: true,
        impact: 'high',
        effort: 'low',
        category: 'Smart Scheduling',
        reasoning: 'Data shows you perform best during these hours'
      });
    }

    // Wellness recommendations
    if (userPatterns.taskCompletionRate < 0.8) {
      newRecommendations.push({
        id: 'completion-rate',
        type: 'wellness',
        priority: 'medium',
        title: 'Improve Task Completion Rate',
        description: `Your completion rate is ${Math.round(userPatterns.taskCompletionRate * 100)}%. Consider breaking down large tasks into smaller steps.`,
        actionable: true,
        impact: 'medium',
        effort: 'medium',
        category: 'Task Management',
        reasoning: 'Lower completion rate may indicate task overwhelm'
      });
    }

    // Learning style recommendations
    if (userPatterns.learningStyle) {
      const learningRecommendations: Record<string, Recommendation> = {
        visual: {
          id: 'visual-learning',
          type: 'learning',
          priority: 'medium',
          title: 'Use Visual Learning Techniques',
          description: 'As a visual learner, try creating mind maps, diagrams, and color-coded notes to enhance retention.',
          actionable: true,
          impact: 'medium',
          effort: 'low',
          category: 'Learning Optimization',
          reasoning: 'Tailored to your visual learning preference'
        },
        reading: {
          id: 'reading-learning',
          type: 'learning',
          priority: 'medium',
          title: 'Optimize Reading Strategies',
          description: 'As a reading learner, focus on detailed notes, summaries, and structured outlines for better comprehension.',
          actionable: true,
          impact: 'medium',
          effort: 'low',
          category: 'Learning Optimization',
          reasoning: 'Tailored to your reading learning preference'
        },
        hands_on: {
          id: 'hands-on-learning',
          type: 'learning',
          priority: 'medium',
          title: 'Embrace Hands-On Learning',
          description: 'As a hands-on learner, prioritize practical exercises, experiments, and real-world applications.',
          actionable: true,
          impact: 'medium',
          effort: 'low',
          category: 'Learning Optimization',
          reasoning: 'Tailored to your hands-on learning preference'
        },
        auditory: {
          id: 'auditory-learning',
          type: 'learning',
          priority: 'medium',
          title: 'Leverage Auditory Learning',
          description: 'As an auditory learner, try explaining concepts aloud, using audio recordings, and participating in discussions.',
          actionable: true,
          impact: 'medium',
          effort: 'low',
          category: 'Learning Optimization',
          reasoning: 'Tailored to your auditory learning preference'
        }
      };

      if (learningRecommendations[userPatterns.learningStyle]) {
        newRecommendations.push(learningRecommendations[userPatterns.learningStyle]);
      }
    }

    // Goal-based recommendations
    const weeklyProgress = (userPatterns.weeklyGoals.achieved / userPatterns.weeklyGoals.target) * 100;
    if (weeklyProgress < 80) {
      newRecommendations.push({
        id: 'weekly-goals',
        type: 'productivity',
        priority: 'medium',
        title: 'Adjust Weekly Goals',
        description: `You've achieved ${Math.round(weeklyProgress)}% of your weekly goal. Consider adjusting targets or improving time management.`,
        actionable: true,
        impact: 'medium',
        effort: 'low',
        category: 'Goal Management',
        reasoning: 'Current goal progress suggests adjustment needed'
      });
    }

    // Stress management recommendations
    if (userPatterns.stressTriggers.includes('deadlines')) {
      newRecommendations.push({
        id: 'deadline-stress',
        type: 'wellness',
        priority: 'high',
        title: 'Manage Deadline Stress',
        description: 'Deadlines are a stress trigger for you. Try breaking tasks into smaller milestones with earlier deadlines.',
        actionable: true,
        impact: 'high',
        effort: 'medium',
        category: 'Stress Management',
        reasoning: 'Identified deadlines as a stress trigger'
      });
    }

    // Focus recommendations
    newRecommendations.push({
      id: 'energy-management',
      type: 'focus',
      priority: 'medium',
      title: 'Optimize Energy Management',
      description: 'Schedule your most challenging tasks during high-energy periods and save routine tasks for low-energy times.',
      actionable: true,
      impact: 'medium',
      effort: 'low',
      category: 'Energy Optimization',
      reasoning: 'Energy-aware scheduling improves productivity'
    });

    setRecommendations(newRecommendations);
    setIsLoading(false);
  };

  const handleApplyRecommendation = (id: string) => {
    setRecommendations(prev => 
      prev.map(rec => 
        rec.id === id ? { ...rec, applied: true } : rec
      )
    );
    setAppliedCount(prev => prev + 1);

    // Store applied recommendations for tracking
    const appliedRecs = JSON.parse(localStorage.getItem('appliedRecommendations') || '[]');
    appliedRecs.push({
      id,
      appliedAt: new Date().toISOString(),
      type: recommendations.find(r => r.id === id)?.type
    });
    localStorage.setItem('appliedRecommendations', JSON.stringify(appliedRecs));
  };

  const handleDismissRecommendation = (id: string) => {
    setRecommendations(prev => 
      prev.map(rec => 
        rec.id === id ? { ...rec, dismissed: true } : rec
      )
    );
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'productivity': return <TrendingIcon />;
      case 'wellness': return <PsychologyIcon />;
      case 'learning': return <LightbulbIcon />;
      case 'scheduling': return <ScheduleIcon />;
      case 'focus': return <SpeedIcon />;
      default: return <AssessmentIcon />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'productivity': return '#1976d2';
      case 'wellness': return '#388e3c';
      case 'learning': return '#f57c00';
      case 'scheduling': return '#7b1fa2';
      case 'focus': return '#d32f2f';
      default: return '#757575';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#f44336';
      case 'medium': return '#ff9800';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const filteredRecommendations = recommendations.filter(rec => {
    if (activeFilter === 'all') return !rec.dismissed;
    return rec.type === activeFilter && !rec.dismissed;
  });

  const typeFilters = [
    { id: 'all', label: 'All', count: recommendations.filter(r => !r.dismissed).length },
    { id: 'productivity', label: 'Productivity', count: recommendations.filter(r => r.type === 'productivity' && !r.dismissed).length },
    { id: 'wellness', label: 'Wellness', count: recommendations.filter(r => r.type === 'wellness' && !r.dismissed).length },
    { id: 'learning', label: 'Learning', count: recommendations.filter(r => r.type === 'learning' && !r.dismissed).length },
    { id: 'scheduling', label: 'Scheduling', count: recommendations.filter(r => r.type === 'scheduling' && !r.dismissed).length },
    { id: 'focus', label: 'Focus', count: recommendations.filter(r => r.type === 'focus' && !r.dismissed).length },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ mb: 3 }}>
        <CardContent>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
                <InsightIcon />
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Intelligent Recommendations
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Personalized insights based on your patterns
                </Typography>
              </Box>
              <Badge badgeContent={appliedCount} color="success">
                <CompletedIcon color="success" />
              </Badge>
            </Box>
            
            <Tooltip title="Refresh Recommendations">
              <IconButton onClick={generateRecommendations} disabled={isLoading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {/* User Patterns Summary */}
          {userPatterns && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>Your Patterns</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                <Chip 
                  label={`Peak Hours: ${userPatterns.peakProductivityHours.join(', ')}`} 
                  size="small" 
                  variant="outlined"
                />
                <Chip 
                  label={`Learning Style: ${userPatterns.learningStyle}`} 
                  size="small" 
                  variant="outlined"
                />
                <Chip 
                  label={`Completion Rate: ${Math.round(userPatterns.taskCompletionRate * 100)}%`} 
                  size="small" 
                  variant="outlined"
                />
                <Chip 
                  label={`Weekly Progress: ${Math.round((userPatterns.weeklyGoals.achieved / userPatterns.weeklyGoals.target) * 100)}%`} 
                  size="small" 
                  variant="outlined"
                />
              </Box>
            </Box>
          )}

          {/* Type Filters */}
          <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
            {typeFilters.map((filter) => (
              <motion.div
                key={filter.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Button
                  variant={activeFilter === filter.id ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => setActiveFilter(filter.id)}
                  sx={{ borderRadius: '20px' }}
                >
                  {filter.label} ({filter.count})
                </Button>
              </motion.div>
            ))}
          </Box>

          {/* Loading State */}
          {isLoading && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <LinearProgress sx={{ width: '100%', mb: 2 }} />
              <Typography variant="body2" color="textSecondary">
                Analyzing your patterns to generate personalized recommendations...
              </Typography>
            </Box>
          )}

          {/* Recommendations List */}
          <AnimatePresence>
            {!isLoading && filteredRecommendations.map((recommendation, index) => (
              <motion.div
                key={recommendation.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card 
                  sx={{ 
                    mb: 2, 
                    border: recommendation.applied ? '2px solid #4caf50' : '1px solid #e0e0e0',
                    bgcolor: recommendation.applied ? 'success.light' : 'background.paper',
                    position: 'relative'
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                      <Avatar sx={{ bgcolor: getTypeColor(recommendation.type), width: 40, height: 40 }}>
                        {getTypeIcon(recommendation.type)}
                      </Avatar>
                      
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {recommendation.title}
                          </Typography>
                          {recommendation.applied && (
                            <Chip label="Applied" size="small" color="success" />
                          )}
                          <Chip 
                            label={recommendation.priority} 
                            size="small" 
                            sx={{ 
                              bgcolor: getPriorityColor(recommendation.priority),
                              color: 'white',
                              fontSize: '0.7rem'
                            }} 
                          />
                        </Box>
                        
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {recommendation.description}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                          <Typography variant="caption" color="textSecondary">
                            Impact: {recommendation.impact}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            •
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Effort: {recommendation.effort}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            •
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {recommendation.category}
                          </Typography>
                        </Box>
                        
                        <Typography variant="caption" color="info.main" sx={{ fontStyle: 'italic', mb: 2, display: 'block' }}>
                          💡 {recommendation.reasoning}
                        </Typography>
                        
                        {!recommendation.applied && recommendation.actionable && (
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                              <Button
                                size="small"
                                variant="contained"
                                startIcon={<ActionIcon />}
                                onClick={() => handleApplyRecommendation(recommendation.id)}
                              >
                                Apply
                              </Button>
                            </motion.div>
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                              <Button
                                size="small"
                                variant="outlined"
                                startIcon={<SaveIcon />}
                              >
                                Save for Later
                              </Button>
                            </motion.div>
                          </Box>
                        )}
                      </Box>
                      
                      <IconButton
                        size="small"
                        onClick={() => handleDismissRecommendation(recommendation.id)}
                        sx={{ ml: 'auto' }}
                      >
                        ×
                      </IconButton>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Empty State */}
          {!isLoading && filteredRecommendations.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <InsightIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="textSecondary" sx={{ mb: 1 }}>
                No recommendations available
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Check back later for new personalized insights
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default IntelligentRecommendations;
