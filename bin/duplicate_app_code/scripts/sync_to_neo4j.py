#!/usr/bin/env python3
"""
Manual Sync CLI Tool

Usage:
  python scripts/sync_to_neo4j.py --sync-all
  python scripts/sync_to_neo4j.py --verify
  python scripts/sync_to_neo4j.py --sync-file <file_id>
  python scripts/sync_to_neo4j.py --force-resync
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine
from dotenv import load_dotenv
from superkb.sync_orchestrator import SyncOrchestrator
from graph_rag.database.snowflake_connector import SnowflakeConnector


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Sync Snowflake knowledge graph to Neo4j"
    )
    
    # Sync operations
    parser.add_argument(
        "--sync-all",
        action="store_true",
        help="Sync all nodes and edges to Neo4j"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify sync status between Snowflake and Neo4j"
    )
    
    parser.add_argument(
        "--sync-file",
        type=str,
        help="Sync nodes from specific file ID"
    )
    
    parser.add_argument(
        "--force-resync",
        action="store_true",
        help="Force resync (clear and rebuild Neo4j)"
    )
    
    # Connection options
    parser.add_argument(
        "--neo4j-uri",
        type=str,
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        help="Neo4j connection URI"
    )
    
    parser.add_argument(
        "--neo4j-user",
        type=str,
        default=os.getenv("NEO4J_USER", "neo4j"),
        help="Neo4j username"
    )
    
    parser.add_argument(
        "--neo4j-password",
        type=str,
        default=os.getenv("NEO4J_PASSWORD", "password"),
        help="Neo4j password"
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Connect to Snowflake
    print("Connecting to Snowflake...")
    connector = SnowflakeConnector()
    engine = connector.get_engine()
    
    # Create session
    with Session(engine) as db:
        # Initialize sync orchestrator
        sync_orch = SyncOrchestrator(
            db=db,
            neo4j_uri=args.neo4j_uri,
            neo4j_user=args.neo4j_user,
            neo4j_password=args.neo4j_password
        )
        
        try:
            # Execute requested operation
            if args.sync_all or args.force_resync:
                print("\n🔄 Starting full sync...")
                stats = sync_orch.sync_all(force=args.force_resync)
                
                print("\nSync Results:")
                print(f"  Nodes synced: {stats['nodes']}")
                print(f"  Relationships synced: {stats['relationships']}")
                print(f"  Duration: {stats['duration_seconds']:.2f}s")
                
            elif args.sync_file:
                print(f"\n🔄 Syncing file {args.sync_file}...")
                count = sync_orch.sync_nodes(file_id=args.sync_file)
                print(f"✓ Synced {count} nodes from file")
                
            elif args.verify:
                print("\n🔍 Verifying sync status...")
                results = sync_orch.verify_sync()
                
                if results['in_sync']:
                    print("\n✓ ✓ ✓ Databases are in sync! ✓ ✓ ✓")
                else:
                    print("\n⚠ Databases are out of sync")
                    print("\nSnowflake:")
                    print(f"  Nodes: {results['snowflake']['nodes']}")
                    print(f"  Edges: {results['snowflake']['edges']}")
                    print("\nNeo4j:")
                    print(f"  Nodes: {results['neo4j']['nodes']}")
                    print(f"  Relationships: {results['neo4j']['relationships']}")
                    print("\nDiff:")
                    print(f"  Nodes: {results['diff']['nodes']} missing in Neo4j")
                    print(f"  Edges: {results['diff']['edges']} missing in Neo4j")
                    
            else:
                parser.print_help()
                return 1
            
        finally:
            sync_orch.close()
    
    print("\n✓ Sync operation completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
