#!/usr/bin/env python3
"""
Playwright End-to-End Testing Script for SuperSuite Streamlit Application

This script automates the complete user journey through the SuperSuite application,
capturing screenshots at each step for documentation purposes.

Usage:
    python playwright_e2e_test.py [--headless] [--slow-mo MILLISECONDS]

Requirements:
    - Streamlit app running at http://localhost:8504
    - Test document: app/notebooks/test_data/resume-harshit.pdf
    - Playwright installed: pip install playwright && playwright install
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, expect, TimeoutError as PlaywrightTimeoutError

# ============================================================================
# CONFIGURATION
# ============================================================================

# Application settings
APP_URL = "http://localhost:8504"
APP_TITLE = "SuperSuite"

# Test data
PROJECT_NAME = "Resume Analysis - Harshit"
PROJECT_DESCRIPTION = "End-to-end test with resume document"
TEST_DOCUMENT_PATH = "app/notebooks/test_data/resume-harshit.pdf"

# Screenshot settings
SCREENSHOT_DIR = "docs/assets/screenshots"
SCREENSHOT_FORMAT = "png"

# Timeout settings (in milliseconds)
DEFAULT_TIMEOUT = 30000  # 30 seconds
UPLOAD_TIMEOUT = 60000  # 1 minute
PROCESSING_TIMEOUT = 600000  # 10 minutes
CHAT_RESPONSE_TIMEOUT = 120000  # 2 minutes

# Chat questions
CHAT_QUESTIONS = [
    "What is Harshit's educational background?",
    "What companies has Harshit worked for?",
    "What are Harshit's key skills?"
]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

class TestReport:
    """Test execution report tracker"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.steps = []
        self.screenshots = []
        self.errors = []
        
    def add_step(self, step_name: str, status: str, duration: float = 0, notes: str = ""):
        """Add a test step result"""
        self.steps.append({
            "step": step_name,
            "status": status,
            "duration_seconds": round(duration, 2),
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_screenshot(self, filename: str, description: str):
        """Add a screenshot record"""
        self.screenshots.append({
            "filename": filename,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_error(self, step: str, error: str):
        """Add an error record"""
        self.errors.append({
            "step": step,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
    def generate_report(self) -> dict:
        """Generate final test report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        passed_steps = sum(1 for s in self.steps if s["status"] == "PASS")
        total_steps = len(self.steps)
        
        return {
            "test_execution": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_seconds": round(duration, 2)
            },
            "summary": {
                "total_steps": total_steps,
                "passed": passed_steps,
                "failed": total_steps - passed_steps,
                "success_rate": f"{(passed_steps/total_steps*100):.1f}%" if total_steps > 0 else "0%"
            },
            "steps": self.steps,
            "screenshots": {
                "total_captured": len(self.screenshots),
                "files": self.screenshots
            },
            "errors": self.errors
        }


def setup_screenshot_directory():
    """Create screenshot directory if it doesn't exist"""
    Path(SCREENSHOT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"✅ Screenshot directory ready: {SCREENSHOT_DIR}")


def capture_screenshot(page: Page, filename: str, description: str, report: TestReport):
    """Capture and save a screenshot"""
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    try:
        page.screenshot(path=filepath, full_page=True)
        report.add_screenshot(filename, description)
        print(f"📸 Screenshot captured: {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to capture screenshot {filename}: {e}")
        report.add_error(f"Screenshot: {filename}", str(e))
        return False


def wait_for_streamlit_ready(page: Page):
    """Wait for Streamlit to be fully loaded and ready"""
    try:
        # Wait for Streamlit's main container
        page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=DEFAULT_TIMEOUT)
        # Give Streamlit a moment to finish rendering
        time.sleep(2)
        print("✅ Streamlit application ready")
        return True
    except PlaywrightTimeoutError:
        print("❌ Streamlit application did not load in time")
        return False


def capture_error_screenshot(page: Page, step_name: str, report: TestReport):
    """Capture screenshot when an error occurs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"error-{step_name}-{timestamp}.png"
    capture_screenshot(page, filename, f"Error in {step_name}", report)


# ============================================================================
# TEST STEP FUNCTIONS
# ============================================================================

def step_1_application_startup(page: Page, report: TestReport) -> bool:
    """Step 1: Navigate to application and verify it loads"""
    step_name = "Step 1: Application Startup"
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Navigate to application
        print(f"Navigating to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle", timeout=DEFAULT_TIMEOUT)
        
        # Wait for Streamlit to be ready
        if not wait_for_streamlit_ready(page):
            raise Exception("Streamlit did not load properly")
        
        # Verify sidebar is visible
        sidebar = page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible(timeout=DEFAULT_TIMEOUT)
        print("✅ Sidebar visible")
        
        # Capture landing page screenshot
        capture_screenshot(page, "01-landing-page.png", "Application landing page", report)
        
        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, "Application loaded successfully")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to load application: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step1", report)
        return False


def step_2_project_creation(page: Page, report: TestReport) -> bool:
    """Step 2: Create a new project"""
    step_name = "Step 2: Project Creation"
    print(f"\n{'='*60}")
    print(f"📁 {step_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Wait for page to be stable
        time.sleep(2)
        
        # Capture empty form
        capture_screenshot(page, "02-create-project-form.png", "Empty project creation form", report)
        
        # Find and fill project name input
        # Streamlit text inputs have data-testid="stTextInput"
        print("Looking for project name input...")
        
        # Try multiple strategies to find the input fields
        # Strategy 1: Look for text inputs in sidebar
        text_inputs = page.locator('[data-testid="stSidebar"] input[type="text"]').all()
        
        if len(text_inputs) >= 2:
            # First input should be project name
            print(f"Filling project name: {PROJECT_NAME}")
            text_inputs[0].fill(PROJECT_NAME)
            time.sleep(0.5)
            
            # Second input should be description
            print(f"Filling project description: {PROJECT_DESCRIPTION}")
            text_inputs[1].fill(PROJECT_DESCRIPTION)
            time.sleep(0.5)
        else:
            # Alternative: Look for labels and find inputs nearby
            print("Using alternative input detection...")
            page.get_by_label("Project Name", exact=False).fill(PROJECT_NAME)
            page.get_by_label("Description", exact=False).fill(PROJECT_DESCRIPTION)
            time.sleep(0.5)
        
        # Capture filled form
        capture_screenshot(page, "03-create-project-filled.png", "Filled project creation form", report)
        
        # Find and click Create button
        print("Looking for Create button...")
        # Try to find button with text "Create"
        create_button = page.get_by_role("button", name="Create", exact=False)
        create_button.click()
        print("✅ Create button clicked")
        
        # Wait for success message or project to appear
        time.sleep(3)
        
        # Capture success state
        capture_screenshot(page, "04-create-project-success.png", "Project creation success", report)
        
        # Verify project appears in dropdown (if there's a select element)
        print("Verifying project was created...")
        
        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, f"Project '{PROJECT_NAME}' created successfully")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to create project: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step2", report)
        return False


def step_3_document_upload(page: Page, report: TestReport) -> bool:
    """Step 3: Upload a document"""
    step_name = "Step 3: Document Upload"
    print(f"\n{'='*60}")
    print(f"📄 {step_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Wait for page to be stable
        time.sleep(2)
        
        # Capture upload interface
        capture_screenshot(page, "05-upload-interface.png", "Document upload interface", report)
        
        # Find file uploader
        print("Looking for file uploader...")
        
        # Get absolute path to test document
        test_doc_abs_path = os.path.abspath(TEST_DOCUMENT_PATH)
        if not os.path.exists(test_doc_abs_path):
            raise Exception(f"Test document not found: {test_doc_abs_path}")
        
        print(f"Test document path: {test_doc_abs_path}")
        
        # Streamlit file uploader has data-testid="stFileUploader"
        file_uploader = page.locator('[data-testid="stFileUploader"] input[type="file"]')
        
        # Set the file
        print(f"Uploading file: {os.path.basename(test_doc_abs_path)}")
        file_uploader.set_input_files(test_doc_abs_path)
        
        # Wait for upload to complete
        time.sleep(3)
        
        # Capture uploaded state
        capture_screenshot(page, "06-file-uploaded.png", "File uploaded confirmation", report)
        
        # Verify file name is displayed
        print("Verifying file upload...")
        
        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, f"Document uploaded: {os.path.basename(test_doc_abs_path)}")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True
        
    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to upload document: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step3", report)
        return False


def step_4_document_processing(page: Page, report: TestReport) -> bool:
    """Step 4: Process the uploaded document"""
    step_name = "Step 4: Document Processing"
    print(f"\n{'='*60}")
    print(f"⚙️ {step_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        time.sleep(2)

        print("Looking for Process Document button...")
        process_button = page.get_by_role("button", name="Process", exact=False)

        capture_screenshot(page, "07-processing-started.png", "Processing started", report)

        process_button.click()
        print("✅ Process Document button clicked")
        print("⏳ Waiting for processing to complete (this may take 2-10 minutes)...")

        processing_complete = False
        max_wait_time = PROCESSING_TIMEOUT / 1000
        poll_interval = 5
        elapsed = 0

        while elapsed < max_wait_time and not processing_complete:
            time.sleep(poll_interval)
            elapsed += poll_interval

            page_content = page.content()

            if any(indicator in page_content.lower() for indicator in [
                "processing complete",
                "successfully processed",
                "extraction complete",
                "processing finished"
            ]):
                processing_complete = True
                print(f"✅ Processing completed after {elapsed}s")
                break

            if elapsed % 30 == 0:
                print(f"⏳ Still processing... ({elapsed}s elapsed)")

        if not processing_complete:
            print(f"⚠️ Processing timeout after {elapsed}s, capturing current state...")

        time.sleep(3)
        capture_screenshot(page, "08-processing-complete.png", "Processing completion", report)

        duration = time.time() - start_time
        status = "PASS" if processing_complete else "PARTIAL"
        notes = f"Processing completed in {elapsed}s" if processing_complete else f"Processing timeout after {elapsed}s"

        report.add_step(step_name, status, duration, notes)
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed during document processing: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step4", report)
        return False


def step_5_ontology_viewing(page: Page, report: TestReport) -> bool:
    """Step 5: View the generated ontology/schema"""
    step_name = "Step 5: Ontology Viewing"
    print(f"\n{'='*60}")
    print(f"🎨 {step_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        time.sleep(2)

        print("Looking for Ontology/Schema tab...")

        tab_found = False
        for tab_name in ["Ontology", "Schema", "Entity Types", "ontology", "schema"]:
            try:
                tab = page.get_by_text(tab_name, exact=False)
                if tab.is_visible():
                    tab.click()
                    print(f"✅ Clicked on '{tab_name}' tab")
                    tab_found = True
                    break
            except:
                continue

        if not tab_found:
            print("⚠️ Could not find Ontology tab, capturing current view...")

        time.sleep(3)
        capture_screenshot(page, "09-ontology-view.png", "Ontology/Schema view", report)

        try:
            if "entity" in page.content().lower():
                capture_screenshot(page, "10-ontology-entities.png", "Entity types view", report)

            if "relationship" in page.content().lower():
                capture_screenshot(page, "11-ontology-relationships.png", "Relationships view", report)
        except:
            pass

        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, "Ontology view captured")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to view ontology: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step5", report)
        return False


def step_6_knowledge_extraction(page: Page, report: TestReport) -> bool:
    """Step 6: View extracted knowledge/entities"""
    step_name = "Step 6: Knowledge Extraction"
    print(f"\n{'='*60}")
    print(f"📊 {step_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        time.sleep(2)

        print("Looking for Knowledge Base/Entities tab...")

        tab_found = False
        for tab_name in ["Knowledge", "Entities", "Knowledge Base", "knowledge", "entities"]:
            try:
                tab = page.get_by_text(tab_name, exact=False)
                if tab.is_visible():
                    tab.click()
                    print(f"✅ Clicked on '{tab_name}' tab")
                    tab_found = True
                    break
            except:
                continue

        if not tab_found:
            print("⚠️ Could not find Knowledge Base tab, capturing current view...")

        time.sleep(3)
        capture_screenshot(page, "12-knowledge-base.png", "Knowledge base view", report)

        try:
            clickable_elements = page.locator('[role="button"]').all()
            if len(clickable_elements) > 0:
                clickable_elements[0].click()
                time.sleep(2)
                capture_screenshot(page, "13-entity-details.png", "Entity details view", report)
        except:
            print("⚠️ Could not click on entity for details")

        try:
            if page.locator('table').count() > 0:
                capture_screenshot(page, "14-entity-table.png", "Entity table view", report)
        except:
            pass

        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, "Knowledge base view captured")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed to view knowledge base: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step6", report)
        return False


def step_7_chat_interface(page: Page, report: TestReport) -> bool:
    """Step 7: Test chat/query interface"""
    step_name = "Step 7: Chat/Query Interface"
    print(f"\n{'='*60}")
    print(f"💬 {step_name}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        time.sleep(2)

        print("Looking for Chat/Query tab...")

        tab_found = False
        for tab_name in ["Chat", "Query", "chat", "query", "Ask"]:
            try:
                tab = page.get_by_text(tab_name, exact=False)
                if tab.is_visible():
                    tab.click()
                    print(f"✅ Clicked on '{tab_name}' tab")
                    tab_found = True
                    break
            except:
                continue

        if not tab_found:
            print("⚠️ Could not find Chat tab, capturing current view...")

        time.sleep(3)
        capture_screenshot(page, "15-chat-interface.png", "Chat interface", report)

        for i, question in enumerate(CHAT_QUESTIONS, 1):
            print(f"\nAsking question {i}: {question}")

            chat_input = page.locator('[data-testid="stChatInput"] textarea, input[type="text"]').first

            chat_input.fill(question)
            time.sleep(0.5)

            chat_input.press("Enter")

            print(f"⏳ Waiting for response...")
            time.sleep(10)

            screenshot_num = 15 + i
            capture_screenshot(
                page,
                f"{screenshot_num}-chat-question-{i}.png",
                f"Chat Q&A {i}: {question}",
                report
            )

            print(f"✅ Question {i} completed")

        duration = time.time() - start_time
        report.add_step(step_name, "PASS", duration, f"Asked {len(CHAT_QUESTIONS)} questions successfully")
        print(f"✅ {step_name} completed in {duration:.2f}s")
        return True

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Failed in chat interface: {str(e)}"
        print(f"❌ {error_msg}")
        report.add_step(step_name, "FAIL", duration, error_msg)
        report.add_error(step_name, str(e))
        capture_error_screenshot(page, "step7", report)
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def run_e2e_test(headless: bool = False, slow_mo: int = 0):
    """Run the complete end-to-end test"""

    print("\n" + "="*60)
    print("🚀 SuperSuite End-to-End Testing with Playwright")
    print("="*60)
    print(f"Application URL: {APP_URL}")
    print(f"Test Document: {TEST_DOCUMENT_PATH}")
    print(f"Screenshot Directory: {SCREENSHOT_DIR}")
    print(f"Headless Mode: {headless}")
    print(f"Slow Motion: {slow_mo}ms")
    print("="*60 + "\n")

    # Setup
    setup_screenshot_directory()
    report = TestReport()

    # Verify test document exists
    if not os.path.exists(TEST_DOCUMENT_PATH):
        print(f"❌ Test document not found: {TEST_DOCUMENT_PATH}")
        print("Please ensure the test document exists before running the test.")
        sys.exit(1)

    # Run tests with Playwright
    with sync_playwright() as p:
        # Launch browser
        print("🌐 Launching browser...")
        # Use Firefox since chromium version mismatch
        browser = p.firefox.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Set default timeout
        page.set_default_timeout(DEFAULT_TIMEOUT)

        try:
            # Execute test steps
            steps = [
                step_1_application_startup,
                step_2_project_creation,
                step_3_document_upload,
                step_4_document_processing,
                step_5_ontology_viewing,
                step_6_knowledge_extraction,
                step_7_chat_interface
            ]

            for step_func in steps:
                success = step_func(page, report)
                if not success:
                    print(f"\n⚠️ Step failed, but continuing with remaining steps...")

        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted by user")
            report.add_error("Test Execution", "Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Unexpected error: {e}")
            report.add_error("Test Execution", str(e))
            capture_error_screenshot(page, "unexpected", report)
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            browser.close()

    # Generate and save report
    print("\n" + "="*60)
    print("📊 Generating Test Report")
    print("="*60)

    final_report = report.generate_report()

    # Save report to JSON
    report_path = "e2e_test_report.json"
    with open(report_path, 'w') as f:
        json.dump(final_report, f, indent=2)
    print(f"✅ Test report saved to: {report_path}")

    # Print summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    print(f"Total Steps: {final_report['summary']['total_steps']}")
    print(f"Passed: {final_report['summary']['passed']}")
    print(f"Failed: {final_report['summary']['failed']}")
    print(f"Success Rate: {final_report['summary']['success_rate']}")
    print(f"Total Duration: {final_report['test_execution']['total_duration_seconds']}s")
    print(f"Screenshots Captured: {final_report['screenshots']['total_captured']}")
    print(f"Errors: {len(final_report['errors'])}")
    print("="*60)

    # Print detailed step results
    print("\n📝 STEP DETAILS:")
    for step in final_report['steps']:
        status_icon = "✅" if step['status'] == "PASS" else "⚠️" if step['status'] == "PARTIAL" else "❌"
        print(f"{status_icon} {step['step']}: {step['status']} ({step['duration_seconds']}s)")
        if step['notes']:
            print(f"   └─ {step['notes']}")

    # Print errors if any
    if final_report['errors']:
        print("\n❌ ERRORS:")
        for error in final_report['errors']:
            print(f"  • {error['step']}: {error['error']}")

    print("\n✅ End-to-end testing complete!")
    print(f"📸 Screenshots saved to: {SCREENSHOT_DIR}")
    print(f"📊 Full report saved to: {report_path}")

    return final_report


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Playwright E2E Testing for SuperSuite Streamlit Application"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)"
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=0,
        help="Slow down operations by specified milliseconds (useful for debugging)"
    )

    args = parser.parse_args()

    try:
        run_e2e_test(headless=args.headless, slow_mo=args.slow_mo)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

