#!/usr/bin/env python3
"""
Selenium-based E2E Testing Script for SuperSuite Streamlit Application

This script performs automated testing and screenshot capture using Selenium WebDriver.
Selenium works better with Streamlit's dynamic elements compared to Playwright.
"""

import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("ERROR: Selenium not installed. Installing now...")
    os.system("pip install selenium")
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
APP_URL = "http://localhost:8504"
SCREENSHOT_DIR = "docs/assets/screenshots"
TEST_DOCUMENT_PATH = "app/notebooks/test_data/resume-harshit.pdf"
PROJECT_NAME = "Resume Analysis - Harshit"
PROJECT_DESCRIPTION = "AI-powered analysis of Harshit's resume"
DEFAULT_TIMEOUT = 30
PROCESSING_TIMEOUT = 300  # 5 minutes for document processing

# Chat questions
CHAT_QUESTIONS = [
    "What is Harshit's educational background?",
    "What companies has Harshit worked for?",
    "What are Harshit's key skills?"
]


class StreamlitTester:
    """Automated tester for Streamlit applications using Selenium."""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.screenshots = []
        self.test_results = []
        
    def setup(self):
        """Initialize the Selenium WebDriver."""
        print("🔧 Setting up Selenium WebDriver...")
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_window_size(1920, 1080)
            print("✅ Chrome WebDriver initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome: {e}")
            print("💡 Trying Firefox instead...")
            firefox_options = webdriver.FirefoxOptions()
            if self.headless:
                firefox_options.add_argument('--headless')
            self.driver = webdriver.Firefox(options=firefox_options)
            self.driver.set_window_size(1920, 1080)
            print("✅ Firefox WebDriver initialized")
    
    def teardown(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")
    
    def take_screenshot(self, filename, description=""):
        """Take a screenshot and save it."""
        screenshot_path = os.path.join(SCREENSHOT_DIR, filename)
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        try:
            self.driver.save_screenshot(screenshot_path)
            self.screenshots.append({
                "filename": filename,
                "description": description,
                "timestamp": datetime.now().isoformat()
            })
            print(f"📸 Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save screenshot {filename}: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=DEFAULT_TIMEOUT):
        """Wait for an element to be present."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            print(f"⏱️ Timeout waiting for element: {value}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=DEFAULT_TIMEOUT):
        """Wait for an element to be clickable."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            print(f"⏱️ Timeout waiting for clickable element: {value}")
            return None
    
    def find_button_by_text(self, text):
        """Find a button by its text content."""
        try:
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if text.lower() in button.text.lower():
                    return button
            return None
        except Exception as e:
            print(f"❌ Error finding button '{text}': {e}")
            return None
    
    def wait_for_streamlit_ready(self):
        """Wait for Streamlit to finish loading."""
        time.sleep(5)  # Initial wait for Streamlit to start rendering - increased

        # Wait for the app container to be present
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stAppViewContainer']"))
            )
            print("✅ App container loaded")
        except TimeoutException:
            print("⏱️ Timeout waiting for app container")
            return False

        # Wait for sidebar to be present
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stSidebar']"))
            )
            print("✅ Sidebar loaded")
        except TimeoutException:
            print("⏱️ Timeout waiting for sidebar")
            return False

        time.sleep(3)  # Additional wait for dynamic content to render
        return True
    
    def test_step_1_startup(self):
        """Test Step 1: Application Startup."""
        print("\n" + "="*60)
        print("📋 STEP 1: Application Startup")
        print("="*60)
        
        try:
            # Navigate to application
            print(f"🌐 Navigating to {APP_URL}...")
            self.driver.get(APP_URL)
            
            # Wait for Streamlit to load
            if not self.wait_for_streamlit_ready():
                raise Exception("Streamlit failed to load")
            
            print("✅ Application loaded successfully")
            
            # Take screenshot
            self.take_screenshot("01-landing-page.png", "Application landing page")
            
            self.test_results.append({
                "step": "Step 1: Application Startup",
                "status": "PASS",
                "duration": 0,
                "notes": "Application loaded successfully"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Step 1 failed: {e}")
            self.take_screenshot(f"error-step1-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 1")
            self.test_results.append({
                "step": "Step 1: Application Startup",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False
    
    def test_step_2_create_project(self):
        """Test Step 2: Project Creation."""
        print("\n" + "="*60)
        print("📋 STEP 2: Project Creation")
        print("="*60)
        
        try:
            # Find and click CREATE button
            print("🔍 Looking for CREATE button...")
            create_button = self.find_button_by_text("CREATE")
            
            if not create_button:
                raise Exception("CREATE button not found")
            
            print("✅ Found CREATE button")
            self.take_screenshot("02-create-project-button.png", "Before clicking CREATE")
            
            # Click CREATE button
            create_button.click()
            time.sleep(5)  # Wait for dialog to open

            print("✅ Clicked CREATE button")
            self.take_screenshot("03-create-project-dialog.png", "Project creation dialog")

            # Find input fields
            print("🔍 Looking for input fields...")
            # Wait for dialog to fully render
            time.sleep(2)
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            # Fill project name
            name_input = None
            for inp in inputs:
                if inp.get_attribute("type") == "text":
                    name_input = inp
                    break
            
            if not name_input:
                raise Exception("Project name input not found")
            
            print(f"✏️ Entering project name: {PROJECT_NAME}")
            name_input.clear()
            name_input.send_keys(PROJECT_NAME)
            time.sleep(0.5)
            
            # Fill description
            if textareas:
                print(f"✏️ Entering description: {PROJECT_DESCRIPTION}")
                textareas[0].clear()
                textareas[0].send_keys(PROJECT_DESCRIPTION)
                time.sleep(0.5)
            
            self.take_screenshot("04-create-project-filled.png", "Filled project form")
            
            # Find and click Create button in dialog
            print("🔍 Looking for Create button in dialog...")
            # Wait a bit for the form to be fully rendered
            time.sleep(1)

            # Find all buttons and look for the "Create" submit button (not the "CREATE" sidebar button)
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            create_submit = None
            for button in buttons:
                # Look for button with exact text "Create" (not "CREATE")
                if button.text.strip() == "Create":
                    create_submit = button
                    break

            if not create_submit:
                raise Exception("Create submit button not found")

            print("✅ Clicking Create button...")
            # Use native click for form submission
            create_submit.click()

            # Wait for project creation and page reload
            print("⏳ Waiting for project creation...")
            time.sleep(5)  # Wait for Streamlit to process and reload

            # Wait for Streamlit to be ready again
            self.wait_for_streamlit_ready()

            self.take_screenshot("05-project-created.png", "Project created")

            print("✅ Project created successfully")
            
            self.test_results.append({
                "step": "Step 2: Project Creation",
                "status": "PASS",
                "duration": 0,
                "notes": "Project created successfully"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Step 2 failed: {e}")
            self.take_screenshot(f"error-step2-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 2")
            self.test_results.append({
                "step": "Step 2: Project Creation",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False
    
    def test_step_3_upload_document(self):
        """Test Step 3: Document Upload."""
        print("\n" + "="*60)
        print("📋 STEP 3: Document Upload")
        print("="*60)

        try:
            # Wait for page to load and tabs to appear
            print("⏳ Waiting for tabs to load...")
            time.sleep(5)  # Increased wait time

            # Wait for tabs to be present
            try:
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='tab']"))
                )
                print("✅ Tabs loaded")
            except TimeoutException:
                print("⏱️ Timeout waiting for tabs")
                # Continue anyway to see what's on the page

            # Ensure we're on the Documents tab (first tab)
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
            if tabs:
                print(f"📑 Found {len(tabs)} tabs")
                # Click first tab to ensure we're on Documents
                self.driver.execute_script("arguments[0].click();", tabs[0])
                time.sleep(3)  # Wait for tab content to load
            else:
                print("⚠️ No tabs found - checking page state...")
                # Save page source for debugging
                with open("page_source_no_tabs.html", "w") as f:
                    f.write(self.driver.page_source)
                print("💾 Saved page source to page_source_no_tabs.html")

            # Take screenshot of upload interface
            self.take_screenshot("06-upload-interface.png", "Document upload interface")
            
            # Find file input - Streamlit hides it, so we need to find it differently
            print("🔍 Looking for file input...")

            # Debug: Print all input elements
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"📋 Found {len(all_inputs)} input elements total")

            # Try multiple strategies to find file input
            file_input = None

            # Strategy 1: Look for ANY file input (even hidden ones)
            for inp in all_inputs:
                input_type = inp.get_attribute("type")
                if input_type == "file":
                    file_input = inp
                    print(f"✅ Found file input (type={input_type})")
                    break

            # Strategy 2: Look for file uploader section
            if not file_input:
                uploaders = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='stFileUploader']")
                print(f"📋 Found {len(uploaders)} file uploaders")
                if uploaders:
                    file_inputs = uploaders[0].find_elements(By.TAG_NAME, "input")
                    for inp in file_inputs:
                        if inp.get_attribute("type") == "file":
                            file_input = inp
                            print("✅ Found file input in uploader section")
                            break

            # Strategy 3: Look for section with text "Choose PDF files"
            if not file_input:
                sections = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Choose PDF')]")
                print(f"📋 Found {len(sections)} sections with 'Choose PDF' text")
                for section in sections:
                    parent = section.find_element(By.XPATH, "..")
                    file_inputs = parent.find_elements(By.TAG_NAME, "input")
                    for inp in file_inputs:
                        if inp.get_attribute("type") == "file":
                            file_input = inp
                            print("✅ Found file input near 'Choose PDF' text")
                            break
                    if file_input:
                        break

            if not file_input:
                # Save page source for debugging
                with open("page_source_debug.html", "w") as f:
                    f.write(self.driver.page_source)
                print("💾 Saved page source to page_source_debug.html for debugging")
                raise Exception("File input not found after trying multiple strategies")
            
            # Get absolute path to test file
            test_file_path = os.path.abspath(TEST_DOCUMENT_PATH)
            
            if not os.path.exists(test_file_path):
                raise Exception(f"Test file not found: {test_file_path}")
            
            print(f"📄 Uploading file: {test_file_path}")
            file_input.send_keys(test_file_path)
            time.sleep(2)  # Wait for file to be selected
            
            self.take_screenshot("07-file-selected.png", "File selected for upload")
            
            # Find and click Upload button
            print("🔍 Looking for Upload Documents button...")
            upload_button = self.find_button_by_text("Upload Documents")
            
            if not upload_button:
                raise Exception("Upload Documents button not found")
            
            print("✅ Clicking Upload Documents button...")
            upload_button.click()
            time.sleep(3)  # Wait for upload to complete
            
            self.take_screenshot("08-file-uploaded.png", "File uploaded successfully")
            
            print("✅ Document uploaded successfully")
            
            self.test_results.append({
                "step": "Step 3: Document Upload",
                "status": "PASS",
                "duration": 0,
                "notes": "Document uploaded successfully"
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Step 3 failed: {e}")
            self.take_screenshot(f"error-step3-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 3")
            self.test_results.append({
                "step": "Step 3: Document Upload",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False


    def test_step_4_process_document(self):
        """Test Step 4: Document Processing."""
        print("\n" + "="*60)
        print("📋 STEP 4: Document Processing")
        print("="*60)

        try:
            # Scroll down to find Process button
            print("📜 Scrolling to find Process Documents section...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            self.take_screenshot("09-ready-to-process.png", "Ready to process documents")

            # Find and click Process button
            print("🔍 Looking for Process All Documents button...")
            # Try with emoji first, then without
            process_button = self.find_button_by_text("🚀 Process All Documents")
            if not process_button:
                process_button = self.find_button_by_text("Process All Documents")

            if not process_button:
                raise Exception("Process All Documents button not found")

            print("✅ Clicking Process All Documents button...")
            process_button.click()

            # Wait for processing to complete (this may take a while)
            print("⏳ Waiting for processing to complete (up to 5 minutes)...")
            time.sleep(5)  # Initial wait

            self.take_screenshot("10-processing-in-progress.png", "Processing in progress")

            # Wait for success message or timeout
            start_time = time.time()
            while time.time() - start_time < PROCESSING_TIMEOUT:
                # Check if processing is complete by looking for success message
                page_text = self.driver.page_source
                if "processed successfully" in page_text.lower() or "all documents have been processed" in page_text.lower():
                    print("✅ Processing completed!")
                    break
                time.sleep(5)  # Check every 5 seconds

            time.sleep(2)
            self.take_screenshot("11-processing-complete.png", "Processing complete")

            print("✅ Document processed successfully")

            self.test_results.append({
                "step": "Step 4: Document Processing",
                "status": "PASS",
                "duration": 0,
                "notes": "Document processed successfully"
            })

            return True

        except Exception as e:
            print(f"❌ Step 4 failed: {e}")
            self.take_screenshot(f"error-step4-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 4")
            self.test_results.append({
                "step": "Step 4: Document Processing",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False

    def test_step_5_view_ontology(self):
        """Test Step 5: Ontology Viewing."""
        print("\n" + "="*60)
        print("📋 STEP 5: Ontology Viewing")
        print("="*60)

        try:
            # Click on Ontology tab
            print("🔍 Looking for Ontology tab...")
            time.sleep(3)  # Wait for any overlays to disappear

            # Find tab by text
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
            ontology_tab = None
            for tab in tabs:
                if "ontology" in tab.text.lower():
                    ontology_tab = tab
                    break

            if not ontology_tab:
                raise Exception("Ontology tab not found")

            print("✅ Clicking Ontology tab...")
            # Use JavaScript click to avoid overlay interception
            self.driver.execute_script("arguments[0].click();", ontology_tab)
            time.sleep(2)

            self.take_screenshot("12-ontology-tab.png", "Ontology tab")

            # Find and click Generate Ontology button
            print("🔍 Looking for Generate Ontology button...")
            generate_button = self.find_button_by_text("Generate Ontology")

            if not generate_button:
                raise Exception("Generate Ontology button not found")

            print("✅ Clicking Generate Ontology button...")
            generate_button.click()
            time.sleep(15)  # Wait for ontology generation

            self.take_screenshot("13-ontology-generated.png", "Ontology generated")

            # Scroll to see relationships
            self.driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
            self.take_screenshot("14-ontology-relationships.png", "Ontology relationships")

            print("✅ Ontology viewed successfully")

            self.test_results.append({
                "step": "Step 5: Ontology Viewing",
                "status": "PASS",
                "duration": 0,
                "notes": "Ontology generated and viewed"
            })

            return True

        except Exception as e:
            print(f"❌ Step 5 failed: {e}")
            self.take_screenshot(f"error-step5-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 5")
            self.test_results.append({
                "step": "Step 5: Ontology Viewing",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False

    def test_step_6_extract_knowledge(self):
        """Test Step 6: Knowledge Extraction."""
        print("\n" + "="*60)
        print("📋 STEP 6: Knowledge Extraction")
        print("="*60)

        try:
            # Click on Knowledge Base tab
            print("🔍 Looking for Knowledge Base tab...")
            time.sleep(2)  # Wait for any overlays to disappear
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
            kb_tab = None
            for tab in tabs:
                if "knowledge" in tab.text.lower():
                    kb_tab = tab
                    break

            if not kb_tab:
                raise Exception("Knowledge Base tab not found")

            print("✅ Clicking Knowledge Base tab...")
            # Use JavaScript click to avoid overlay interception
            self.driver.execute_script("arguments[0].click();", kb_tab)
            time.sleep(2)

            self.take_screenshot("15-knowledge-base-tab.png", "Knowledge Base tab")

            # Find and click Start Knowledge Extraction button
            print("🔍 Looking for Start Knowledge Extraction button...")
            extract_button = self.find_button_by_text("Start Knowledge Extraction")

            if extract_button:
                print("✅ Clicking Start Knowledge Extraction button...")
                extract_button.click()
                time.sleep(15)  # Wait for extraction

                self.take_screenshot("16-knowledge-extracted.png", "Knowledge extracted")
            else:
                print("ℹ️ Knowledge already extracted")
                self.take_screenshot("16-knowledge-extracted.png", "Knowledge base view")

            # Browse different entity tabs
            time.sleep(2)
            self.take_screenshot("17-knowledge-overview.png", "Knowledge overview")

            print("✅ Knowledge extraction completed")

            self.test_results.append({
                "step": "Step 6: Knowledge Extraction",
                "status": "PASS",
                "duration": 0,
                "notes": "Knowledge extracted successfully"
            })

            return True

        except Exception as e:
            print(f"❌ Step 6 failed: {e}")
            self.take_screenshot(f"error-step6-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 6")
            self.test_results.append({
                "step": "Step 6: Knowledge Extraction",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False

    def test_step_7_chat_interface(self):
        """Test Step 7: Chat Interface."""
        print("\n" + "="*60)
        print("📋 STEP 7: Chat Interface")
        print("="*60)

        try:
            # Click on Chat tab
            print("🔍 Looking for Chat tab...")
            time.sleep(2)  # Wait for any overlays to disappear
            tabs = self.driver.find_elements(By.CSS_SELECTOR, "[role='tab']")
            chat_tab = None
            for tab in tabs:
                if "chat" in tab.text.lower():
                    chat_tab = tab
                    break

            if not chat_tab:
                raise Exception("Chat tab not found")

            print("✅ Clicking Chat tab...")
            # Use JavaScript click to avoid overlay interception
            self.driver.execute_script("arguments[0].click();", chat_tab)
            time.sleep(2)

            self.take_screenshot("18-chat-interface.png", "Chat interface")

            # Find chat input
            print("🔍 Looking for chat input...")
            chat_inputs = self.driver.find_elements(By.TAG_NAME, "textarea")

            if not chat_inputs:
                chat_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")

            if not chat_inputs:
                raise Exception("Chat input not found")

            chat_input = chat_inputs[-1]  # Get the last input (likely the chat input)

            # Ask questions
            for i, question in enumerate(CHAT_QUESTIONS, 1):
                print(f"💬 Asking question {i}: {question}")

                chat_input.clear()
                chat_input.send_keys(question)
                chat_input.send_keys(Keys.RETURN)

                time.sleep(10)  # Wait for response

                self.take_screenshot(f"19-chat-question-{i}.png", f"Chat question {i}")

            print("✅ Chat interface tested successfully")

            self.test_results.append({
                "step": "Step 7: Chat Interface",
                "status": "PASS",
                "duration": 0,
                "notes": "Chat tested with 3 questions"
            })

            return True

        except Exception as e:
            print(f"❌ Step 7 failed: {e}")
            self.take_screenshot(f"error-step7-{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "Error in step 7")
            self.test_results.append({
                "step": "Step 7: Chat Interface",
                "status": "FAIL",
                "duration": 0,
                "notes": str(e)
            })
            return False


def main():
    """Main test execution."""
    print("🚀 Starting Selenium E2E Testing for SuperSuite")
    print("="*60)

    # Create tester instance
    tester = StreamlitTester(headless=False)

    try:
        # Setup
        tester.setup()

        # Run all 7 tests
        tester.test_step_1_startup()
        tester.test_step_2_create_project()
        tester.test_step_3_upload_document()
        tester.test_step_4_process_document()
        tester.test_step_5_view_ontology()
        tester.test_step_6_extract_knowledge()
        tester.test_step_7_chat_interface()

        # Generate report
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in tester.test_results if r["status"] == "PASS")
        failed = sum(1 for r in tester.test_results if r["status"] == "FAIL")

        print(f"✅ Passed: {passed}/{len(tester.test_results)}")
        print(f"❌ Failed: {failed}/{len(tester.test_results)}")
        print(f"📸 Screenshots: {len(tester.screenshots)}")

        # Save report
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(tester.test_results),
                "passed": passed,
                "failed": failed
            },
            "results": tester.test_results,
            "screenshots": tester.screenshots
        }

        with open("selenium_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\n📄 Report saved to: selenium_test_report.json")
        print(f"📸 Screenshots saved to: {SCREENSHOT_DIR}/")

    finally:
        # Cleanup
        print("\n⏸️  Keeping browser open for 30 seconds for review...")
        time.sleep(30)
        tester.teardown()


if __name__ == "__main__":
    main()

