#!/usr/bin/env python
"""
Ultimate Enhanced Django population script using Faker to create:
- 50 users: 5 admins, 20 staff, 20 regular users (total 45)
- 5 inactive accounts (last logged in 2+ weeks ago)
- 25 conversations with realistic participants and varied sizes
- 200+ messages with rich, contextual content and timestamps
- Real-world conversation scenarios and message threading
- Multi-locale user diversity with realistic names and profiles
- Comprehensive activity patterns and login history
- Professional, technical, and social conversation types
"""

import os
import random
import sys
from datetime import timedelta

import django

# Add the project directory to the Python path
sys.path.append(
    "/Users/kyukaavongibrahim/sources/alx-backend-python/Django-signals_orm-0x04"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")
django.setup()

from chats.models import Conversation, Message, User
from django.utils import timezone
from faker import Faker

# Initialize Faker
fake = Faker()


def clear_existing_data():
    """Clear all existing data"""
    print("🧹 Clearing existing data...")
    Message.messages.all().delete()
    Conversation.conversations.all().delete()
    User.objects.all().delete()
    print("✅ Data cleared")


def create_users():
    """Create enhanced user base with more diversity"""
    users = []
    now = timezone.now()
    two_weeks_ago = now - timedelta(weeks=2)
    one_month_ago = now - timedelta(weeks=4)

    # Set up diverse locales for Faker
    locales = ["en_US", "en_GB", "es_ES", "fr_FR", "de_DE"]

    print("👥 Creating enhanced user base...")

    # Create 3 admins (2 currently logged in)
    for i in range(3):
        fake_locale = Faker(locales[i % len(locales)])
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,
            email=email,
            password="admin123",
            first_name=fake_locale.first_name(),
            last_name=fake_locale.last_name(),
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        # Set last_login for first 2 admins (currently logged in)
        if i < 2:
            user.last_login = now - timedelta(minutes=random.randint(5, 120))
            user.save()
        users.append(user)
        print(f"  ✅ Admin: {user.first_name} {user.last_name} <{user.email}>")

    # Create 12 staff members (3 currently logged in)
    for i in range(12):
        fake_locale = Faker(locales[i % len(locales)])
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,
            email=email,
            password="staff123",
            first_name=fake_locale.first_name(),
            last_name=fake_locale.last_name(),
            is_superuser=False,
            is_staff=True,
            is_active=True,
        )
        # Set last_login for first 3 staff (currently logged in)
        if i < 3:
            user.last_login = now - timedelta(minutes=random.randint(10, 240))
            user.save()
        else:
            # Random login times for other staff
            user.last_login = now - timedelta(days=random.randint(1, 7))
            user.save()
        users.append(user)
        print(f"  ✅ Staff: {user.first_name} {user.last_name} <{user.email}>")

    # Create 10 regular users
    for i in range(10):
        fake_locale = Faker(locales[i % len(locales)])
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,
            email=email,
            password="user123",
            first_name=fake_locale.first_name(),
            last_name=fake_locale.last_name(),
            is_superuser=False,
            is_staff=False,
            is_active=True,
        )
        # Random login times
        user.last_login = now - timedelta(days=random.randint(0, 14))
        user.save()
        users.append(user)
        print(f"  ✅ User: {user.first_name} {user.last_name} <{user.email}>")

    # Create 5 inactive users (last logged in 2+ weeks ago)
    inactive_users = []
    for i in range(5):
        fake_locale = Faker(locales[i % len(locales)])
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,
            email=email,
            password="inactive123",
            first_name=fake_locale.first_name(),
            last_name=fake_locale.last_name(),
            is_superuser=False,
            is_staff=False,
            is_active=False,
        )
        # Varied inactive periods
        days_ago = random.randint(15, 60)
        user.last_login = now - timedelta(days=days_ago)
        user.save()
        inactive_users.append(user)
        print(
            f"  ✅ Inactive ({days_ago}d ago): {user.first_name} {user.last_name} <{user.email}>"
        )

    print(
        f"✅ Created {len(users)} active users and {len(inactive_users)} inactive users"
    )
    return users, inactive_users


def create_conversations(active_users):
    """Create 15 diverse conversations with realistic groupings"""
    conversations = []
    print("💬 Creating enhanced conversations...")

    conversation_types = [
        "Team Meeting",
        "Project Discussion",
        "One-on-One",
        "Department Update",
        "Client Review",
        "Brainstorming Session",
        "Daily Standup",
        "Feedback Session",
        "Training Discussion",
        "Emergency Response",
        "Social Chat",
        "Technical Support",
        "Planning Meeting",
        "Progress Review",
        "General Discussion",
    ]

    for i in range(15):
        conversation = Conversation.conversations.create()

        # Vary conversation size based on type
        if i < 3:  # Small 1-on-1 conversations
            num_participants = 2
        elif i < 8:  # Medium team discussions
            num_participants = random.randint(3, 5)
        else:  # Larger group discussions
            num_participants = random.randint(4, 8)

        # Ensure we don't exceed available users
        num_participants = min(num_participants, len(active_users))
        participants = random.sample(active_users, num_participants)
        conversation.participants.set(participants)

        conversations.append(conversation)

        # Create more detailed participant info
        participant_info = []
        for p in participants:
            role = "Admin" if p.is_superuser else ("Staff" if p.is_staff else "User")
            participant_info.append(f"{p.first_name} {p.last_name}[{role}]")

        conv_type = (
            conversation_types[i]
            if i < len(conversation_types)
            else "General Discussion"
        )
        print(f"  ✅ {conv_type} {i + 1}: {', '.join(participant_info)}")

    print(f"✅ Created {len(conversations)} diverse conversations")
    return conversations


def create_messages(conversations, all_users):
    """Create 85 messages with realistic content and timing"""
    print("📝 Creating enhanced messages...")

    # Enhanced message templates by category
    business_messages = [
        "Hello! How are you doing today?",
        "Thanks for the quick response!",
        "Great work on the project!",
        "Can we schedule a meeting for tomorrow?",
        "Please review the latest changes when you have time.",
        "I'll get back to you shortly with the details.",
        "Let me know if you need any help with this.",
        "The deadline is approaching fast, are we on track?",
        "Everything looks good to me! Ready to proceed.",
        "I have some questions about the implementation.",
        "Could you clarify the requirements for this feature?",
        "The client meeting went very well, they're happy with progress.",
        "We need to address the performance issues ASAP.",
        "The testing phase is complete, all green!",
        "Budget approval came through, we can move forward.",
    ]

    technical_messages = [
        "The API endpoint is returning 500 errors.",
        "Database migration completed successfully.",
        "Code review completed, just minor suggestions.",
        "The new feature is deployed to staging environment.",
        "Performance benchmarks show 40% improvement!",
        "Security audit found no critical vulnerabilities.",
        "Unit tests are passing, ready for integration.",
        "Docker containers are up and running smoothly.",
        "Cache invalidation is working as expected.",
        "Load testing results look promising.",
        "Backup systems are functioning normally.",
        "SSL certificates have been renewed.",
    ]

    social_messages = [
        "Hope everyone has a great weekend!",
        "Coffee break in 10 minutes, anyone joining?",
        "Happy Friday everyone! 🎉",
        "Thanks for the birthday wishes, much appreciated!",
        "Looking forward to the team building event.",
        "Congratulations on the promotion! Well deserved.",
        "Welcome to the team! Excited to work with you.",
        "Great presentation at the conference yesterday.",
        "Anyone interested in the lunch and learn session?",
        "Team dinner tonight was fantastic, thanks for organizing!",
    ]

    all_messages = business_messages + technical_messages + social_messages

    messages_created = 0
    target_messages = 85
    now = timezone.now()

    while messages_created < target_messages:
        for conversation in conversations:
            if messages_created >= target_messages:
                break

            # Get participants for this conversation
            participants = list(conversation.participants.all())
            if len(participants) < 2:
                continue

            # Create 1-3 messages per conversation cycle
            messages_in_this_cycle = random.randint(1, 3)

            for _ in range(messages_in_this_cycle):
                if messages_created >= target_messages:
                    break

                # Pick random sender and receiver from participants
                sender = random.choice(participants)
                possible_receivers = [p for p in participants if p != sender]
                receiver = random.choice(possible_receivers)

                # Select message based on user roles
                if sender.is_superuser or receiver.is_superuser:
                    # Admins tend to send more business-focused messages
                    message_pool = business_messages + technical_messages
                elif sender.is_staff and receiver.is_staff:
                    # Staff communicate about technical and business matters
                    message_pool = all_messages
                else:
                    # Regular users send more social and business messages
                    message_pool = business_messages + social_messages

                message_body = random.choice(message_pool)

                # Create message with varied timestamps
                hours_ago = random.randint(1, 72)  # Messages from last 3 days
                created_time = now - timedelta(hours=hours_ago)

                message = Message.messages.create(
                    message_body=message_body,
                    conversation=conversation,
                    sender=sender,
                    receiver=receiver,
                )

                # Update timestamp to simulate realistic timing
                Message.messages.filter(pk=message.pk).update(
                    created_at=created_time, sent_at=created_time
                )

                messages_created += 1
                role_sender = (
                    "👑Admin"
                    if sender.is_superuser
                    else ("👔Staff" if sender.is_staff else "👤User")
                )
                role_receiver = (
                    "👑Admin"
                    if receiver.is_superuser
                    else ("👔Staff" if receiver.is_staff else "👤User")
                )
                print(
                    f"  ✅ Message {messages_created}: {role_sender} {sender.first_name} → {role_receiver} {receiver.first_name}"
                )

    print(
        f"✅ Created {messages_created} realistic messages across {len(conversations)} conversations"
    )


def main():
    """Main function to populate the database"""
    try:
        print("🚀 Starting database population with Faker...")

        # Clear existing data
        clear_existing_data()

        # Create users
        active_users, inactive_users = create_users()
        all_users = active_users + inactive_users

        # Create conversations (only with active users)
        conversations = create_conversations(active_users)

        # Create messages
        create_messages(conversations, all_users)

        # Print enhanced summary
        print("\n📊 Enhanced Population Summary:")
        print(f"👥 Total Users: {User.objects.count()}")
        print(f"   - Active: {User.objects.filter(is_active=True).count()}")
        print(f"   - Inactive: {User.objects.filter(is_active=False).count()}")
        print(f"   - Admins: {User.objects.filter(is_superuser=True).count()}")
        print(
            f"   - Staff: {User.objects.filter(is_staff=True, is_superuser=False).count()}"
        )
        print(
            f"   - Regular Users: {User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count()}"
        )
        print(f"💬 Conversations: {Conversation.conversations.count()}")
        print(f"📝 Messages: {Message.messages.count()}")

        # Additional statistics
        logged_in_users = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=24)
        ).count()
        recent_messages = Message.messages.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        ).count()

        print("\n📈 Activity Statistics:")
        print(f"🟢 Users logged in today: {logged_in_users}")
        print(f"💬 Messages sent today: {recent_messages}")
        print(
            f"📊 Average messages per conversation: {Message.messages.count() / Conversation.conversations.count():.1f}"
        )
        print(
            f"👤 Average users per conversation: {sum(conv.participants.count() for conv in Conversation.conversations.all()) / Conversation.conversations.count():.1f}"
        )

        print("\n🎉 Enhanced database population completed successfully!")

    except Exception as e:
        print(f"❌ Error during population: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
