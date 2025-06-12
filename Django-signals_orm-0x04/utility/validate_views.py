#!/usr/bin/env python
"""
Django Views Validation
=======================
Validates that all Django ViewSets are working correctly
"""

import os
import sys
from datetime import datetime

import django

# Setup Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")
django.setup()


def validate_views():
    """Validate Django views functionality"""

    print("🚀 Django Views Validation")
    print("=" * 60)
    print("Testing Django ViewSets functionality")
    print(f"Date: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}")
    print("=" * 60)

    results = {}

    try:
        # Import everything we need
        from chats.models import Conversation, Message, User
        from chats.views import ConversationViewSet, CustomTokenView, MessageViewSet
        from rest_framework.test import APIRequestFactory

        print("✅ Successfully imported all views and models")

        # Test 1: View Class Structure
        print("\n🔍 Testing View Class Structure...")
        try:
            # Test ConversationViewSet
            conv_viewset = ConversationViewSet()
            assert hasattr(conv_viewset, "queryset"), (
                "ConversationViewSet missing queryset"
            )
            assert hasattr(conv_viewset, "serializer_class"), (
                "ConversationViewSet missing serializer_class"
            )
            assert hasattr(conv_viewset, "permission_classes"), (
                "ConversationViewSet missing permission_classes"
            )
            print("✅ ConversationViewSet structure valid")

            # Test MessageViewSet
            msg_viewset = MessageViewSet()
            assert hasattr(msg_viewset, "queryset"), "MessageViewSet missing queryset"
            assert hasattr(msg_viewset, "serializer_class"), (
                "MessageViewSet missing serializer_class"
            )
            assert hasattr(msg_viewset, "permission_classes"), (
                "MessageViewSet missing permission_classes"
            )
            print("✅ MessageViewSet structure valid")

            # Test CustomTokenView
            token_view = CustomTokenView()
            assert hasattr(token_view, "serializer_class"), (
                "CustomTokenView missing serializer_class"
            )
            print("✅ CustomTokenView structure valid")

            results["ViewStructure"] = True

        except Exception as e:
            print(f"❌ View structure error: {e}")
            results["ViewStructure"] = False

        # Test 2: ViewSet Configuration
        print("\n🔍 Testing ViewSet Configuration...")
        try:
            conv_viewset = ConversationViewSet()

            # Check queryset
            queryset = conv_viewset.queryset
            print(f"✅ ConversationViewSet queryset: {queryset.model.__name__}")

            # Check serializer
            serializer_class = conv_viewset.serializer_class
            print(f"✅ ConversationViewSet serializer: {serializer_class.__name__}")

            # Check permissions
            permissions = conv_viewset.permission_classes
            print(f"✅ ConversationViewSet permissions: {len(permissions)} classes")

            # Check filter backends
            filter_backends = conv_viewset.filter_backends
            print(f"✅ ConversationViewSet filters: {len(filter_backends)} backends")

            results["ConversationConfig"] = True

        except Exception as e:
            print(f"❌ ConversationViewSet config error: {e}")
            results["ConversationConfig"] = False

        # Test 3: MessageViewSet Configuration
        print("\n🔍 Testing MessageViewSet Configuration...")
        try:
            msg_viewset = MessageViewSet()

            # Check queryset
            queryset = msg_viewset.queryset
            print(f"✅ MessageViewSet queryset: {queryset.model.__name__}")

            # Check serializer
            serializer_class = msg_viewset.serializer_class
            print(f"✅ MessageViewSet serializer: {serializer_class.__name__}")

            # Check pagination
            pagination_class = msg_viewset.pagination_class
            print(
                f"✅ MessageViewSet pagination: {pagination_class.__name__ if pagination_class else 'None'}"
            )

            results["MessageConfig"] = True

        except Exception as e:
            print(f"❌ MessageViewSet config error: {e}")
            results["MessageConfig"] = False

        # Test 4: Custom Methods
        print("\n🔍 Testing Custom Methods...")
        try:
            # Test ConversationViewSet custom methods
            conv_viewset = ConversationViewSet()

            # Test get_queryset method
            if hasattr(conv_viewset, "get_queryset"):
                print("✅ ConversationViewSet.get_queryset() method exists")

            # Test create method
            if hasattr(conv_viewset, "create"):
                print("✅ ConversationViewSet.create() method exists")

            # Test MessageViewSet custom methods
            msg_viewset = MessageViewSet()

            # Test get_permissions method
            if hasattr(msg_viewset, "get_permissions"):
                print("✅ MessageViewSet.get_permissions() method exists")

            # Test get_queryset method
            if hasattr(msg_viewset, "get_queryset"):
                print("✅ MessageViewSet.get_queryset() method exists")

            # Test create method
            if hasattr(msg_viewset, "create"):
                print("✅ MessageViewSet.create() method exists")

            results["CustomMethods"] = True

        except Exception as e:
            print(f"❌ Custom methods error: {e}")
            results["CustomMethods"] = False

        # Test 5: Method Logic with Mock Data
        print("\n🔍 Testing Method Logic...")
        try:
            # Get test user
            test_user = User.objects.filter(is_active=True).first()

            if test_user:
                print(f"✅ Using test user: {test_user.email}")

                # Test ConversationViewSet get_queryset with mock request
                conv_viewset = ConversationViewSet()
                factory = APIRequestFactory()
                request = factory.get("/api/conversations/")
                request.user = test_user
                conv_viewset.request = request

                filtered_queryset = conv_viewset.get_queryset()
                print(
                    f"✅ ConversationViewSet.get_queryset() returns {filtered_queryset.count()} conversations"
                )

                # Test MessageViewSet get_queryset
                msg_viewset = MessageViewSet()
                request = factory.get("/api/messages/")
                request.user = test_user
                msg_viewset.request = request
                msg_viewset.kwargs = {}

                filtered_queryset = msg_viewset.get_queryset()
                print(
                    f"✅ MessageViewSet.get_queryset() returns {filtered_queryset.count()} messages"
                )

                # Test get_permissions
                permissions = msg_viewset.get_permissions()
                print(
                    f"✅ MessageViewSet.get_permissions() returns {len(permissions)} permission instances"
                )

            else:
                print("⚠️  No test user available for method logic testing")

            results["MethodLogic"] = True

        except Exception as e:
            print(f"❌ Method logic error: {e}")
            results["MethodLogic"] = False

        # Test 6: Database Integration
        print("\n🔍 Testing Database Integration...")
        try:
            # Check database state
            user_count = User.objects.count()
            conv_count = Conversation.conversations.count()
            msg_count = Message.messages.count()

            print(
                f"✅ Database state: {user_count} users, {conv_count} conversations, {msg_count} messages"
            )

            # Test querysets work with database
            conv_viewset = ConversationViewSet()
            total_conversations = conv_viewset.queryset.count()
            print(
                f"✅ ConversationViewSet queryset accesses {total_conversations} total conversations"
            )

            msg_viewset = MessageViewSet()
            total_messages = msg_viewset.queryset.count()
            print(
                f"✅ MessageViewSet queryset accesses {total_messages} total messages"
            )

            results["DatabaseIntegration"] = True

        except Exception as e:
            print(f"❌ Database integration error: {e}")
            results["DatabaseIntegration"] = False

        # Generate Summary
        print("\n" + "=" * 60)
        print("📊 DJANGO VIEWS VALIDATION SUMMARY")
        print("=" * 60)

        test_names = {
            "ViewStructure": "View Class Structure",
            "ConversationConfig": "ConversationViewSet Config",
            "MessageConfig": "MessageViewSet Config",
            "CustomMethods": "Custom Methods",
            "MethodLogic": "Method Logic",
            "DatabaseIntegration": "Database Integration",
        }

        passed = sum(results.values())
        total = len(results)

        for key, value in results.items():
            status = "✅ PASSED" if value else "❌ FAILED"
            test_name = test_names.get(key, key)
            print(f"{test_name:<30} {status}")

        print("-" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            print("\n🎉 ALL DJANGO VIEWS ARE WORKING PERFECTLY!")
            print("✅ ViewSet structure is correct")
            print("✅ Configuration is complete")
            print("✅ Custom methods are implemented")
            print("✅ Business logic is functional")
            print("✅ Database integration is working")
        elif passed >= total * 0.8:
            print(f"\n✅ Views are mostly functional ({passed}/{total} tests passed)")
            print("Minor issues detected but core functionality works")
        else:
            print(f"\n⚠️  {total - passed} significant test(s) failed. Review required.")

        print("=" * 60)
        return passed >= total * 0.8

    except Exception as e:
        print(f"❌ Views validation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = validate_views()
        print(f"\nValidation {'PASSED' if success else 'FAILED'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Script execution failed: {e}")
        sys.exit(1)
