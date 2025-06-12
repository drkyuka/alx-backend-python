#!/usr/bin/env python
"""
Master Test Runner for Django-signals_orm-0x04
==============================================

This script runs all test and validation scripts in the utility folder.
It provides a comprehensive test suite for the entire Django project.
"""

import os
import subprocess
import sys
from datetime import datetime

# Add the project directory to the Python path
PROJECT_ROOT = (
    "/Users/kyukaavongibrahim/sources/alx-backend-python/Django-signals_orm-0x04"
)
sys.path.append(PROJECT_ROOT)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")

import django

django.setup()


def run_script(script_name, description):
    """Run a utility script and return success status."""
    print(f"\n{'=' * 60}")
    print(f"🔍 RUNNING: {description}")
    print(f"{'=' * 60}")

    script_path = os.path.join(PROJECT_ROOT, "utility", script_name)

    try:
        if not os.path.exists(script_path):
            print(f"❌ SKIPPED: {script_name} not found")
            return False

        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED: {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False

    except Exception as e:
        print(f"❌ ERROR running {script_name}: {e}")
        return False


def check_database_status():
    """Check if database is populated."""
    try:
        from chats.models import Conversation, Message, User

        user_count = User.objects.count()
        message_count = Message.messages.count()
        conversation_count = Conversation.conversations.count()

        print("\n📊 DATABASE STATUS")
        print(f"{'=' * 30}")
        print(f"Users: {user_count}")
        print(f"Messages: {message_count}")
        print(f"Conversations: {conversation_count}")

        if user_count == 0:
            print("\n⚠️  DATABASE EMPTY - Consider running populate_ultimate.py first")
            return False
        else:
            print("\n✅ DATABASE POPULATED")
            return True

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False


def main():
    """Run all test and validation scripts."""
    print("🚀 DJANGO-SIGNALS_ORM-0X04 MASTER TEST RUNNER")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {PROJECT_ROOT}")

    # Check database status
    db_populated = check_database_status()

    # Define test scripts to run
    test_scripts = [
        ("test_serializers_comprehensive.py", "Comprehensive Serializer Validation"),
        ("validate_views.py", "Django Views Validation"),
        ("api_endpoint_validation_enhanced.py", "Enhanced API Endpoint Testing"),
        ("serializer_validation_report.py", "Generate Validation Report"),
    ]

    # Optional data population if database is empty
    if not db_populated:
        print(f"\n{'=' * 60}")
        print("🔄 DATABASE SETUP REQUIRED")
        print(f"{'=' * 60}")
        print("Database appears to be empty. Running data population first...")

        populate_success = run_script(
            "populate_ultimate.py", "Ultimate Data Population"
        )
        if not populate_success:
            print("❌ Failed to populate database. Some tests may fail.")

    # Run all test scripts
    results = []
    for script_name, description in test_scripts:
        success = run_script(script_name, description)
        results.append((script_name, description, success))

    # Generate summary report
    print(f"\n{'=' * 60}")
    print("📊 TEST EXECUTION SUMMARY")
    print(f"{'=' * 60}")

    passed = sum(1 for _, _, success in results if success)
    total = len(results)

    for script_name, description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description:<40} {status}")

    print(f"\n{'=' * 60}")
    print(f"TOTAL TESTS: {total}")
    print(f"PASSED: {passed}")
    print(f"FAILED: {total - passed}")
    print(f"SUCCESS RATE: {(passed / total * 100):.1f}%")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! PROJECT IS PRODUCTION READY!")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED. REVIEW OUTPUT ABOVE.")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
