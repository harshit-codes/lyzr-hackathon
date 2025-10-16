# Manual Testing Guide - SuperSuite Application

## Important Changes Made

### Fixed Issues
1. ✅ **Added Document Processing** - The Documents tab now has a "Process All Documents" button
2. ✅ **File Persistence** - Uploaded files are now saved to `uploads/{project_id}/` directory
3. ✅ **Processing Workflow** - Documents must be processed before ontology generation

### Application is Ready for Testing
- URL: http://localhost:8504
- Test File: `app/notebooks/test_data/resume-harshit.pdf`
- Browser: Already open

---

## Testing Workflow (7 Steps)

### Step 1: Application Startup ✅
**What to Test:**
- Application loads without errors
- Sidebar shows "Project Dashboard"
- Main area shows "No Project Selected" message

**Screenshot to Capture:**
- `01-landing-page.png` - Full application view

**Expected Result:**
- Clean UI with sidebar and main content area
- "CREATE" button visible in sidebar
- No error messages

---

### Step 2: Project Creation
**What to Do:**
1. Click "CREATE" button in sidebar
2. Dialog opens with form
3. Enter:
   - Project Name: `Resume Analysis - Harshit`
   - Description: `AI-powered analysis of Harshit's resume`
4. Click "Create" button

**Screenshots to Capture:**
- `02-create-project-dialog.png` - Empty dialog form
- `03-create-project-filled.png` - Filled form before clicking Create
- `04-project-created.png` - Success message and project selected

**Expected Result:**
- Success message appears
- Project appears in sidebar
- Project is automatically selected
- Main area shows 4 tabs: Documents, Ontology, Knowledge Base, Chat

---

### Step 3: Document Upload
**What to Do:**
1. Stay on "Documents" tab (first tab)
2. Click "Choose PDF files to upload" button
3. Select file: `app/notebooks/test_data/resume-harshit.pdf`
4. Verify file appears in preview
5. Click "⬆️ Upload Documents" button

**Screenshots to Capture:**
- `05-upload-interface.png` - File uploader before selecting file
- `06-file-selected.png` - File preview showing resume-harshit.pdf
- `07-file-uploaded.png` - Success message and file in documents list

**Expected Result:**
- File appears in "File Preview" section
- Shows filename, size (~111 KB), and PDF icon
- After upload: Success message
- Document appears in "Project Documents" table with status "Uploaded"

---

### Step 4: Document Processing (NEW FEATURE)
**What to Do:**
1. Scroll down to "Process Documents" section
2. Should show "X document(s) ready to process"
3. Click "🚀 Process All Documents" button
4. Wait for processing to complete (may take 30-60 seconds)
5. Watch progress bar and status messages

**Screenshots to Capture:**
- `08-ready-to-process.png` - Before clicking Process button
- `09-processing-in-progress.png` - Progress bar showing processing
- `10-processing-complete.png` - Success message after processing

**Expected Result:**
- Progress bar shows processing status
- Status text shows "Processing resume-harshit.pdf..."
- Success message: "✅ All documents processed successfully!"
- Document status changes from "Uploaded" to "Processed"

**Note:** This is a REAL processing step that:
- Extracts text from PDF
- Generates schema using DeepSeek AI
- Extracts entities
- Stores data in Snowflake
- May take 30-60 seconds

---

### Step 5: Ontology Viewing
**What to Do:**
1. Click on "🎯 Ontology" tab (second tab)
2. Should see list of processed documents with checkboxes
3. Ensure "resume-harshit.pdf" is checked
4. Click "🤖 Generate Ontology" button
5. Wait for ontology generation (may take 10-20 seconds)
6. View generated entity types and relationships

**Screenshots to Capture:**
- `11-ontology-tab.png` - Before generating ontology
- `12-ontology-generating.png` - Spinner showing "Analyzing documents..."
- `13-ontology-generated.png` - Entity Types table
- `14-ontology-relationships.png` - Relationship Types table

**Expected Result:**
- Document checkbox appears
- After generation: Two tables appear
  - "🏗️ Entity Types" - Shows entities like Person, Organization, etc.
  - "🔗 Relationship Types" - Shows relationships
- Metrics show: Entity Types count, Relationships count, Total Attributes
- Note: "Ontology generated using DeepSeek AI analysis"

---

### Step 6: Knowledge Extraction
**What to Do:**
1. Click on "🧠 Knowledge Base" tab (third tab)
2. Should see "Extract Knowledge" section
3. Click "🚀 Start Knowledge Extraction" button
4. Wait for extraction (may take 10-20 seconds)
5. View extracted entities in sub-tabs

**Screenshots to Capture:**
- `15-knowledge-base-tab.png` - Before extraction
- `16-extraction-in-progress.png` - Spinner showing "Extracting knowledge..."
- `17-knowledge-extracted.png` - Overview tab with statistics
- `18-persons-tab.png` - Persons entities (if any)
- `19-organizations-tab.png` - Organizations entities (if any)

**Expected Result:**
- Success message: "✅ Knowledge base ready!"
- Four sub-tabs appear: Persons, Organizations, Concepts, Overview
- Overview tab shows statistics:
  - Total Entities
  - Total Relationships
  - Tables Created
  - Extraction Time
- Entity tables show real data extracted from resume
- Note: "Knowledge extracted using DeepSeek AI processing"

---

### Step 7: Chat Interface
**What to Do:**
1. Click on "💬 Chat" tab (fourth tab)
2. Should see chat interface with suggestions
3. Type question: `What is Harshit's educational background?`
4. Press Enter and wait for response
5. Ask second question: `What companies has Harshit worked for?`
6. Ask third question: `What are Harshit's key skills?`

**Screenshots to Capture:**
- `20-chat-interface.png` - Empty chat interface
- `21-chat-question-1.png` - First question and response
- `22-chat-question-2.png` - Second question and response
- `23-chat-question-3.png` - Third question and response
- `24-chat-quick-actions.png` - Quick action buttons at bottom

**Expected Result:**
- Chat input field at bottom
- Suggestions shown initially
- Each question appears as user message
- AI responses appear with thinking spinner
- Responses should reference actual resume content
- Quick action buttons: "Summarize Content", "List Key People", "List Organizations"

---

## Screenshot Checklist

Save all screenshots to: `docs/assets/screenshots/`

- [ ] `01-landing-page.png`
- [ ] `02-create-project-dialog.png`
- [ ] `03-create-project-filled.png`
- [ ] `04-project-created.png`
- [ ] `05-upload-interface.png`
- [ ] `06-file-selected.png`
- [ ] `07-file-uploaded.png`
- [ ] `08-ready-to-process.png`
- [ ] `09-processing-in-progress.png`
- [ ] `10-processing-complete.png`
- [ ] `11-ontology-tab.png`
- [ ] `12-ontology-generating.png`
- [ ] `13-ontology-generated.png`
- [ ] `14-ontology-relationships.png`
- [ ] `15-knowledge-base-tab.png`
- [ ] `16-extraction-in-progress.png`
- [ ] `17-knowledge-extracted.png`
- [ ] `18-persons-tab.png`
- [ ] `19-organizations-tab.png`
- [ ] `20-chat-interface.png`
- [ ] `21-chat-question-1.png`
- [ ] `22-chat-question-2.png`
- [ ] `23-chat-question-3.png`
- [ ] `24-chat-quick-actions.png`

**Total: 24 screenshots**

---

## Issues to Watch For

### Potential Issues
1. **Service Initialization Errors**
   - If you see "Failed to initialize services", check .env file
   - Ensure Snowflake, Neo4j, DeepSeek credentials are correct

2. **Processing Timeouts**
   - Document processing may take 30-60 seconds
   - Don't refresh the page during processing

3. **Empty Results**
   - If ontology or knowledge base is empty, check Snowflake data
   - Verify document was actually processed (status = "Processed")

4. **Chat Not Working**
   - Ensure knowledge base was extracted first
   - Check DeepSeek API key is valid

### How to Report Issues
If you encounter any errors:
1. Take screenshot of the error
2. Note the step where it occurred
3. Check browser console for errors (F12 → Console tab)
4. Report back with details

---

## After Testing

### If All Tests Pass ✅
1. Confirm all 24 screenshots captured
2. Verify screenshots show real data (not mock data)
3. Note any UI improvements needed
4. Proceed to documentation update

### If Tests Fail ❌
1. Document which step failed
2. Capture error screenshot
3. Note error message
4. Report back for debugging

---

## Quick Commands

```bash
# View application
open http://localhost:8504

# Check if app is running
lsof -ti:8504

# View test file
open app/notebooks/test_data/resume-harshit.pdf

# View screenshots directory
open docs/assets/screenshots/
```

---

**Ready to test! Open http://localhost:8504 and follow the 7 steps above.** 🚀

