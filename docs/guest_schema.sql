-- Guest Mode Tables for Supabase
-- Run this in Supabase SQL Editor

-- Guest sessions table
CREATE TABLE IF NOT EXISTS guest_sessions (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_accessed TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Guest tasks table
CREATE TABLE IF NOT EXISTS guest_tasks (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  guest_session_id TEXT NOT NULL REFERENCES guest_sessions(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  task_type TEXT NOT NULL,
  due_date TIMESTAMP WITH TIME ZONE NOT NULL,
  weight_score FLOAT DEFAULT 0.5,
  predicted_hours FLOAT DEFAULT 4.0,
  priority_score FLOAT DEFAULT 0.5,
  status TEXT DEFAULT 'pending',
  grade_percentage FLOAT DEFAULT 0.0,
  extra_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Guest courses table
CREATE TABLE IF NOT EXISTS guest_courses (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  guest_session_id TEXT NOT NULL REFERENCES guest_sessions(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_guest_tasks_session ON guest_tasks(guest_session_id);
CREATE INDEX IF NOT EXISTS idx_guest_courses_session ON guest_courses(guest_session_id);
CREATE INDEX IF NOT EXISTS idx_guest_tasks_due_date ON guest_tasks(due_date);

-- Enable RLS
ALTER TABLE guest_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE guest_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE guest_courses ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow public access (no auth needed for guests)
CREATE POLICY "Allow guest session creation" ON guest_sessions
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow guest session access" ON guest_sessions
  FOR SELECT USING (true);

CREATE POLICY "Allow guest task creation" ON guest_tasks
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow guest task access" ON guest_tasks
  FOR SELECT USING (true);

CREATE POLICY "Allow guest task update" ON guest_tasks
  FOR UPDATE USING (true);

CREATE POLICY "Allow guest task delete" ON guest_tasks
  FOR DELETE USING (true);

CREATE POLICY "Allow guest course creation" ON guest_courses
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow guest course access" ON guest_courses
  FOR SELECT USING (true);

CREATE POLICY "Allow guest course update" ON guest_courses
  FOR UPDATE USING (true);

CREATE POLICY "Allow guest course delete" ON guest_courses
  FOR DELETE USING (true);
