import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from chats.models import User, Conversation, Message

FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones"]


class Command(BaseCommand):
    help = "Seed the database with users, conversations, and messages for chats app."

    def handle(self, *args, **options):
        # Clear existing data
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        User.objects.all().delete()

        # Create 5 users
        users = []
        for i in range(5):
            user = User.objects.create(
                email=f"user{i + 1}@example.com",
                password="testpassword",
                first_name=FIRST_NAMES[i % len(FIRST_NAMES)],
                last_name=LAST_NAMES[i % len(LAST_NAMES)],
                phone_number=f"555-000{i + 1}",
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users."))

        # Create 12 conversations, each with 2-4 random participants
        conversations = []
        for i in range(12):
            convo = Conversation.objects.create()
            num_participants = random.randint(2, 4)
            participants = random.sample(users, num_participants)
            convo.participants.add(*participants)
            conversations.append((convo, participants))
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(conversations)} conversations.")
        )

        # Create 50 messages distributed among conversations
        messages = []
        for i in range(50):
            convo, participants = random.choice(conversations)
            sender, receiver = random.sample(participants, 2)
            msg = Message.objects.create(
                message_body=f"Message {i + 1} from {sender.first_name} to {receiver.first_name}",
                conversation=convo,
                sender=sender,
                receiver=receiver,
                sent_at=timezone.now(),
                created_at=timezone.now(),
            )
            messages.append(msg)
        self.stdout.write(self.style.SUCCESS(f"Created {len(messages)} messages."))
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
