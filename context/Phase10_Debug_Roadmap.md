# Phase 10: Debug Roadmap - ADCC Analysis Engine v0.6.0-alpha.6

## Overview
This debug roadmap provides a systematic approach to testing, debugging, and deploying the complete ADCC Analysis Engine. It covers all major system components, integration testing, and Railway deployment preparation.

## Table of Contents
1. [Pre-Debugging Setup](#pre-debugging-setup)
2. [Core System Debugging](#core-system-debugging)
3. [Data Acquisition Debugging](#data-acquisition-debugging)
4. [Data Processing Debugging](#data-processing-debugging)
5. [Analytics Engine Debugging](#analytics-engine-debugging)
6. [Web UI Debugging](#web-ui-debugging)
7. [Integration Testing](#integration-testing)
8. [Performance Testing](#performance-testing)
9. [Railway Deployment Setup](#railway-deployment-setup)
10. [Production Readiness](#production-readiness)

---

## 1. Pre-Debugging Setup

### 1.1 Environment Verification
**Commands to run:**
```bash
# Verify Python environment
python --version
pip list

# Verify virtual environment
echo $VIRTUAL_ENV

# Check project structure
ls -la src/
ls -la tests/
```

**Expected Results:**
- Python 3.9+ installed
- All dependencies from requirements.txt installed
- Virtual environment active
- All source directories present

### 1.2 Test Environment Setup
**Commands to run:**
```bash
# Run all existing tests
pytest tests/ -v --tb=short

# Check test coverage
pytest --cov=src --cov-report=html --cov-report=term

# Verify no critical errors
python tests/verify_phase9.py
```

**Expected Results:**
- All tests pass (97.1%+ success rate)
- No critical import errors
- Coverage report generated

### 1.3 Data Directory Structure
**Verify these directories exist:**
```
data/
├── raw/           # Raw downloaded files
├── processed/     # Processed data files
└── datastore/     # Final output files
downloads/         # Temporary downloads
logs/              # Application logs
tests/             # Test files and outputs
```

---

## 2. Core System Debugging

### 2.1 Configuration System
**Test File:** `src/config/settings.py`

**Debug Steps:**
1. **Test Configuration Loading**
   ```bash
   python -c "from src.config.settings import get_settings; print(get_settings())"
   ```

2. **Test Environment Variables**
   ```bash
   # Set test environment variables
   export SMOOTHCOMP_USERNAME="test_user"
   export SMOOTHCOMP_PASSWORD="test_pass"
   export LOG_LEVEL="DEBUG"
   
   # Test loading
   python -c "from src.config.settings import get_settings; s = get_settings(); print(f'Username: {s.smoothcomp_username}')"
   ```

**Expected Results:**
- Configuration loads without errors
- Environment variables properly read
- Default values used when variables not set

### 2.2 Logging System
**Test File:** `src/utils/logger.py`

**Debug Steps:**
1. **Test Basic Logging**
   ```python
   from src.utils.logger import logger
   
   logger.info("Test info message")
   logger.warning("Test warning message")
   logger.error("Test error message")
   ```

2. **Check Log Files**
   ```bash
   ls -la logs/
   tail -f logs/app.log
   ```

**Expected Results:**
- Log messages appear in console and log files
- Proper log levels and formatting
- No encoding issues

### 2.3 File Handler
**Test File:** `src/utils/file_handler.py`

**Debug Steps:**
1. **Test JSON Operations**
   ```python
   from src.utils.file_handler import save_json_file, load_json_file
   from pathlib import Path
   
   test_data = {"test": "data", "number": 123}
   test_file = Path("tests/test_output.json")
   
   # Save and load
   save_json_file(test_data, test_file)
   loaded_data = load_json_file(test_file)
   print(f"Data matches: {test_data == loaded_data}")
   ```

2. **Test Directory Operations**
   ```python
   from src.utils.file_handler import ensure_directory_exists
   
   test_dir = Path("tests/test_directory")
   ensure_directory_exists(test_dir)
   print(f"Directory exists: {test_dir.exists()}")
   ```

**Expected Results:**
- JSON files save and load correctly
- Directories created as needed
- No file permission issues

---

## 3. Data Acquisition Debugging

### 3.1 Smoothcomp Client
**Test File:** `src/data_acquisition/smoothcomp_client.py`

**Debug Steps:**
1. **Test Client Initialization**
   ```python
   from src.data_acquisition.smoothcomp_client import SmoothcompClient
   
   client = SmoothcompClient("test_user", "test_pass")
   print(f"Client initialized: {client is not None}")
   ```

2. **Test API Endpoints** (with real credentials)
   ```python
   # Test event info retrieval
   event_info = client.get_event_info("E12692")
   print(f"Event info: {event_info}")
   
   # Test registration data
   registrations = client.get_registrations("E12692")
   print(f"Registrations count: {len(registrations) if registrations else 0}")
   ```

**Expected Results:**
- Client initializes without errors
- API calls return expected data structure
- Error handling works for invalid credentials

### 3.2 Browser Automation
**Test File:** `src/data_acquisition/browser_automation.py`

**Debug Steps:**
1. **Test Browser Startup**
   ```python
   from src.data_acquisition.browser_automation import BrowserAutomation
   from pathlib import Path
   
   download_dir = Path("downloads")
   browser = BrowserAutomation(download_dir=download_dir)
   
   # Test browser start
   browser.start_browser()
   print("Browser started successfully")
   
   # Test browser stop
   browser.stop_browser()
   print("Browser stopped successfully")
   ```

2. **Test Navigation** (manual verification)
   ```python
   # Navigate to event page
   browser.navigate_to_event("E12692")
   print("Navigation completed")
   ```

**Expected Results:**
- Browser starts and stops cleanly
- No Chrome driver issues
- Download directory accessible

### 3.3 File Monitor
**Test File:** `src/data_acquisition/file_monitor.py`

**Debug Steps:**
1. **Test File Detection**
   ```python
   from src.data_acquisition.file_monitor import FileMonitor
   from pathlib import Path
   
   watch_dir = Path("downloads")
   monitor = FileMonitor(watch_directory=watch_dir, file_patterns=["*.csv", "*.xlsx"])
   
   # Start monitoring
   monitor.start_monitoring()
   print("File monitoring started")
   
   # Create test file
   test_file = watch_dir / "test.csv"
   test_file.write_text("test,data")
   
   # Check detection
   new_files = monitor.get_new_files()
   print(f"Detected files: {new_files}")
   
   # Stop monitoring
   monitor.stop_monitoring()
   ```

**Expected Results:**
- File monitoring starts without errors
- New files detected correctly
- File patterns work as expected

---

## 4. Data Processing Debugging

### 4.1 Data Validation
**Test File:** `src/data_processing/validators.py`

**Debug Steps:**
1. **Test Athlete Data Validation**
   ```python
   from src.data_processing.validators import validate_athlete_data
   
   test_athlete = {
       "name": "Test Athlete",
       "age_class": "adult",
       "skill_level": "advanced",
       "weight_class": "91kg"
   }
   
   result = validate_athlete_data(test_athlete)
   print(f"Validation result: {result}")
   ```

2. **Test Match Data Validation**
   ```python
   from src.data_processing.validators import validate_match_data
   
   test_match = {
       "winner_id": "A123456",
       "loser_id": "A789012",
       "win_type": "SUBMISSION",
       "division": "D-A-M-ADV-W91KG"
   }
   
   result = validate_match_data(test_match)
   print(f"Match validation: {result}")
   ```

**Expected Results:**
- Valid data passes validation
- Invalid data properly rejected
- Clear error messages

### 4.2 Data Transformation
**Test File:** `src/data_processing/transformers.py`

**Debug Steps:**
1. **Test CSV to DataFrame Conversion**
   ```python
   from src.data_processing.transformers import csv_to_dataframe
   
   # Create test CSV
   test_csv = "tests/test_data.csv"
   with open(test_csv, 'w') as f:
       f.write("name,age_class,skill_level\n")
       f.write("Test Athlete,adult,advanced\n")
   
   df = csv_to_dataframe(test_csv)
   print(f"DataFrame shape: {df.shape}")
   print(f"Columns: {df.columns.tolist()}")
   ```

2. **Test Excel Processing**
   ```python
   from src.data_processing.transformers import excel_to_dataframe
   
   # Test with sample Excel file
   # (Create or download a sample Excel file first)
   ```

**Expected Results:**
- CSV files load correctly
- Excel files process without errors
- Data types properly inferred

---

## 5. Analytics Engine Debugging

### 5.1 Glicko Engine
**Test File:** `src/analytics/glicko_engine.py`

**Debug Steps:**
1. **Test Basic Glicko Calculation**
   ```python
   from src.analytics.glicko_engine import GlickoEngine
   
   engine = GlickoEngine()
   
   # Test rating calculation
   current_rating = 1500
   current_rd = 350
   opponent_rating = 1600
   opponent_rd = 300
   result = 1  # Win
   
   new_rating, new_rd = engine.calculate_new_rating(
       current_rating, current_rd, opponent_rating, opponent_rd, result
   )
   
   print(f"New rating: {new_rating:.2f}")
   print(f"New RD: {new_rd:.2f}")
   ```

2. **Test Batch Processing**
   ```python
   # Test processing multiple matches
   matches = [
       {"opponent_rating": 1600, "opponent_rd": 300, "result": 1},
       {"opponent_rating": 1400, "opponent_rd": 400, "result": 0},
       {"opponent_rating": 1550, "opponent_rd": 320, "result": 1}
   ]
   
   final_rating, final_rd = engine.process_matches(current_rating, current_rd, matches)
   print(f"Final rating: {final_rating:.2f}")
   print(f"Final RD: {final_rd:.2f}")
   ```

**Expected Results:**
- Ratings calculated correctly
- RD decreases with more matches
- Win/loss affects rating appropriately

### 5.2 Record Calculator
**Test File:** `src/analytics/record_calculator.py`

**Debug Steps:**
1. **Test Record Calculation**
   ```python
   from src.analytics.record_calculator import RecordCalculator
   
   calculator = RecordCalculator()
   
   # Test record calculation
   matches = [
       {"result": "WIN", "win_type": "SUBMISSION"},
       {"result": "LOSS", "win_type": "POINTS"},
       {"result": "WIN", "win_type": "SUBMISSION"}
   ]
   
   record = calculator.calculate_record(matches)
   print(f"Record: {record}")
   ```

**Expected Results:**
- Win/loss counts correct
- Win types properly categorized
- Win percentage calculated correctly

### 5.3 Medal Tracker
**Test File:** `src/analytics/medal_tracker.py`

**Debug Steps:**
1. **Test Medal Counting**
   ```python
   from src.analytics.medal_tracker import MedalTracker
   
   tracker = MedalTracker()
   
   # Test medal assignment
   event_results = [
       {"athlete_id": "A123456", "position": 1, "division": "D-A-M-ADV-W91KG"},
       {"athlete_id": "A789012", "position": 2, "division": "D-A-M-ADV-W91KG"},
       {"athlete_id": "A345678", "position": 3, "division": "D-A-M-ADV-W91KG"}
   ]
   
   medals = tracker.assign_medals(event_results)
   print(f"Medals assigned: {medals}")
   ```

**Expected Results:**
- Gold, silver, bronze properly assigned
- Medal counts accurate
- No duplicate medals

---

## 6. Web UI Debugging

### 6.1 FastAPI Application
**Test File:** `src/web_ui/main.py`

**Debug Steps:**
1. **Test Application Startup**
   ```bash
   # Start the application
   uvicorn src.web_ui.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Test Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Test API Documentation**
   - Open browser to `http://localhost:8000/docs`
   - Verify all endpoints listed
   - Test interactive documentation

**Expected Results:**
- Application starts without errors
- Health check returns 200 OK
- API documentation accessible

### 6.2 Authentication System
**Test File:** `src/web_ui/api/auth.py`

**Debug Steps:**
1. **Test Login Endpoint**
   ```bash
   curl -X POST "http://localhost:8000/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Test Token Validation**
   ```bash
   # Use token from login response
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/auth/verify
   ```

**Expected Results:**
- Login returns JWT token
- Token validation works
- Invalid credentials rejected

### 6.3 API Endpoints
**Test Files:** `src/web_ui/api/athletes.py`, `src/web_ui/api/events.py`, `src/web_ui/api/leaderboards.py`

**Debug Steps:**
1. **Test Athlete Endpoints**
   ```bash
   # Get athletes
   curl http://localhost:8000/api/athletes
   
   # Search athletes
   curl "http://localhost:8000/api/athletes/search?name=test"
   ```

2. **Test Event Endpoints**
   ```bash
   # Get events
   curl http://localhost:8000/api/events
   
   # Get specific event
   curl http://localhost:8000/api/events/E12692
   ```

3. **Test Leaderboard Endpoints**
   ```bash
   # Get leaderboard
   curl http://localhost:8000/api/leaderboards
   
   # Get top athletes
   curl http://localhost:8000/api/leaderboards/top
   ```

**Expected Results:**
- All endpoints return valid JSON
- Proper HTTP status codes
- Error handling works

### 6.4 Frontend Templates
**Test Files:** `src/web_ui/templates/`

**Debug Steps:**
1. **Test Template Rendering**
   - Visit `http://localhost:8000/` in browser
   - Check all pages load correctly
   - Verify navigation works

2. **Test Static Files**
   - Check CSS loads: `http://localhost:8000/static/css/style.css`
   - Check JS loads: `http://localhost:8000/static/js/main.js`

3. **Test Responsive Design**
   - Test on different screen sizes
   - Verify mobile compatibility

**Expected Results:**
- All pages render correctly
- Static files load
- Responsive design works
- No JavaScript errors

---

## 7. Integration Testing

### 7.1 System Integrator
**Test File:** `src/integration/system_integrator.py`

**Debug Steps:**
1. **Test Component Initialization**
   ```python
   from src.integration.system_integrator import SystemIntegrator
   
   integrator = SystemIntegrator()
   print("All components initialized successfully")
   ```

2. **Test End-to-End Workflow**
   ```python
   # Test complete event processing
   event_id = "E12692"
   result = integrator.process_event(event_id)
   print(f"Event processing result: {result}")
   ```

**Expected Results:**
- All components initialize
- End-to-end workflow completes
- No integration errors

### 7.2 Performance Monitor
**Test File:** `src/integration/performance_monitor.py`

**Debug Steps:**
1. **Test Performance Monitoring**
   ```python
   from src.integration.performance_monitor import PerformanceMonitor
   
   monitor = PerformanceMonitor()
   
   # Start monitoring
   monitor.start_monitoring()
   
   # Perform some operations
   # ...
   
   # Get performance stats
   stats = monitor.get_performance_stats()
   print(f"Performance stats: {stats}")
   ```

**Expected Results:**
- Performance data collected
- Memory and CPU usage tracked
- No monitoring errors

---

## 8. Performance Testing

### 8.1 Load Testing
**Tools:** Use `locust` or `ab` for load testing

**Debug Steps:**
1. **Install Load Testing Tool**
   ```bash
   pip install locust
   ```

2. **Create Load Test Script**
   ```python
   # locustfile.py
   from locust import HttpUser, task, between
   
   class ADCCUser(HttpUser):
       wait_time = between(1, 3)
       
       @task
       def test_health(self):
           self.client.get("/health")
       
       @task
       def test_leaderboard(self):
           self.client.get("/api/leaderboards")
       
       @task
       def test_athletes(self):
           self.client.get("/api/athletes")
   ```

3. **Run Load Test**
   ```bash
   locust -f locustfile.py --host=http://localhost:8000
   ```

**Expected Results:**
- Response times under 30 seconds
- No errors under normal load
- System remains responsive

### 8.2 Memory Testing
**Debug Steps:**
1. **Test Large Dataset Processing**
   ```python
   # Create large test dataset
   import pandas as pd
   import numpy as np
   
   # Generate 10,000 athletes
   athletes_data = []
   for i in range(10000):
       athletes_data.append({
           'id': f'A{i}',
           'name': f'Athlete {i}',
           'rating': np.random.normal(1500, 200),
           'rd': np.random.uniform(200, 400)
       })
   
   df = pd.DataFrame(athletes_data)
   
   # Test processing
   from src.analytics.glicko_engine import GlickoEngine
   engine = GlickoEngine()
   
   # Process large dataset
   # Monitor memory usage
   ```

**Expected Results:**
- Memory usage stays reasonable
- No memory leaks
- Processing completes successfully

---

## 9. Railway Deployment Setup

### 9.1 Railway Account Setup
**Manual Steps:**
1. **Create Railway Account**
   - Go to https://railway.app/
   - Sign up with GitHub account
   - Verify email address

2. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

3. **Login to Railway**
   ```bash
   railway login
   ```

### 9.2 Project Configuration
**Files to Create:**

1. **railway.json**
   ```json
   {
     "build": {
       "builder": "nixpacks"
     },
     "deploy": {
       "startCommand": "uvicorn src.web_ui.main:app --host 0.0.0.0 --port $PORT",
       "healthcheckPath": "/health",
       "healthcheckTimeout": 300,
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

2. **Procfile** (alternative to railway.json)
   ```
   web: uvicorn src.web_ui.main:app --host 0.0.0.0 --port $PORT
   ```

3. **runtime.txt**
   ```
   python-3.9.18
   ```

### 9.3 Environment Variables Setup
**Railway Commands:**
```bash
# Set required environment variables
railway variables set SMOOTHCOMP_USERNAME=your_username
railway variables set SMOOTHCOMP_PASSWORD=your_password
railway variables set ADMIN_PASSWORD=secure_hash
railway variables set DEVELOPER_PASSWORD=secure_hash
railway variables set LOG_LEVEL=INFO
railway variables set WEBHOOK_SECRET=your_secret_key
railway variables set JWT_SECRET_KEY=your_jwt_secret
```

**Generate Secure Passwords:**
```bash
# Generate secure password hashes
python -c "import bcrypt; print(bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode())"
python -c "import bcrypt; print(bcrypt.hashpw('dev123'.encode(), bcrypt.gensalt()).decode())"
```

### 9.4 Deployment Process
**Commands:**
```bash
# Link to Railway project
railway link

# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs

# Open deployed application
railway open
```

### 9.5 Post-Deployment Testing
**Debug Steps:**
1. **Test Health Check**
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **Test API Endpoints**
   ```bash
   # Test public endpoints
   curl https://your-app.railway.app/api/leaderboards
   curl https://your-app.railway.app/api/athletes
   ```

3. **Test Web UI**
   - Open https://your-app.railway.app/ in browser
   - Test all pages and functionality
   - Verify responsive design

4. **Test Authentication**
   ```bash
   # Test login
   curl -X POST "https://your-app.railway.app/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "admin123"}'
   ```

**Expected Results:**
- Application deploys successfully
- All endpoints accessible
- Web UI functional
- Authentication works
- No environment-specific errors

---

## 10. Production Readiness

### 10.1 Security Audit
**Checklist:**
- [ ] Environment variables not in code
- [ ] Passwords properly hashed
- [ ] JWT tokens secure
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection

### 10.2 Error Handling
**Test Error Scenarios:**
1. **Invalid API requests**
2. **Missing authentication**
3. **Invalid data formats**
4. **Network timeouts**
5. **Database connection issues**

### 10.3 Monitoring Setup
**Implement:**
1. **Application logging**
2. **Error tracking**
3. **Performance monitoring**
4. **Uptime monitoring**

### 10.4 Backup Strategy
**Setup:**
1. **Database backups**
2. **File system backups**
3. **Configuration backups**
4. **Recovery procedures**

---

## Debugging Checklist

### Core System
- [ ] Configuration loads correctly
- [ ] Logging works properly
- [ ] File operations successful
- [ ] Error handling robust

### Data Acquisition
- [ ] Smoothcomp client functional
- [ ] Browser automation works
- [ ] File monitoring detects changes
- [ ] Data validation passes

### Data Processing
- [ ] Data transformation successful
- [ ] Validation rules enforced
- [ ] Error recovery works
- [ ] Performance acceptable

### Analytics Engine
- [ ] Glicko calculations accurate
- [ ] Record tracking correct
- [ ] Medal assignment proper
- [ ] Performance optimized

### Web UI
- [ ] FastAPI application starts
- [ ] All endpoints functional
- [ ] Authentication works
- [ ] Frontend responsive
- [ ] Static files load

### Integration
- [ ] Components work together
- [ ] End-to-end workflows complete
- [ ] Performance monitoring active
- [ ] Error handling comprehensive

### Railway Deployment
- [ ] Application deploys successfully
- [ ] Environment variables set
- [ ] Health checks pass
- [ ] All functionality works
- [ ] Performance acceptable

### Production Readiness
- [ ] Security audit passed
- [ ] Error handling tested
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Documentation complete

---

## Troubleshooting Guide

### Common Issues

1. **Import Errors**
   - Check Python path
   - Verify virtual environment
   - Check file permissions

2. **Database Connection Issues**
   - Verify connection strings
   - Check network connectivity
   - Test credentials

3. **File Permission Errors**
   - Check directory permissions
   - Verify file ownership
   - Test write access

4. **Memory Issues**
   - Monitor memory usage
   - Optimize data processing
   - Implement pagination

5. **Performance Issues**
   - Profile code execution
   - Optimize database queries
   - Implement caching

### Emergency Procedures

1. **Application Won't Start**
   - Check logs for errors
   - Verify environment variables
   - Test configuration loading

2. **Data Processing Fails**
   - Check input file formats
   - Verify data validation
   - Test error recovery

3. **Web UI Not Responding**
   - Check FastAPI logs
   - Verify port availability
   - Test health endpoint

4. **Railway Deployment Fails**
   - Check build logs
   - Verify environment variables
   - Test local deployment

---

## Success Criteria

### Phase 10 Completion
- [ ] All system components debugged
- [ ] Integration testing successful
- [ ] Performance requirements met
- [ ] Railway deployment functional
- [ ] Production readiness achieved
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Backup strategy implemented

### Final System Status
- [ ] Complete pipeline operational
- [ ] Web UI fully functional
- [ ] Error handling robust
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Ready for production use
- [ ] Monitoring active
- [ ] Backup procedures tested

---

## Next Steps After Phase 10

1. **User Acceptance Testing**
   - Test with real users
   - Gather feedback
   - Implement improvements

2. **Performance Optimization**
   - Monitor real usage
   - Optimize bottlenecks
   - Scale as needed

3. **Feature Enhancements**
   - Add new features
   - Improve user experience
   - Expand functionality

4. **Maintenance Planning**
   - Regular updates
   - Security patches
   - Performance monitoring

---

## Notes

- **Test incrementally** - Don't wait until the end to test
- **Document everything** - Keep detailed notes of issues and solutions
- **Use version control** - Commit changes frequently
- **Monitor performance** - Track system metrics continuously
- **Plan for scale** - Design for future growth
- **Security first** - Always prioritize security
- **Backup regularly** - Protect against data loss
- **Test thoroughly** - Verify all functionality works 