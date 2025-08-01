# ADCC Analysis Engine v0.6.0-alpha.6 - Development Roadmap

## Overview
This roadmap outlines the recommended development order to build the ADCC analysis engine with minimal debugging complexity. Each phase builds upon the previous one, allowing for thorough testing at each step.

## Phase 1: Foundation & Core Infrastructure (Week 1)

### 1.1 Project Setup
**Manual Actions Required:**
- Create project directory structure
- Set up virtual environment
- Install core dependencies (FastAPI, pandas, selenium, etc.)
- Create initial `.env` file with placeholder values

**Files to Create:**
```
├── requirements.txt
├── .env (with placeholders)
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── models.py
│   │   └── exceptions.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── file_handler.py
```

**Testing Focus:**
- Verify imports work
- Test basic logging functionality
- Ensure file operations work correctly

### 1.2 Basic Configuration System
**Files to Create:**
```
├── config/
│   ├── __init__.py
│   └── settings.py
├── logs/
│   └── .gitkeep
```

**Testing Focus:**
- Test configuration loading
- Verify environment variable handling
- Test logging configuration

### 1.3 Data Directory Structure
**Manual Actions Required:**
- Create all data directories
- Download 1-2 example files manually for testing

**Directories to Create:**
```
├── data/
│   ├── raw/
│   ├── processed/
│   └── datastore/
├── downloads/
└── logs/
```

**Testing Focus:**
- Verify directory permissions
- Test file read/write operations
- Ensure proper file organization

---

## Phase 2: Data Models & Validation (Week 1-2)

### 2.1 Core Data Models
**Files to Create:**
```
├── src/core/
│   ├── models.py (Pydantic models)
│   └── validators.py
```

**Models to Implement:**
- Athlete model
- Event model
- Match model
- Division model
- Club model

**Testing Focus:**
- Test model validation
- Verify data type handling
- Test edge cases (missing data, invalid formats)

### 2.2 Data Validation System
**Files to Create:**
```
├── src/utils/
│   └── validators.py
```

**Testing Focus:**
- Test name normalization
- Test date validation
- Test division string parsing
- Test athlete ID generation

---

## Phase 3: File Processing Pipeline (Week 2-3)

### 3.1 Raw File Processing
**Manual Actions Required:**
- Download 1-2 complete event datasets manually
- Place in `data/raw/` directory
- Document file formats and structures

**Files to Create:**
```
├── src/data_processing/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── id_generator.py
│   └── classifier.py
```

**Testing Focus:**
- Test CSV registration file parsing
- Test Excel match data parsing
- Test JSON registration API parsing
- Verify data cleaning and normalization

### 3.2 ID Generation System
**Files to Create:**
```
├── src/data_processing/
│   └── id_generator.py
```

**Testing Focus:**
- Test athlete ID generation
- Test event ID generation
- Test division ID generation
- Test match ID generation
- Verify ID uniqueness and consistency

### 3.3 Division Classification
**Files to Create:**
```
├── src/data_processing/
│   └── classifier.py
```

**Testing Focus:**
- Test age class separation (youth/adult/masters)
- Test division string parsing
- Test gi/no-gi classification
- Verify division mapping accuracy

---

## Phase 4: Data Storage & State Management (Week 3-4)

### 4.1 Parquet File Processing
**Files to Create:**
```
├── src/utils/
│   └── file_handler.py
```

**Testing Focus:**
- Test Parquet file creation
- Test data reading/writing
- Verify data integrity
- Test file compression

### 4.2 JSON Dictionary Creation
**Files to Create:**
```
├── src/analytics/
│   ├── __init__.py
│   ├── athlete_profiles.py
│   ├── division_mapper.py
│   └── club_tracker.py
```

**Testing Focus:**
- Test athlete profile creation
- Test division mapping
- Test club tracking
- Verify JSON structure and data integrity

### 4.3 State Management System
**Files to Create:**
```
├── src/state_management/
│   ├── __init__.py
│   ├── save_states.py
│   └── rollback.py
```

**Testing Focus:**
- Test state snapshots
- Test rollback functionality
- Verify chronological processing
- Test out-of-order event handling

---

## Phase 5: Analytics Engine (Week 4-5)

### 5.1 Glicko-2 Implementation
**Files to Create:**
```
├── src/analytics/
│   ├── glicko_engine.py
│   └── record_calculator.py
```

**Manual Actions Required:**
- Research and implement Glicko-2 algorithm
- Test with small datasets first

**Testing Focus:**
- Test Glicko calculations
- Test rating updates
- Test period finalization
- Verify mathematical accuracy

### 5.2 Record Tracking
**Files to Create:**
```
├── src/analytics/
│   └── record_calculator.py
```

**Testing Focus:**
- Test win/loss record calculation
- Test match history tracking
- Verify record accuracy

### 5.3 Medal Tracking
**Files to Create:**
```
├── src/analytics/
│   ├── medal_tracker.py
│   └── report_generator.py
```

**Testing Focus:**
- Test medal counting
- Test report generation
- Verify Excel output format

---

## Phase 6: File Acquisition System (Week 5-6)

### 6.1 Smoothcomp API Client
**Files to Create:**
```
├── src/data_acquisition/
│   ├── __init__.py
│   ├── smoothcomp_client.py
│   └── browser_automation.py
```

**Manual Actions Required:**
- Set up Smoothcomp API credentials
- Test API endpoints manually
- Document API response formats

**Testing Focus:**
- Test API authentication
- Test registration data download
- Test match data download
- Verify data format consistency

### 6.2 Browser Automation
**Files to Create:**
```
├── src/data_acquisition/
│   ├── browser_automation.py
│   └── file_monitor.py
```

**Manual Actions Required:**
- Set up Chrome WebDriver
- Test manual download process
- Document user interaction steps

**Testing Focus:**
- Test browser automation
- Test file monitoring
- Test download detection
- Verify file movement and renaming

### 6.3 Template System
**Files to Create:**
```
├── src/data_acquisition/
│   └── template_processor.py
```

**Testing Focus:**
- Test template creation
- Test data entry validation
- Test auto-suggestion system

---

## Phase 7: Web UI Foundation (Week 6-7)

### 7.1 FastAPI Application
**Files to Create:**
```
├── src/web_ui/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── athletes.py
│   │   └── events.py
│   └── models/
│       ├── __init__.py
│       ├── schemas.py
│       └── responses.py
```

**Testing Focus:**
- Test FastAPI startup
- Test basic endpoints
- Test authentication system
- Verify API documentation generation

### 7.2 Basic Frontend
**Files to Create:**
```
├── src/web_ui/
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
```

**Testing Focus:**
- Test basic page rendering
- Test CSS styling
- Test JavaScript functionality
- Verify responsive design

---

## Phase 8: Advanced Web UI Features (Week 7-8)

### 8.1 Leaderboard System
**Files to Create:**
```
├── src/web_ui/
│   ├── api/
│   │   └── leaderboards.py
│   ├── templates/
│   │   └── leaderboard.html
│   └── static/
│       └── js/
│           └── leaderboard.js
```

**Testing Focus:**
- Test leaderboard generation
- Test filtering and sorting
- Test pagination
- Verify data accuracy

### 8.2 Athlete Profiles
**Files to Create:**
```
├── src/web_ui/
│   ├── templates/
│   │   └── athlete_profile.html
│   └── static/
│       └── js/
│           └── athlete_profile.js
```

**Testing Focus:**
- Test profile data display
- Test trend graphs
- Test match history
- Verify data completeness

### 8.3 Admin Interface
**Files to Create:**
```
├── src/web_ui/
│   ├── api/
│   │   ├── admin.py
│   │   └── developer.py
│   ├── templates/
│   │   └── admin.html
│   └── static/
│       └── js/
│           └── admin.js
```

**Testing Focus:**
- Test admin authentication
- Test file upload/download
- Test system commands
- Verify permission system

---

## Phase 9: Advanced Features (Week 8-9)

### 9.1 Webhook System
**Files to Create:**
```
├── src/webhooks/
│   ├── __init__.py
│   ├── webhook_manager.py
│   ├── event_dispatcher.py
│   ├── delivery_queue.py
│   └── security.py
```

**Testing Focus:**
- Test webhook registration
- Test event dispatching
- Test delivery retry logic
- Verify security measures

### 9.2 Audit System
**Files to Create:**
```
├── src/utils/
│   └── audit_logger.py
```

**Testing Focus:**
- Test audit logging
- Test data modification tracking
- Test access logging
- Verify log integrity

### 9.3 Performance Optimization
**Files to Create:**
```
├── src/utils/
│   └── cache_manager.py
```

**Testing Focus:**
- Test caching system
- Test performance improvements
- Test memory usage
- Verify data consistency

---

## Phase 10: Integration & Testing (Week 9-10)

### 10.1 End-to-End Testing
**Manual Actions Required:**
- Download complete dataset for testing
- Test full pipeline from download to web UI
- Document any issues found

**Testing Focus:**
- Test complete workflow
- Test error handling
- Test performance under load
- Verify data accuracy throughout pipeline

### 10.2 Testing Strategy

#### 10.2.1 Test Coverage Requirements
- **Minimum 80% code coverage** for all code
- **100% coverage** for critical functions (Glicko calculations, data validation, ID generation)
- **Test all error conditions** and edge cases
- **Include integration tests** for complete workflows
- **Exclude 20%** from coverage: configuration loading, logging setup, performance optimization code

#### 10.2.2 Coverage Strategy Breakdown
```python
# Unit Tests (60% of coverage)
def test_generate_athlete_id_new_athlete():
    """Test ID generation for new athlete."""
    smoothcomp_id = 123456
    result = generate_athlete_id(smoothcomp_id)
    assert result == "A123456"

def test_glicko_calculation_submission_win():
    """Test Glicko calculation with submission win."""
    current_rating = 1500
    current_rd = 350
    match_result = MatchResult(winner=True, win_type="SUBMISSION")
    
    new_rating, new_rd = calculate_glicko_rating(current_rating, current_rd, [match_result])
    
    assert new_rating > current_rating  # Should increase for win
    assert new_rd < current_rd  # Should decrease RD

# Integration Tests (25% of coverage)
def test_complete_event_processing():
    """Test processing a complete event from raw data to final output."""
    event_id = "E12692"
    raw_files = ["registrations.csv", "matches.xlsx", "registrations.json"]
    
    result = process_event(event_id, raw_files)
    
    assert result["status"] == "completed"
    assert os.path.exists(f"data/processed/{event_id}_matches.parquet")
    assert os.path.exists("data/datastore/athlete_profiles.json")

# Error Condition Tests (15% of coverage)
def test_invalid_file_format():
    """Test handling of invalid file formats."""
    with pytest.raises(ValueError, match="Invalid file format"):
        process_registration_file("invalid_file.txt")

def test_concurrent_processing_conflict():
    """Test conflict handling for simultaneous processing."""
    task1 = start_data_processing("E12692")
    
    with pytest.raises(ConcurrentOperationError):
        start_data_processing("E12692")
```

#### 10.2.3 Coverage Tools and Commands
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Generate coverage report
coverage html

# Check coverage in CI/CD
pytest --cov=src --cov-fail-under=80
```

#### 10.2.4 Test Data Management
```python
# Use factories for test data
class AthleteFactory:
    @staticmethod
    def create_athlete(**kwargs) -> Athlete:
        defaults = {
            'id': 'A123456',
            'name': 'Test Athlete',
            'age_class': 'adult',
            'skill_level': 'advanced'
        }
        defaults.update(kwargs)
        return Athlete(**defaults)
```

#### 10.2.5 Performance Testing
- Load test critical endpoints
- Monitor response times under load (target: <30 seconds for API calls)
- Test with realistic data volumes
- Benchmark file I/O operations
- Test concurrent user scenarios
- Verify conflict handling for simultaneous operations
- Test data processing operations (can take several minutes)
- Ensure system remains responsive during long-running tasks

### 10.3 Documentation
**Files to Create:**
```
├── README.md
├── API_DOCUMENTATION.md
├── DEPLOYMENT_GUIDE.md
└── USER_MANUAL.md
```

### 10.3 Railway Deployment Workflow

#### 10.3.1 Railway Setup
**Manual Actions Required:**
- Set up Railway account
- Configure production environment
- Test deployment process

#### 10.3.2 Railway Configuration
```json
// railway.json
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

#### 10.3.3 Railway Environment Variables
```bash
# Required Railway environment variables
railway variables set SMOOTHCOMP_USERNAME=your_username
railway variables set SMOOTHCOMP_PASSWORD=your_password
railway variables set ADMIN_PASSWORD=secure_hash
railway variables set DEVELOPER_PASSWORD=secure_hash
railway variables set LOG_LEVEL=INFO
railway variables set WEBHOOK_SECRET=your_secret_key
```

#### 10.3.4 Railway Deployment Commands
```bash
# Connect to Railway
railway login
railway link

# Deploy to Railway
railway up

# Check deployment status
railway status

# View logs
railway logs

# Rollback if needed
railway rollback
```

#### 10.3.5 Development → Staging → Production Workflow
```bash
# Development
git checkout develop
railway up --service dev

# Staging
git checkout main
railway up --service staging

# Production
git tag v0.6.0-alpha.7
git push origin v0.6.0-alpha.7
railway up --service production
```

#### 10.3.6 Railway-Specific Considerations
- **File Persistence**: Use Railway volumes for persistent data storage
- **Resource Limits**: Memory limits (512MB-8GB), CPU constraints
- **Scaling Strategy**: Start with hobby plan, upgrade to pro for production
- **Backup Strategy**: Implement backup for critical data
- **Ephemeral File System**: Handle Railway's file system limitations

---

## Debugging Strategy

### For Each Phase:
1. **Start Small**: Test with minimal datasets first
2. **Log Everything**: Use extensive logging to track data flow
3. **Validate Outputs**: Check data at each processing step
4. **Test Edge Cases**: Handle missing data, invalid formats, etc.
5. **Document Issues**: Keep detailed notes of problems and solutions

### Manual Testing Checklist:
- [ ] Verify file downloads work correctly
- [ ] Check data parsing accuracy
- [ ] Validate ID generation uniqueness
- [ ] Test Glicko calculations with known values
- [ ] Verify web UI functionality
- [ ] Test error handling and recovery

### Common Debugging Points:
1. **File I/O**: Check file permissions and paths
2. **Data Types**: Verify pandas DataFrame operations
3. **API Responses**: Validate Smoothcomp API data
4. **Web UI**: Test browser compatibility
5. **Performance**: Monitor memory usage and processing times

---

## Success Criteria

### Phase Completion:
- [ ] All tests pass
- [ ] No critical errors in logs
- [ ] Data integrity verified
- [ ] Performance meets requirements
- [ ] Documentation updated

### Final System:
- [ ] Complete pipeline functional
- [ ] Web UI responsive and user-friendly
- [ ] Error handling robust
- [ ] Performance optimized
- [ ] Ready for production deployment

---

## Code Quality Tools

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.9
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Type Checking Configuration
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### IDE Configuration
- Enable type checking
- Configure linting rules
- Set up debugging configurations
- Use consistent formatting settings
- Enable auto-formatting on save

---

## Notes

- **Always test with real data** when possible
- **Keep backups** of working versions
- **Document everything** - especially manual steps
- **Use version control** for all code changes
- **Test incrementally** - don't wait until the end to test
- **Plan for rollbacks** - have recovery procedures ready 