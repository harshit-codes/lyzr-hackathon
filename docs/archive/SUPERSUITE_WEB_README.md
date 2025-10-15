# 🚀 SuperSuite - AI-Powered Document Intelligence Platform

A beautiful web interface for the complete SuperSuite platform that transforms PDF documents into interactive knowledge bases with conversational AI capabilities.

## ✨ Features

### 🖼️ **SuperScan**
- Intelligent document analysis and structure recognition
- Automatic schema proposal generation
- Entity and relationship detection

### 🧠 **SuperKB**
- Knowledge graph creation from documents
- Entity extraction using advanced NER models
- Vector embeddings for semantic search
- Neo4j graph database synchronization

### 💬 **SuperChat**
- Conversational AI interface
- Multi-step reasoning with tool orchestration
- Context-aware responses with citations
- Natural language querying

### 🎨 **Beautiful Web Interface**
- Drag & drop PDF upload
- Real-time processing status
- Interactive chat interface
- Processing analytics and insights

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
pip install streamlit

# Set up environment variables (optional)
export OPENAI_API_KEY="your-openai-key"  # For enhanced schema proposals
export NEO4J_URI="bolt://localhost:7687"  # For graph database
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
```

### Launch the Application

#### Option 1: Using the launcher script
```bash
./run_supersuite.sh
```

#### Option 2: Direct Streamlit run
```bash
streamlit run code/streamlit_app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 How to Use

### 1. **Create a Project**
- Enter a descriptive project name
- Click "🎯 Create Project"

### 2. **Upload PDF Document**
- Drag and drop or click to select a PDF file
- Click "🚀 Process Document" to start analysis

### 3. **Monitor Processing**
- Watch real-time progress through SuperScan → SuperKB → SuperChat
- View processing statistics and results

### 4. **Chat with Your Document**
- Ask questions in natural language
- Get AI-powered responses with source citations
- Explore relationships and entities

## 🎯 Example Usage

1. **Upload a research paper PDF**
2. **Ask questions like:**
   - "What are the main research questions?"
   - "Who are the key contributors?"
   - "What methodologies are used?"
   - "Summarize the conclusions"

3. **Explore the knowledge graph:**
   - View extracted entities and relationships
   - See processing statistics
   - Track citation sources

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │ -> │ End-to-End      │ -> │   SuperSuite    │
│                 │    │ Orchestrator    │    │   Components   │
│ • File Upload   │    │                 │    │                │
│ • Progress UI   │    │ • SuperScan     │    │ • SuperScan    │
│ • Chat Interface│    │ • SuperKB       │    │ • SuperKB      │
│ • Analytics     │    │ • SuperChat     │    │ • SuperChat    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Technical Details

### Components Integration

- **SuperScan**: Document structure analysis and schema generation
- **SuperKB**: Knowledge base creation with entity extraction and embeddings
- **SuperChat**: Conversational AI with multi-modal reasoning
- **Streamlit**: Modern web interface with real-time updates

### Data Flow

1. **PDF Upload** → Temporary file storage
2. **SuperScan** → Text extraction, schema proposals
3. **SuperKB** → Chunking, entity extraction, embeddings, Neo4j sync
4. **SuperChat** → Agent initialization for conversational queries
5. **User Queries** → AI reasoning → Cited responses

### Error Handling

- Graceful degradation when services unavailable
- Clear error messages and recovery suggestions
- Processing status tracking and rollback capabilities

## 📊 Analytics & Insights

The application provides comprehensive analytics:

- **Processing Metrics**: Chunks, entities, relationships, embeddings
- **Performance Stats**: Processing time, query response times
- **Citation Tracking**: Source verification for all responses
- **Project History**: Track all processed documents

## 🔒 Security & Privacy

- All processing happens locally (except optional external APIs)
- No document content is stored permanently
- Temporary files are cleaned up automatically
- API keys are optional and user-provided

## 🚀 Production Deployment

For production deployment:

```bash
# Set environment variables
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run with proper configuration
streamlit run code/streamlit_app.py --server.enableCORS=false --server.enableXsrfProtection=true
```

## 🐛 Troubleshooting

### Common Issues

1. **"SuperSuite initialization failed"**
   - Check database connections
   - Verify environment variables
   - Ensure all dependencies are installed

2. **"PDF processing failed"**
   - Verify PDF is not corrupted
   - Check file size limits
   - Ensure PDF text is extractable

3. **"Chat queries not working"**
   - Verify Neo4j connection (optional)
   - Check if document was processed successfully
   - Ensure chat agent was initialized

### Debug Mode

Run with debug logging:
```bash
STREAMLIT_LOG_LEVEL=debug streamlit run code/streamlit_app.py
```

## 🤝 Contributing

This is a hackathon project showcasing the SuperSuite platform. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the SuperSuite platform demonstration.

---

**Built with ❤️ for the SuperSuite Hackathon**

Transform your documents into intelligent, conversational knowledge bases! 🚀