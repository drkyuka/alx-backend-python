#!/usr/bin/env python
"""
Django population script using Faker to create:
- 11 users: 2 admins, 7 staf    # Create 3 inactive users (last logged in 2 weeks ago)
    inactive_users = []
    for i in range(3):
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password="inactive123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=False,
            is_staff=False,
            is_active=False,  # Inactive
            last_login=two_weeks_ago,
        )users (total 11)
- 3 inactive accounts (last logged in 2 weeks ago)
- 9 conversations with random participants
- 37 messages between users
- 1 admin and 1 staff currently logged in
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Add the project directory to the Python path
sys.path.append(
    "/Users/kyukaavongibrahim/sources/alx-backend-python/Django-signals_orm-0x04"
)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django-signals_orm-0x04.settings")
django.setup()

from faker import Faker
from django.utils import timezone
from chats.models import User, Conversation, Message

# Initialize Faker
fake = Faker()


def populate_users():
    """Create 11 active users + 3 inactive users"""
    users = []
    now = timezone.now()
    two_weeks_ago = now - timedelta(weeks=2)

    print("Creating users...")

    # Create 2 admins (superusers)
    for i in range(2):
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password="admin123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=True,
            is_staff=True,
            is_active=True,
            last_login=now
            if i == 0
            else fake.date_time_between(
                start_date="-30d", end_date="now", tzinfo=timezone.utc
            ),
        )
        users.append(user)
        print(f"Created admin: {user.email}")

    # Create 7 staff users
    for i in range(7):
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password="staff123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=False,
            is_staff=True,
            is_active=True,
            last_login=now
            if i == 0
            else fake.date_time_between(
                start_date="-7d", end_date="now", tzinfo=timezone.utc
            ),
        )
        users.append(user)
        print(f"Created staff: {user.email}")

    # Create 2 regular active users
    for i in range(2):
        email = fake.unique.email()
        user = User.objects.create_user(
            username=email,  # Use email as username
            email=email,
            password="user123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=False,
            is_staff=False,
            is_active=True,
            last_login=fake.date_time_between(
                start_date="-3d", end_date="now", tzinfo=timezone.utc
            ),
        )
        users.append(user)
        print(f"Created regular user: {user.email}")

    # Create 3 inactive users (last logged in 2 weeks ago)
    inactive_users = []
    for i in range(3):
        user = User.objects.create_user(
            email=fake.unique.email(),
            password="inactive123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            is_superuser=False,
            is_staff=False,
            is_active=False,
            last_login=two_weeks_ago,
        )
        inactive_users.append(user)
        print(f"Created inactive user: {user.email}")

    return users, inactive_users


def populate_conversations(all_users):
    """Create 9 conversations with random participants"""
    conversations = []

    print("\nCreating conversations...")

    for i in range(9):
        # Create conversation
        conversation = Conversation.objects.create()

        # Add 2-4 random participants to each conversation
        num_participants = random.randint(2, 4)
        participants = random.sample(all_users, num_participants)

        conversation.participants.set(participants)
        conversations.append(conversation)

        participant_emails = [p.email for p in participants]
        print(f"Created conversation {i + 1} with participants: {participant_emails}")

    return conversations


def populate_messages(conversations, all_users):
    """Create 37 messages distributed among conversations"""
    print("\nCreating messages...")

    message_bodies = [
        "Hello! How are you doing today?",
        "Thanks for the quick response!",
        "Can we schedule a meeting for tomorrow?",
        "Great work on the project!",
        "I'll get back to you shortly.",
        "The document has been updated.",
        "Please review the latest changes.",
        "Looking forward to our collaboration.",
        "Have a great weekend!",
        "Let me know if you need any help.",
        "The deadline is approaching fast.",
        "Could you please clarify this point?",
        "Excellent presentation yesterday!",
        "I've shared the files with you.",
        "The meeting went really well.",
        "Thanks for your patience.",
        "I'll handle this right away.",
        "Please confirm your availability.",
        "The system is working perfectly now.",
        "Great job on solving that issue!",
        "I'm currently working on it.",
        "Could we reschedule for next week?",
        "The report is almost ready.",
        "Thanks for the detailed feedback.",
        "I'll send you the updated version.",
        "The project is on track.",
        "Let's discuss this in detail.",
        "I've completed the task.",
        "The team meeting is at 3 PM.",
        "Please check your email.",
        "I'm available for a call.",
        "The issue has been resolved.",
        "Thanks for bringing this up.",
        "I'll review it by end of day.",
        "The presentation looks great!",
        "Can you send me the file?",
        "I'll be there in 10 minutes.",
    ]

    for i in range(37):
        # Pick a random conversation
        conversation = random.choice(conversations)
        participants = list(conversation.participants.all())

        # Pick sender and receiver from conversation participants
        if len(participants) >= 2:
            sender = random.choice(participants)
            # Make sure receiver is different from sender
            possible_receivers = [p for p in participants if p != sender]
            receiver = random.choice(possible_receivers)

            # Create message with realistic content
            message_body = (
                random.choice(message_bodies)
                if i < len(message_bodies)
                else fake.text(max_nb_chars=200)
            )

            message = Message.objects.create(
                message_body=message_body,
                conversation=conversation,
                sender=sender,
                receiver=receiver,
            )

            print(f"Created message {i + 1}: {sender.email} -> {receiver.email}")

    print(f"\nCreated {Message.objects.count()} messages in total.")


def main():
    """Main function to populate all data"""
    print("🚀 Starting database population with Faker...")

    # Clear existing data
    print("\nClearing existing data...")
    Message.objects.all().delete()
    Conversation.objects.all().delete()
    User.objects.all().delete()

    try:
        # Create users
        active_users, inactive_users = populate_users()
        all_users = active_users + inactive_users

        # Create conversations
        conversations = populate_conversations(
            active_users
        )  # Only active users in conversations

        # Create messages
        populate_messages(conversations, active_users)

        # Print summary
        print("\n" + "=" * 50)
        print("📊 POPULATION SUMMARY")
        print("=" * 50)
        print(f"👥 Total Users: {User.objects.count()}")
        print(
            f"   - Admins (superuser): {User.objects.filter(is_superuser=True).count()}"
        )
        print(
            f"   - Staff: {User.objects.filter(is_staff=True, is_superuser=False).count()}"
        )
        print(
            f"   - Regular users: {User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count()}"
        )
        print(f"   - Inactive users: {User.objects.filter(is_active=False).count()}")
        print(f"💬 Conversations: {Conversation.objects.count()}")
        print(f"📨 Messages: {Message.objects.count()}")

        # Show currently logged in users
        now = timezone.now()
        recently_logged_in = User.objects.filter(
            last_login__gte=now - timedelta(hours=1)
        )
        print(f"🟢 Currently logged in users: {recently_logged_in.count()}")
        for user in recently_logged_in:
            role = (
                "Admin" if user.is_superuser else "Staff" if user.is_staff else "User"
            )
            print(f"   - {user.email} ({role})")

        print("\n✅ Database population completed successfully!")

    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
