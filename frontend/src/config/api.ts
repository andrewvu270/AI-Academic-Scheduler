// Centralized API configuration
export const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL;
//  || 'http://localhost:8000';

// Debug: Log the API URL being used
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Environment variables:', (import.meta as any).env);

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Common API endpoints
export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  GOOGLE_URL: '/api/auth/google-url',
  
  // Upload
  UPLOAD_PREVIEW: '/api/upload/preview',
  UPLOAD_SYLLABUS: '/api/upload/syllabus',
  
  // Tasks
  TASKS: '/api/tasks',
  TASK_COMPLETE: (id: string) => `/api/tasks/${id}/complete`,
  
  // Courses
  COURSES: '/api/courses',
  
  // Survey
  SURVEY_SUBMIT: '/api/survey/submit',
  
  // Study Plan
  STUDY_PLAN_GENERATE: '/api/study-plan/generate',
  
  // ML
  ML_PREDICT: '/api/ml/predict-workload',
  
  // Guest
  GUEST_SESSION: '/api/guest/session',
  GUEST_MIGRATE: (id: string) => `/api/guest/migrate/${id}`,
} as const;
