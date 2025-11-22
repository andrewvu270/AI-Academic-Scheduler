-- Create survey_responses table for storing training data
CREATE TABLE IF NOT EXISTS survey_responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_title VARCHAR(255) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    course_name VARCHAR(255),
    due_date DATE NOT NULL,
    grade_percentage DECIMAL(5,2) NOT NULL,
    estimated_hours DECIMAL(5,2) NOT NULL,
    actual_hours DECIMAL(5,2) NOT NULL,
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    priority_rating INTEGER CHECK (priority_rating >= 1 AND priority_rating <= 5),
    completed BOOLEAN DEFAULT false,
    completion_date DATE,
    notes TEXT,
    user_feedback TEXT,
    is_synthetic BOOLEAN DEFAULT false, -- Flag for AI-generated data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_survey_responses_task_type ON survey_responses(task_type);
CREATE INDEX idx_survey_responses_created_at ON survey_responses(created_at);
CREATE INDEX idx_survey_responses_is_synthetic ON survey_responses(is_synthetic);

-- Enable Row Level Security
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users to insert their own data
CREATE POLICY "Users can insert their own survey responses" ON survey_responses
    FOR INSERT WITH CHECK (auth.uid() = created_by);

-- Create policy for reading (everyone can read for now, adjust as needed)
CREATE POLICY "Anyone can read survey responses" ON survey_responses
    FOR SELECT USING (true);
