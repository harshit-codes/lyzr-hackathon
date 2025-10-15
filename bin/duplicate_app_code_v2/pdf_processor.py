#!/usr/bin/env python3
"""
SuperSuite PDF Processor - Command Line Interface

A command-line interface for processing PDF documents through the SuperSuite platform.
This provides the same functionality as the web interface but in a terminal-based format.

Usage:
    python3 pdf_processor.py --pdf path/to/document.pdf --project "My Project"
    python3 pdf_processor.py --query "What are the main topics?" --project "My Project"
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import SuperSuite components (with error handling for missing dependencies)
try:
    from end_to_end_orchestrator import EndToEndOrchestrator
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    MISSING_DEPS_ERROR = str(e)


class SuperSuiteCLI:
    """Command-line interface for SuperSuite PDF processing."""

    def __init__(self):
        self.orchestrator: Optional[EndToEndOrchestrator] = None
        self.current_project = None

    def initialize(self):
        """Initialize the SuperSuite orchestrator."""
        if not DEPENDENCIES_AVAILABLE:
            print("❌ Missing dependencies. Please install required packages:")
            print(f"   Error: {MISSING_DEPS_ERROR}")
            print("   Run: pip install python-dotenv sqlmodel PyPDF2 transformers sentence-transformers snowflake-sqlalchemy")
            return False

        print("🚀 Initializing SuperSuite...")
        try:
            self.orchestrator = EndToEndOrchestrator()
            self.orchestrator.initialize_services()
            print("✅ SuperSuite initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize SuperSuite: {e}")
            return False

    def create_project(self, project_name: str):
        """Create a new project."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        print(f"🏗️ Creating project: {project_name}")
        try:
            project = self.orchestrator.create_project(
                project_name=project_name,
                description=f"CLI project: {project_name}"
            )
            self.current_project = project
            print(f"✅ Project '{project_name}' created successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to create project: {e}")
            return False

    def process_pdf(self, pdf_path: str, project_name: Optional[str] = None):
        """Process a PDF file through SuperSuite."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        # Create project if specified
        if project_name and not self.current_project:
            if not self.create_project(project_name):
                return False

        if not self.current_project:
            print("❌ No active project. Use --project to specify a project name.")
            return False

        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False

        print(f"📤 Processing PDF: {pdf_path}")
        print("=" * 60)

        try:
            # Process through SuperSuite
            results = self.orchestrator.process_document(
                pdf_path,
                self.current_project["kb_project"].project_id
            )

            if results.get("success"):
                print("✅ PDF processed successfully!")
                print("\n📊 Processing Results:")
                print("-" * 30)

                scan_results = results.get("scan_results", {})
                kb_results = results.get("kb_results", {})

                print(f"📄 File: {Path(pdf_path).name}")
                print(f"📊 Chunks created: {kb_results.get('chunks', 0)}")
                print(f"🏷️ Entities extracted: {kb_results.get('entities', 0)}")
                print(f"🔗 Relationships created: {kb_results.get('edges', 0)}")
                print(f"🧠 Embeddings generated: {kb_results.get('embeddings', 0)}")
                print(f"📚 Schemas created: {scan_results.get('schemas_created', 0)}")
                print(f"🔄 Neo4j synced: {'✅' if kb_results.get('neo4j_synced') else '❌'}")

                # Initialize chat agent
                print("\n🤖 Initializing chat agent...")
                self.orchestrator.initialize_chat_agent()
                print("✅ Ready for questions! Use --query to ask questions.")

                return True
            else:
                print(f"❌ Processing failed: {results.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Processing error: {e}")
            return False

    def query_document(self, query: str):
        """Query the processed knowledge base."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        if not self.current_project:
            print("❌ No active project. Process a PDF first.")
            return False

        print(f"🤔 Query: {query}")
        print("-" * 40)

        try:
            response = self.orchestrator.query_knowledge_base(query)

            if "error" in response:
                print(f"❌ Query failed: {response['error']}")
                return False

            print(f"💬 Response: {response.get('response', 'No response')}")
            print(f"🎯 Intent: {response.get('intent', 'Unknown')}")
            print(f"📚 Citations: {response.get('citations', 0)}")
            print(f"⚡ Response time: {response.get('execution_time', 0):.2f}s")

            return True

        except Exception as e:
            print(f"❌ Query error: {e}")
            return False

    def show_stats(self):
        """Show processing statistics."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return

        summary = self.orchestrator.get_processing_summary()

        if summary.get("total_files", 0) == 0:
            print("📊 No documents processed yet.")
            return

        print("📊 SuperSuite Statistics")
        print("=" * 40)
        print(f"📄 Total files processed: {summary['total_files']}")
        print(f"📊 Total chunks: {summary['total_chunks']}")
        print(f"🏷️ Total entities: {summary['total_entities']}")
        print(f"📚 Total schemas: {summary['total_schemas']}")
        print(f"🔄 Neo4j synchronized: {'✅' if summary.get('neo4j_synced') else '❌'}")

        if summary.get("files"):
            print("\n📋 Processed Files:")
            for file_info in summary["files"]:
                print(f"  📄 {file_info['filename']}: {file_info['entities']} entities, {file_info['chunks']} chunks")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="SuperSuite PDF Processor - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF and create a new project
  python3 pdf_processor.py --pdf research_paper.pdf --project "My Research"

  # Ask questions about processed documents
  python3 pdf_processor.py --query "What are the main findings?" --project "My Research"

  # View processing statistics
  python3 pdf_processor.py --stats

  # Interactive mode (process PDF and then query)
  python3 pdf_processor.py --pdf document.pdf --project "Test Project" --interactive
        """
    )

    parser.add_argument("--pdf", help="Path to PDF file to process")
    parser.add_argument("--project", help="Project name for organizing documents")
    parser.add_argument("--query", help="Question to ask about processed documents")
    parser.add_argument("--stats", action="store_true", help="Show processing statistics")
    parser.add_argument("--interactive", action="store_true",
                       help="Enter interactive mode after processing")

    args = parser.parse_args()

    # Validate arguments
    if not any([args.pdf, args.query, args.stats]):
        parser.print_help()
        return

    # Initialize CLI
    cli = SuperSuiteCLI()

    if not cli.initialize():
        return

    # Handle stats request
    if args.stats:
        cli.show_stats()
        return

    # Handle project creation/loading
    if args.project:
        # Try to create project (will handle if it already exists)
        cli.create_project(args.project)

    # Handle PDF processing
    if args.pdf:
        if cli.process_pdf(args.pdf, args.project):
            if args.interactive:
                print("\n💬 Interactive Query Mode")
                print("Type your questions or 'quit' to exit")
                print("-" * 40)

                while True:
                    try:
                        query = input("❓ Question: ").strip()
                        if query.lower() in ['quit', 'exit', 'q']:
                            break
                        if query:
                            cli.query_document(query)
                            print()
                    except KeyboardInterrupt:
                        break
                print("👋 Goodbye!")
        return

    # Handle direct queries
    if args.query:
        cli.query_document(args.query)


if __name__ == "__main__":
    main()


class SuperSuiteCLI:
    """Command-line interface for SuperSuite PDF processing."""

    def __init__(self):
        self.orchestrator: Optional[EndToEndOrchestrator] = None
        self.current_project = None

    def initialize(self):
        """Initialize the SuperSuite orchestrator."""
        print("🚀 Initializing SuperSuite...")
        try:
            self.orchestrator = EndToEndOrchestrator()
            self.orchestrator.initialize_services()
            print("✅ SuperSuite initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize SuperSuite: {e}")
            return False

    def create_project(self, project_name: str):
        """Create a new project."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        print(f"🏗️ Creating project: {project_name}")
        try:
            project = self.orchestrator.create_project(
                project_name=project_name,
                description=f"CLI project: {project_name}"
            )
            self.current_project = project
            print(f"✅ Project '{project_name}' created successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to create project: {e}")
            return False

    def process_pdf(self, pdf_path: str, project_name: Optional[str] = None):
        """Process a PDF file through SuperSuite."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        # Create project if specified
        if project_name and not self.current_project:
            if not self.create_project(project_name):
                return False

        if not self.current_project:
            print("❌ No active project. Use --project to specify a project name.")
            return False

        # Check if PDF exists
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return False

        print(f"📤 Processing PDF: {pdf_path}")
        print("=" * 60)

        try:
            # Process through SuperSuite
            results = self.orchestrator.process_document(
                pdf_path,
                self.current_project["kb_project"].project_id
            )

            if results.get("success"):
                print("✅ PDF processed successfully!")
                print("\n📊 Processing Results:")
                print("-" * 30)

                scan_results = results.get("scan_results", {})
                kb_results = results.get("kb_results", {})

                print(f"📄 File: {Path(pdf_path).name}")
                print(f"📊 Chunks created: {kb_results.get('chunks', 0)}")
                print(f"🏷️ Entities extracted: {kb_results.get('entities', 0)}")
                print(f"🔗 Relationships created: {kb_results.get('edges', 0)}")
                print(f"🧠 Embeddings generated: {kb_results.get('embeddings', 0)}")
                print(f"📚 Schemas created: {scan_results.get('schemas_created', 0)}")
                print(f"🔄 Neo4j synced: {'✅' if kb_results.get('neo4j_synced') else '❌'}")

                # Initialize chat agent
                print("\n🤖 Initializing chat agent...")
                self.orchestrator.initialize_chat_agent()
                print("✅ Ready for questions! Use --query to ask questions.")

                return True
            else:
                print(f"❌ Processing failed: {results.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Processing error: {e}")
            return False

    def query_document(self, query: str):
        """Query the processed knowledge base."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return False

        if not self.current_project:
            print("❌ No active project. Process a PDF first.")
            return False

        print(f"🤔 Query: {query}")
        print("-" * 40)

        try:
            response = self.orchestrator.query_knowledge_base(query)

            if "error" in response:
                print(f"❌ Query failed: {response['error']}")
                return False

            print(f"💬 Response: {response.get('response', 'No response')}")
            print(f"🎯 Intent: {response.get('intent', 'Unknown')}")
            print(f"📚 Citations: {response.get('citations', 0)}")
            print(f"⚡ Response time: {response.get('execution_time', 0):.2f}s")

            return True

        except Exception as e:
            print(f"❌ Query error: {e}")
            return False

    def show_stats(self):
        """Show processing statistics."""
        if not self.orchestrator:
            print("❌ SuperSuite not initialized")
            return

        summary = self.orchestrator.get_processing_summary()

        if summary.get("total_files", 0) == 0:
            print("📊 No documents processed yet.")
            return

        print("📊 SuperSuite Statistics")
        print("=" * 40)
        print(f"📄 Total files processed: {summary['total_files']}")
        print(f"📊 Total chunks: {summary['total_chunks']}")
        print(f"🏷️ Total entities: {summary['total_entities']}")
        print(f"📚 Total schemas: {summary['total_schemas']}")
        print(f"🔄 Neo4j synchronized: {'✅' if summary.get('neo4j_synced') else '❌'}")

        if summary.get("files"):
            print("\n📋 Processed Files:")
            for file_info in summary["files"]:
                print(f"  📄 {file_info['filename']}: {file_info['entities']} entities, {file_info['chunks']} chunks")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="SuperSuite PDF Processor - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a PDF and create a new project
  python3 pdf_processor.py --pdf research_paper.pdf --project "My Research"

  # Ask questions about processed documents
  python3 pdf_processor.py --query "What are the main findings?" --project "My Research"

  # View processing statistics
  python3 pdf_processor.py --stats

  # Interactive mode (process PDF and then query)
  python3 pdf_processor.py --pdf document.pdf --project "Test Project" --interactive
        """
    )

    parser.add_argument("--pdf", help="Path to PDF file to process")
    parser.add_argument("--project", help="Project name for organizing documents")
    parser.add_argument("--query", help="Question to ask about processed documents")
    parser.add_argument("--stats", action="store_true", help="Show processing statistics")
    parser.add_argument("--interactive", action="store_true",
                       help="Enter interactive mode after processing")

    args = parser.parse_args()

    # Validate arguments
    if not any([args.pdf, args.query, args.stats]):
        parser.print_help()
        return

    # Initialize CLI
    cli = SuperSuiteCLI()

    if not cli.initialize():
        return

    # Handle stats request
    if args.stats:
        cli.show_stats()
        return

    # Handle project creation/loading
    if args.project:
        # Try to create project (will handle if it already exists)
        cli.create_project(args.project)

    # Handle PDF processing
    if args.pdf:
        if cli.process_pdf(args.pdf, args.project):
            if args.interactive:
                print("\n💬 Interactive Query Mode")
                print("Type your questions or 'quit' to exit")
                print("-" * 40)

                while True:
                    try:
                        query = input("❓ Question: ").strip()
                        if query.lower() in ['quit', 'exit', 'q']:
                            break
                        if query:
                            cli.query_document(query)
                            print()
                    except KeyboardInterrupt:
                        break
                print("👋 Goodbye!")
        return

    # Handle direct queries
    if args.query:
        cli.query_document(args.query)


if __name__ == "__main__":
    main()