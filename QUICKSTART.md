# MyDesk Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key
- Supabase account (optional for cloud sync)

### Installation

```bash
# Clone and navigate to project
cd academic-scheduler

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Environment Variables

Create `.env` file in backend directory:

```bash
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini  # Cost-effective option
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Run the Application

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 📡 API Examples

### Parse a Document
```bash
curl -X POST http://localhost:8000/api/v2/agents/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Assignment 1 due December 15, 2025. Worth 30% of grade.",
    "source_type": "syllabus"
  }'
```

### Predict Workload
```bash
curl -X POST http://localhost:8000/api/v2/agents/predict \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "title": "Research Paper",
      "description": "Write 10-page research paper on AI ethics",
      "task_type": "Assignment",
      "grade_percentage": 40
    }
  }'
```

### Full Pipeline (Recommended)
```bash
curl -X POST http://localhost:8000/api/v2/agents/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your syllabus text here...",
    "source_type": "pdf",
    "schedule_days": 7
  }'
```

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v
```

## 🏗️ Architecture

**5 Agents + MCP Orchestrator:**

1. **Task Parsing Agent** - Extracts tasks from documents
2. **Workload Prediction Agent** - Estimates hours + stress (hybrid LLM+ML)
3. **Prioritization Agent** - Ranks tasks intelligently
4. **Schedule Optimization Agent** - Balances workload, prevents burnout
5. **Natural Language Agent** - Processes queries

**MCP Orchestrator** - Coordinates all agents and manages workflows

## 🔑 Key Features

- ✅ Multi-agent AI architecture
- ✅ Hybrid LLM + ML predictions
- ✅ Stress & burnout detection
- ✅ Natural language interface
- ✅ Auto-build & auto-test CI/CD
- ✅ Comprehensive test suite

## 📚 Documentation

- [README.md](file:///Users/andrwvu/Desktop/SWE/Projects/academic-scheduler/README.md) - Full documentation
- [walkthrough.md](file:///Users/andrwvu/.gemini/antigravity/brain/ad0432a0-cda4-4183-be7d-1ce32c4be6ee/walkthrough.md) - Detailed walkthrough
- [implementation_plan.md](file:///Users/andrwvu/.gemini/antigravity/brain/ad0432a0-cda4-4183-be7d-1ce32c4be6ee/implementation_plan.md) - Implementation details

## 🎯 Next Steps

1. **Frontend Integration** - Connect UI to new agent endpoints
2. **Stress Visualization** - Add charts and burnout warnings
3. **Natural Language UI** - Add chat-style interface
4. **Deploy** - Push to production with CI/CD

---

**Branch:** `PrototypeMyDesk`  
**Status:** ✅ Backend complete, ready for frontend integration
