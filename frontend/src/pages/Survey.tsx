import React, { useState } from 'react';
import {
  Container,
  Paper,
  Box,
  Typography,
  Button,
  TextField,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Slider,
  FormControlLabel,
  Checkbox,
  Grid,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';

interface SurveyItem {
  task_title: string;
  task_type: string;
  due_date: string;
  grade_percentage: number;
  estimated_hours: number;
  actual_hours: number;
  difficulty_level: number;
  priority_rating: number;
  completed: boolean;
  completion_date: string;
  notes: string;
}

const Survey: React.FC = () => {
  const [items, setItems] = useState<SurveyItem[]>([
    {
      task_title: '',
      task_type: 'Assignment',
      due_date: '',
      grade_percentage: 0,
      estimated_hours: 0,
      actual_hours: 0,
      difficulty_level: 3,
      priority_rating: 3,
      completed: false,
      completion_date: '',
      notes: '',
    },
  ]);
  const [userFeedback, setUserFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAddItem = () => {
    setItems([
      ...items,
      {
        task_title: '',
        task_type: 'Assignment',
        due_date: '',
        grade_percentage: 0,
        estimated_hours: 0,
        actual_hours: 0,
        difficulty_level: 3,
        priority_rating: 3,
        completed: false,
        completion_date: '',
        notes: '',
      },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleItemChange = (index: number, field: keyof SurveyItem, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const handleSubmit = async () => {
    if (items.some(item => !item.task_title || !item.due_date)) {
      setMessage({ type: 'error', text: 'Please fill in all required fields' });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/survey/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          responses: items,
          user_feedback: userFeedback,
        }),
      });

      if (!response.ok) throw new Error('Failed to submit survey');
      
      setMessage({ type: 'success', text: 'Survey submitted successfully! Thank you for contributing to model training.' });
      setItems([
        {
          task_title: '',
          task_type: 'Assignment',
          due_date: '',
          grade_percentage: 0,
          estimated_hours: 0,
          actual_hours: 0,
          difficulty_level: 3,
          priority_rating: 3,
          completed: false,
          completion_date: '',
          notes: '',
        },
      ]);
      setUserFeedback('');
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to submit survey' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
          Task Data Collection Survey
        </Typography>
        <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
          Help us improve our AI scheduling model by sharing your task completion data.
          Your responses will be used to train a machine learning model for better task prioritization.
        </Typography>
      </Box>

      {message && (
        <Alert severity={message.type} sx={{ mb: 3 }}>
          {message.text}
        </Alert>
      )}

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Tasks ({items.length})
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddItem}
            disabled={loading}
          >
            Add Task
          </Button>
        </Box>

        {items.map((item, index) => (
          <Card key={index} sx={{ mb: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  Task {index + 1}
                </Typography>
                <Button
                  size="small"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => handleRemoveItem(index)}
                  disabled={items.length === 1}
                >
                  Remove
                </Button>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Task Title *"
                    value={item.task_title}
                    onChange={(e) => handleItemChange(index, 'task_title', e.target.value)}
                    disabled={loading}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Task Type"
                    value={item.task_type}
                    onChange={(e) => handleItemChange(index, 'task_type', e.target.value)}
                    disabled={loading}
                    SelectProps={{
                      native: true,
                    }}
                  >
                    <option value="Assignment">Assignment</option>
                    <option value="Exam">Exam</option>
                    <option value="Quiz">Quiz</option>
                    <option value="Project">Project</option>
                    <option value="Reading">Reading</option>
                    <option value="Lab">Lab</option>
                  </TextField>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="Due Date *"
                    value={item.due_date}
                    onChange={(e) => handleItemChange(index, 'due_date', e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    disabled={loading}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Grade Percentage (0-100)"
                    value={item.grade_percentage}
                    onChange={(e) => handleItemChange(index, 'grade_percentage', parseFloat(e.target.value))}
                    disabled={loading}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Estimated Hours"
                    value={item.estimated_hours}
                    onChange={(event) => handleItemChange(index, 'estimated_hours', parseFloat(event.target.value))}
                    disabled={loading}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Actual Hours Spent"
                    value={item.actual_hours}
                    onChange={(event) => handleItemChange(index, 'actual_hours', parseFloat(event.target.value))}
                    disabled={loading}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Difficulty Level: {item.difficulty_level}/5
                    </Typography>
                    <Slider
                      value={item.difficulty_level}
                      onChange={(_event, value) => handleItemChange(index, 'difficulty_level', value)}
                      min={1}
                      max={5}
                      marks
                      disabled={loading}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Priority Rating: {item.priority_rating}/5
                    </Typography>
                    <Slider
                      value={item.priority_rating}
                      onChange={(_event, value) => handleItemChange(index, 'priority_rating', value)}
                      min={1}
                      max={5}
                      marks
                      disabled={loading}
                    />
                  </Box>
                </Grid>

                <Grid item xs={12} sm={6}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={item.completed}
                        onChange={(e) => handleItemChange(index, 'completed', e.target.checked)}
                        disabled={loading}
                      />
                    }
                    label="Completed"
                  />
                </Grid>
                {item.completed && (
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      type="date"
                      label="Completion Date"
                      value={item.completion_date}
                      onChange={(e) => handleItemChange(index, 'completion_date', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      disabled={loading}
                    />
                  </Grid>
                )}

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Notes (optional)"
                    value={item.notes}
                    onChange={(e) => handleItemChange(index, 'notes', e.target.value)}
                    disabled={loading}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        ))}
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
          Additional Feedback (Optional)
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={4}
          label="Any additional feedback about task prioritization or scheduling?"
          value={userFeedback}
          onChange={(e) => setUserFeedback(e.target.value)}
          disabled={loading}
        />
      </Paper>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          onClick={(): void => window.history.back()}
          disabled={loading}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading}
          sx={{ minWidth: 150 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Submit Survey'}
        </Button>
      </Box>
    </Container>
  );
};

export default Survey;
