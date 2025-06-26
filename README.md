# MediTracked - Advanced Clinical Patient Tracking and Telemedicine System

MediTracked is a comprehensive, AI-powered healthcare management system designed for modern healthcare institutions. This advanced platform includes patient tracking, appointment management, telemedicine capabilities, AI health analytics, and comprehensive clinical workflows.

## 🚀 Features

### Core Healthcare Management
- **Advanced User & Role Management**: Patient, doctor, receptionist, and admin roles with granular permissions
- **Comprehensive Patient Management**: Complete patient profiles, medical history, treatment tracking
- **Smart Appointment System**: Intelligent scheduling with availability checking and conflict resolution
- **Digital Treatment Records**: Electronic health records with integrated prescription management
- **Advanced Notification System**: Multi-channel notifications (email, SMS, push) with templates

### 🩺 Telemedicine & Remote Care
- **Video Consultations**: HD video/audio calls with screen sharing capabilities
- **Real-time Chat**: Secure messaging during consultations with file sharing
- **Session Recording**: Automatic session recording for compliance and review
- **Virtual Waiting Rooms**: Organized patient queues for teleconsultations
- **Multi-device Support**: Desktop, tablet, and mobile compatibility

### 🤖 AI-Powered Health Analytics
- **Symptom Analysis**: AI-driven symptom checker with health recommendations
- **Drug Interaction Detection**: Comprehensive medication safety checking
- **Health Risk Assessment**: Predictive analytics for patient health risks
- **Personalized Health Insights**: AI-generated health recommendations
- **Clinical Decision Support**: Evidence-based treatment suggestions

### 📊 Advanced Analytics & Reporting
- **Real-time Dashboard**: Comprehensive analytics with interactive charts
- **Performance Metrics**: Hospital efficiency and patient outcome tracking
- **Predictive Analytics**: AI-powered forecasting for resource planning
- **Custom Reports**: Flexible reporting with multiple export formats
- **Data Visualization**: Interactive charts and graphs for clinical insights

### 🌍 Internationalization & Accessibility
- **Multi-language Support**: Turkish, English, Arabic, German, French
- **Medical Terminology Database**: Standardized medical terms across languages
- **Responsive Design**: Mobile-first approach with full responsive layout
- **Accessibility Features**: WCAG compliant with screen reader support

### 📱 Mobile & API Support
- **RESTful API**: Complete mobile app integration support
- **Cross-platform Mobile**: iOS and Android compatibility
- **Offline Capabilities**: Critical features available offline
- **Push Notifications**: Real-time mobile notifications
- **Secure Authentication**: JWT-based security with multi-factor authentication

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+ 
- Node.js 16+ (for development)
- Redis (for real-time features)
- PostgreSQL (recommended for production)

### Quick Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/meditracked.git
   cd meditracked
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/Mac
   # or venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database setup:**
   ```bash
   python manage.py manage_migrations
   python manage.py setup_meditracked --all
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Start Redis (for real-time features):**
   ```bash
   redis-server
   ```

### Production Deployment
For production deployment, see our [Deployment Guide](docs/deployment.md).

## 👥 Default User Accounts

After running the setup command, you'll have these test accounts:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Administrator | Full system access |
| `dr_sarah` | `doctor123` | Doctor (Cardiology) | Sample cardiologist |
| `dr_michael` | `doctor123` | Doctor (Neurology) | Sample neurologist |
| `dr_emma` | `doctor123` | Doctor (Pediatrics) | Sample pediatrician |
| `receptionist` | `receptionist123` | Receptionist | Front desk staff |
| `patient_john` | `patient123` | Patient | Sample patient |
| `patient_jane` | `patient123` | Patient | Sample patient |

## 🏗️ System Architecture

### Core Modules
- **`core/`** - Core functionality, analytics, AI features
- **`users/`** - User management and authentication
- **`appointments/`** - Appointment scheduling and management
- **`treatments/`** - Medical treatments and prescriptions
- **`telemedicine/`** - Video consultations and remote care

### Key Components
- **Analytics Engine** (`core/analytics.py`) - Real-time data analysis
- **AI Health Assistant** (`core/ai_features.py`) - ML-powered health insights
- **Mobile API** (`core/mobile_api.py`) - REST API for mobile apps
- **Notification System** (`core/models_notifications.py`) - Multi-channel notifications
- **Internationalization** (`core/models_i18n.py`) - Multi-language support

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/meditracked

# AI Services
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_hf_key

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Redis (for real-time features)
REDIS_URL=redis://localhost:6379/0
```

### Feature Toggles
Enable/disable features in `settings.py`:
```python
AI_SETTINGS = {
    'ENABLE_AI_FEATURES': True,
    'SYMPTOM_ANALYSIS_ENABLED': True,
    'DRUG_INTERACTION_CHECK': True,
    'HEALTH_RISK_ASSESSMENT': True,
}

TELEMEDICINE_SETTINGS = {
    'MAX_SESSION_DURATION': 120,  # minutes
    'RECORDING_ENABLED': True,
    'AUTO_END_SESSION_AFTER': 150,
}
```

## 📱 API Documentation

### Authentication
```bash
# Get API token
curl -X POST http://localhost:8000/core/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token your_token_here" \
  http://localhost:8000/core/api/dashboard/
```

### Key Endpoints
- `GET /core/api/dashboard/` - User dashboard data
- `GET /core/api/appointments/` - User appointments
- `POST /core/api/appointments/` - Create appointment
- `GET /core/api/health-summary/` - Health summary
- `POST /core/api/ai/symptom-check/` - AI symptom analysis
- `GET /telemedicine/` - Telemedicine sessions
- `POST /telemedicine/schedule/` - Schedule teleconsultation

## 🚀 Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test telemedicine
python manage.py test core.tests.test_ai_features

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Development Commands
```bash
# Create migrations for new models
python manage.py manage_migrations

# Reset development database
python manage.py manage_migrations --reset
python manage.py setup_meditracked --all

# Generate sample data
python manage.py setup_meditracked --sample-data

# Check system health
python manage.py check --deploy
```

## 🎯 Usage Examples

### Telemedicine Session
1. **Schedule Session**: Doctor or patient schedules a teleconsultation
2. **Join Session**: Both parties join via video link
3. **Consultation**: Video/audio call with real-time chat and file sharing
4. **Documentation**: Session notes, prescriptions, and follow-up plans
5. **Recording**: Automatic session recording for compliance

### AI Health Assistant
1. **Symptom Input**: Patient describes symptoms to AI assistant
2. **Analysis**: AI analyzes symptoms and medical history
3. **Recommendations**: Evidence-based health recommendations
4. **Risk Assessment**: Identification of potential health risks
5. **Doctor Referral**: Automatic referral suggestions when needed

### Analytics Dashboard
1. **Real-time Metrics**: Live hospital performance indicators
2. **Predictive Analytics**: AI-powered forecasting and insights
3. **Custom Reports**: Flexible reporting with multiple formats
4. **Data Export**: PDF, Excel, CSV export capabilities

## 🔒 Security Features

- **Multi-factor Authentication** (MFA)
- **Role-based Access Control** (RBAC)
- **Data Encryption** at rest and in transit
- **HIPAA Compliance** features
- **Audit Logging** for all critical actions
- **Session Management** with automatic timeout
- **API Rate Limiting** and DDoS protection

## 🌟 Advanced Features

### AI & Machine Learning
- Symptom analysis with medical knowledge base
- Drug interaction detection using pharmaceutical databases
- Predictive health risk modeling
- Personalized treatment recommendations
- Clinical decision support tools

### Telemedicine
- WebRTC-based video calling
- Screen sharing for consultations
- Real-time chat with file sharing
- Session recording and playback
- Virtual waiting rooms
- Multi-device support

### Analytics & Reporting
- Real-time dashboard with live metrics
- Interactive charts and visualizations
- Predictive analytics for resource planning
- Custom report generation
- Data export in multiple formats
- Performance benchmarking

## 🛡️ Compliance & Standards

- **HIPAA** - Health Insurance Portability and Accountability Act
- **GDPR** - General Data Protection Regulation
- **HL7 FHIR** - Healthcare data exchange standards
- **ICD-10** - International Classification of Diseases
- **SNOMED CT** - Systematized Nomenclature of Medicine Clinical Terms

## 📞 Support & Documentation

- 📚 [Full Documentation](https://docs.meditracked.com)
- 🐛 [Issue Tracker](https://github.com/your-org/meditracked/issues)
- 💬 [Community Forum](https://community.meditracked.com)
- 📧 [Email Support](mailto:support@meditracked.com)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django & Django REST Framework communities
- OpenAI for AI capabilities
- WebRTC for real-time communication
- Chart.js for data visualization
- Bootstrap for responsive design

---

**MediTracked** - Transforming Healthcare Through Technology

For more information, visit [www.meditracked.com](https://www.meditracked.com)
|------|-------------|
| Patient | - Can view their own appointments<br>- Can view their own treatment history<br>- Can update their own profile |
| Doctor | - Can view their own appointments<br>- Can add treatments and prescriptions to their patients<br>- Can view information about their patients |
| Receptionist | - Can create patient records<br>- Can create and update appointments<br>- Can view all patients and appointments |
| Admin | - Full system access<br>- Can manage all users<br>- Can view and edit all data |

## Technologies

- Django 5.2
- SQLite (for development)
- Bootstrap 5
- JavaScript

## Screenshots

<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 38" src="https://github.com/user-attachments/assets/08e809ee-f8b1-497e-aed0-649e98d03ad7" />

<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 42" src="https://github.com/user-attachments/assets/9de98ddc-d74d-40ca-a96b-0f71fe205b2d" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 11 03" src="https://github.com/user-attachments/assets/01ccd4f5-3e33-460b-b64f-1323187f34a1" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 50" src="https://github.com/user-attachments/assets/bb5cbe50-643c-4fa3-8f4b-efbe1a9150ea" />
<img width="1710" alt="Ekran Resmi 2025-06-15 15 10 46" src="https://github.com/user-attachments/assets/e5073729-d999-4352-9b0f-2e6f07988d10" />


## License

This project is licensed under the Apache 2.0 License.

## Contact

Please get in touch with any questions or feedback.

---

Developer: K. Umut Araz 
