# Playwright End-to-End Testing for SuperSuite

## Overview

This automated testing script uses Playwright to perform comprehensive end-to-end testing of the SuperSuite Streamlit application while automatically capturing screenshots for documentation purposes.

---

## Features

✅ **Fully Automated Testing** - Complete 7-step user journey automation  
✅ **Screenshot Capture** - Automatic screenshot capture at each step  
✅ **Comprehensive Reporting** - JSON test report with detailed metrics  
✅ **Error Handling** - Robust error handling with error screenshots  
✅ **Streamlit-Aware** - Handles Streamlit's dynamic rendering  
✅ **Configurable** - Headless mode, slow motion, custom timeouts  

---

## Prerequisites

### 1. Playwright Installation

Ensure Playwright is installed with browser drivers:

```bash
# Install Playwright
pip install playwright

# Install browser drivers (Chromium, Firefox, WebKit)
playwright install
```

### 2. Application Running

The SuperSuite Streamlit application must be running:

```bash
# Start the application
streamlit run app/streamlit_app.py --server.port=8504
```

**Application URL:** http://localhost:8504

### 3. Test Document

Ensure the test document exists:

```bash
# Verify test document
ls -lh app/notebooks/test_data/resume-harshit.pdf
```

---

## Usage

### Basic Usage (Headed Mode)

Run with visible browser window (recommended for first run):

```bash
python playwright_e2e_test.py
```

### Headless Mode

Run without browser GUI (faster, for CI/CD):

```bash
python playwright_e2e_test.py --headless
```

### Slow Motion Mode

Slow down operations for debugging (milliseconds):

```bash
python playwright_e2e_test.py --slow-mo 500
```

### Combined Options

```bash
python playwright_e2e_test.py --headless --slow-mo 100
```

---

## Test Workflow

The script automates the following 7-step workflow:

### Step 1: Application Startup
- Navigate to http://localhost:8504
- Verify Streamlit loads correctly
- Verify sidebar is visible
- **Screenshot:** `01-landing-page.png`

### Step 2: Project Creation
- Capture empty project form
- Fill project name: "Resume Analysis - Harshit"
- Fill description: "End-to-end test with resume document"
- Click Create button
- Verify project creation success
- **Screenshots:**
  - `02-create-project-form.png`
  - `03-create-project-filled.png`
  - `04-create-project-success.png`

### Step 3: Document Upload
- Navigate to upload interface
- Upload `app/notebooks/test_data/resume-harshit.pdf`
- Verify file upload confirmation
- **Screenshots:**
  - `05-upload-interface.png`
  - `06-file-uploaded.png`

### Step 4: Document Processing
- Click "Process Document" button
- Wait for processing to complete (up to 10 minutes)
- Monitor progress indicators
- Verify completion
- **Screenshots:**
  - `07-processing-started.png`
  - `08-processing-complete.png`

### Step 5: Ontology Viewing
- Navigate to Ontology/Schema tab
- View generated entity types
- View relationships
- **Screenshots:**
  - `09-ontology-view.png`
  - `10-ontology-entities.png` (if available)
  - `11-ontology-relationships.png` (if available)

### Step 6: Knowledge Extraction
- Navigate to Knowledge Base/Entities tab
- View extracted entities
- Click on entity for details
- View entity table
- **Screenshots:**
  - `12-knowledge-base.png`
  - `13-entity-details.png`
  - `14-entity-table.png` (if available)

### Step 7: Chat/Query Interface
- Navigate to Chat/Query tab
- Ask 3 questions:
  1. "What is Harshit's educational background?"
  2. "What companies has Harshit worked for?"
  3. "What are Harshit's key skills?"
- Wait for responses
- **Screenshots:**
  - `15-chat-interface.png`
  - `16-chat-question-1.png`
  - `17-chat-question-2.png`
  - `18-chat-question-3.png`

---

## Output

### Screenshots

All screenshots are saved to:
```
docs/assets/screenshots/
```

**Naming Convention:**
```
[number]-[feature]-[description].png

Examples:
01-landing-page.png
02-create-project-form.png
16-chat-question-1.png
```

**Error Screenshots:**
```
error-[step-name]-[timestamp].png

Example:
error-step4-20251016_143022.png
```

### Test Report

A comprehensive JSON report is generated:
```
e2e_test_report.json
```

**Report Contents:**
- Test execution metadata (start time, end time, duration)
- Summary (total steps, passed, failed, success rate)
- Detailed step results (status, duration, notes)
- Screenshot inventory (filenames, descriptions, timestamps)
- Error log (if any)

**Example Report:**
```json
{
  "test_execution": {
    "start_time": "2025-10-16T14:30:00.123456",
    "end_time": "2025-10-16T14:45:30.654321",
    "total_duration_seconds": 930.53
  },
  "summary": {
    "total_steps": 7,
    "passed": 7,
    "failed": 0,
    "success_rate": "100.0%"
  },
  "steps": [
    {
      "step": "Step 1: Application Startup",
      "status": "PASS",
      "duration_seconds": 5.23,
      "notes": "Application loaded successfully",
      "timestamp": "2025-10-16T14:30:05.123456"
    }
  ],
  "screenshots": {
    "total_captured": 18,
    "files": [
      {
        "filename": "01-landing-page.png",
        "description": "Application landing page",
        "timestamp": "2025-10-16T14:30:05.123456"
      }
    ]
  },
  "errors": []
}
```

---

## Configuration

### Timeouts

Edit these constants in `playwright_e2e_test.py`:

```python
DEFAULT_TIMEOUT = 30000  # 30 seconds
UPLOAD_TIMEOUT = 60000  # 1 minute
PROCESSING_TIMEOUT = 600000  # 10 minutes
CHAT_RESPONSE_TIMEOUT = 120000  # 2 minutes
```

### Application URL

```python
APP_URL = "http://localhost:8504"
```

### Test Document

```python
TEST_DOCUMENT_PATH = "app/notebooks/test_data/resume-harshit.pdf"
```

### Chat Questions

```python
CHAT_QUESTIONS = [
    "What is Harshit's educational background?",
    "What companies has Harshit worked for?",
    "What are Harshit's key skills?"
]
```

---

## Troubleshooting

### Issue: Browser doesn't launch

**Error:** `Executable doesn't exist`

**Solution:**
```bash
# Install browser drivers
playwright install chromium
```

### Issue: Application not found

**Error:** `net::ERR_CONNECTION_REFUSED`

**Solution:**
```bash
# Ensure Streamlit is running
streamlit run app/streamlit_app.py --server.port=8504
```

### Issue: Test document not found

**Error:** `Test document not found: app/notebooks/test_data/resume-harshit.pdf`

**Solution:**
```bash
# Verify file exists
ls -lh app/notebooks/test_data/resume-harshit.pdf

# If missing, use a different PDF
# Edit TEST_DOCUMENT_PATH in the script
```

### Issue: Elements not found

**Error:** `Timeout 30000ms exceeded`

**Solution:**
1. Run in headed mode to see what's happening:
   ```bash
   python playwright_e2e_test.py
   ```

2. Increase timeout:
   ```python
   DEFAULT_TIMEOUT = 60000  # 60 seconds
   ```

3. Use slow motion to debug:
   ```bash
   python playwright_e2e_test.py --slow-mo 1000
   ```

### Issue: Processing timeout

**Symptom:** Step 4 times out after 10 minutes

**Solution:**
1. Increase processing timeout:
   ```python
   PROCESSING_TIMEOUT = 1200000  # 20 minutes
   ```

2. Check application logs for errors

3. Verify database connections (Snowflake, Neo4j)

### Issue: Screenshots are blank

**Symptom:** Screenshots captured but show blank pages

**Solution:**
1. Add longer wait times before screenshots:
   ```python
   time.sleep(5)  # Wait for rendering
   ```

2. Use `full_page=False` for viewport-only screenshots

3. Check browser console for JavaScript errors

---

## Advanced Usage

### Custom Browser

Use Firefox or WebKit instead of Chromium:

```python
# In run_e2e_test function, change:
browser = p.firefox.launch(headless=headless, slow_mo=slow_mo)
# or
browser = p.webkit.launch(headless=headless, slow_mo=slow_mo)
```

### Custom Viewport

Change browser window size:

```python
context = browser.new_context(viewport={"width": 2560, "height": 1440})
```

### Video Recording

Record test execution:

```python
context = browser.new_context(
    viewport={"width": 1920, "height": 1080},
    record_video_dir="test_videos/"
)
```

### Network Logging

Log network requests:

```python
page.on("request", lambda request: print(f">> {request.method} {request.url}"))
page.on("response", lambda response: print(f"<< {response.status} {response.url}"))
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: E2E Testing

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Start Streamlit
        run: |
          streamlit run app/streamlit_app.py --server.port=8504 &
          sleep 10
      
      - name: Run E2E tests
        run: python playwright_e2e_test.py --headless
      
      - name: Upload screenshots
        uses: actions/upload-artifact@v2
        with:
          name: screenshots
          path: docs/assets/screenshots/
      
      - name: Upload test report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: e2e_test_report.json
```

---

## Best Practices

### 1. Run in Headed Mode First
Always run with visible browser first to see what's happening:
```bash
python playwright_e2e_test.py
```

### 2. Use Slow Motion for Debugging
When troubleshooting, slow down operations:
```bash
python playwright_e2e_test.py --slow-mo 500
```

### 3. Check Application Logs
Monitor Streamlit console output during test execution

### 4. Verify Screenshots
After test completion, review all screenshots for quality

### 5. Clean Up Old Screenshots
Remove old screenshots before running new tests:
```bash
rm -rf docs/assets/screenshots/*.png
```

---

## Success Criteria

The test is successful if:

✅ All 7 steps complete with PASS status  
✅ At least 18 screenshots captured  
✅ No error screenshots generated  
✅ Processing completes within timeout  
✅ Chat responses received  
✅ Test report shows 100% success rate  

---

## Next Steps

After successful test execution:

1. **Review Screenshots:**
   ```bash
   open docs/assets/screenshots/
   ```

2. **Review Test Report:**
   ```bash
   cat e2e_test_report.json | python -m json.tool
   ```

3. **Update Documentation:**
   - Embed screenshots in user guide files
   - Update descriptions based on actual UI
   - Verify all links work

4. **Commit Results:**
   ```bash
   git add docs/assets/screenshots/
   git add e2e_test_report.json
   git commit -m "Add E2E test screenshots and report"
   ```

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review Playwright documentation: https://playwright.dev/python/
- Check Streamlit testing guide: https://docs.streamlit.io/library/advanced-features/testing

---

**Ready to run? Execute the script and watch the magic happen!** 🚀

```bash
python playwright_e2e_test.py
```

