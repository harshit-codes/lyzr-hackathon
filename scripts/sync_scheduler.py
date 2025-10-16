#!/usr/bin/env python3
"""
Neo4j to Snowflake Sync Scheduler
Schedules periodic synchronization of graph data from Neo4j to Snowflake

Usage:
    python sync_scheduler.py --interval 3600  # Sync every hour
    python sync_scheduler.py --cron "0 * * * *"  # Use cron expression
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime, timedelta
from typing import Optional
import subprocess
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyncScheduler:
    """Scheduler for Neo4j to Snowflake sync jobs"""

    def __init__(self, interval_seconds: int = 3600):
        self.interval_seconds = interval_seconds
        self.running = False
        self.last_sync_time: Optional[datetime] = None
        self.next_sync_time: Optional[datetime] = None
        self.sync_count = 0

    def calculate_next_sync_time(self) -> datetime:
        """Calculate when the next sync should run"""
        if self.last_sync_time is None:
            # First sync - run immediately
            return datetime.now()
        else:
            # Schedule next sync based on interval
            return self.last_sync_time + timedelta(seconds=self.interval_seconds)

    def run_sync_job(self) -> bool:
        """Run the sync job and return success status"""
        try:
            logger.info("🚀 Starting scheduled sync job...")

            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sync_script = os.path.join(script_dir, "neo4j_snowflake_sync.py")

            # Run the sync script
            result = subprocess.run(
                [sys.executable, sync_script],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(script_dir)  # Run from project root
            )

            if result.returncode == 0:
                logger.info("✅ Sync job completed successfully")
                if result.stdout:
                    logger.info(f"📊 Sync output: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"❌ Sync job failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error output: {result.stderr.strip()}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to run sync job: {e}")
            return False

    def run_sync_cycle(self):
        """Run one complete sync cycle"""
        self.last_sync_time = datetime.now()
        self.sync_count += 1

        logger.info(f"🔄 Starting sync cycle #{self.sync_count}")

        success = self.run_sync_job()

        if success:
            logger.info(f"✅ Sync cycle #{self.sync_count} completed successfully")
        else:
            logger.error(f"❌ Sync cycle #{self.sync_count} failed")

        self.next_sync_time = self.calculate_next_sync_time()
        logger.info(f"📅 Next sync scheduled for: {self.next_sync_time}")

    def sleep_until_next_sync(self):
        """Sleep until the next sync is due"""
        if self.next_sync_time is None:
            return

        now = datetime.now()
        sleep_seconds = (self.next_sync_time - now).total_seconds()

        if sleep_seconds > 0:
            logger.info(f"😴 Sleeping for {sleep_seconds:.0f} seconds until next sync")
            time.sleep(sleep_seconds)
        else:
            logger.warning("⚠️ Next sync time is in the past, running immediately")

    def start_scheduler(self):
        """Start the scheduler loop"""
        logger.info("🎯 Starting Neo4j to Snowflake sync scheduler")
        logger.info(f"⏰ Sync interval: {self.interval_seconds} seconds ({self.interval_seconds/3600:.1f} hours)")

        # Validate environment
        self._validate_environment()

        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while self.running:
                # Run sync cycle
                self.run_sync_cycle()

                # Sleep until next cycle (unless this was the first run)
                if self.sync_count > 0:
                    self.sleep_until_next_sync()

        except KeyboardInterrupt:
            logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
        finally:
            logger.info(f"📊 Scheduler finished. Total syncs: {self.sync_count}")

    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping scheduler...")
        self.running = False

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.stop_scheduler()

    def _validate_environment(self):
        """Validate that required environment variables are set"""
        required_vars = [
            "SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD",
            "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"❌ Missing required environment variables: {missing_vars}")
            logger.error("Please set these variables before running the scheduler")
            sys.exit(1)

        logger.info("✅ Environment validation passed")

def parse_cron_expression(cron_expr: str) -> int:
    """Parse cron expression to seconds (simplified - only supports hourly)"""
    # This is a simplified cron parser
    # For production, consider using a proper cron parser library

    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("Invalid cron expression format")

    minute, hour, day, month, weekday = parts

    # Only support simple hourly schedules for now
    if minute == "0" and hour == "*" and day == "*" and month == "*" and weekday == "*":
        return 3600  # Every hour
    elif minute == "0" and hour.isdigit() and day == "*" and month == "*" and weekday == "*":
        return int(hour) * 3600  # Every N hours
    else:
        raise ValueError("Unsupported cron expression. Only hourly schedules supported.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Neo4j to Snowflake Sync Scheduler")
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Sync interval in seconds (default: 3600 = 1 hour)"
    )
    parser.add_argument(
        "--cron",
        type=str,
        help="Cron expression for sync schedule (e.g., '0 * * * *' for hourly)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run sync once and exit (don't schedule)"
    )

    args = parser.parse_args()

    # Determine interval
    interval_seconds = args.interval
    if args.cron:
        interval_seconds = parse_cron_expression(args.cron)
        logger.info(f"📅 Parsed cron expression '{args.cron}' as {interval_seconds} seconds interval")

    # Create scheduler
    scheduler = SyncScheduler(interval_seconds=interval_seconds)

    if args.once:
        # Run once and exit
        logger.info("🔄 Running sync job once...")
        scheduler.run_sync_cycle()
    else:
        # Start scheduler
        scheduler.start_scheduler()

if __name__ == "__main__":
    main()