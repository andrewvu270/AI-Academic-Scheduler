# AI Academic Scheduler

An intelligent academic planning system that helps students optimize their study schedules by extracting deadlines from syllabi, predicting workload, and generating optimized daily study plans using machine learning.

##  Documentation

For detailed documentation, see the [docs/](docs/) directory:

- **[Installation Guide](docs/installation.md)** - Complete setup instructions including development environment
- **[System Architecture](docs/architecture.md)** - Component overview and data flow
- **[Machine Learning Guide](docs/machine-learning.md)** - ML model training and management
- **[Development Guide](docs/development.md)** - Development workflow and best practices
- **[API Reference](docs/api-reference.md)** - Complete endpoint documentation
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions

## 🚀 Features

- **📄 Syllabus Processing**: Upload PDF or image syllabi and automatically extract all assignments, exams, and deadlines
- **🤖 AI-Powered Extraction**: Uses OpenAI GPT to intelligently parse and categorize academic tasks
- **⚖️ Smart Weighting**: Automatically calculates task importance based on grade percentage, task type, and instructor emphasis
- **📊 Workload Prediction**: ML models predict how much time each task will take based on historical data
- **📅 Optimized Scheduling**: Generates daily and weekly study schedules optimized for productivity
- **🔔 Smart Notifications**: Timely reminders for upcoming deadlines and study sessions
- **📈 Progress Tracking**: Monitor study habits and task completion over time
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python**: Core programming language
- **SQLAlchemy**: SQL toolkit and ORM
- **Supabase**: Primary database (PostgreSQL backend)
- **OpenAI API**: For intelligent text extraction
- **LightGBM**: Machine learning for workload prediction
- **pdfplumber**: PDF text extraction
- **Tesseract**: OCR for image-based documents

### Frontend
- **React**: User interface library
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: React component library
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests

### Infrastructure
- **Docker**: Containerization (for backend services)

## 📋 Usage Guide

### 1. Create an Account

1. Navigate to the application
2. Click "Sign Up"
3. Enter your email and password
4. Verify your email if required

### 2. Add a Course

1. Go to the "Courses" page
2. Click "Add Course"
3. Enter course details (name, code, semester)
4. Save the course

### 3. Upload a Syllabus

1. Select a course
2. Click "Upload Syllabus"
3. Choose a PDF or image file
4. Wait for AI processing
5. Review extracted tasks and make corrections if needed

### 4. View Your Schedule

1. Go to the "Schedule" page
2. Set your available study hours
3. View your optimized daily schedule
4. Check off completed tasks

### 5. Track Progress

1. Use the timer to track study sessions
2. Mark tasks as complete
3. View analytics on your study habits

## 🗺️ Roadmap

### Version 1.0 (Current)
- [x] Basic syllabus processing
- [x] Task extraction and weighting
- [x] Schedule generation
- [x] User authentication
- [x] Study session tracking

### Version 1.1 (Planned)
- [ ] Mobile app (React Native)
- [ ] Calendar integration
- [ ] Advanced analytics
- [ ] Study group features

### Version 2.0 (Future)
- [ ] Collaborative scheduling
- [ ] AI-powered study recommendations
- [ ] Integration with learning management systems
- [ ] Advanced ML models for personalization

## 🔒 Security Considerations

- All API endpoints require authentication
- JWT tokens with expiration
- Input validation and sanitization
- File upload restrictions
- CORS configuration
- Environment variable protection
- SQL injection prevention through ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style
- Write tests for new features
- Update documentation
- Ensure all tests pass
- Use descriptive commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- FastAPI for the web framework
- React for the frontend framework
- All contributors and users of this project

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Installation Guide](docs/installation.md)
2. Search existing [Issues](https://github.com/yourusername/ai-academic-scheduler/issues)
3. Create new issue with detailed information
4. Contact the development team

---

**Built with ❤️ for students everywhere**