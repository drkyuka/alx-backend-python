#!/usr/bin/env python
"""
Ultimate Enhanced Django population script using Faker to create:
- 50 users: 5 admins, 20 staff, 20 regular users, 5 inactive (total 50)
- 25 conversations with realistic participants and varied sizes
- 250+ messages with rich, contextual content and timestamps
- Real-world conversation scenarios and message threading
- Multi-locale user diversity with realistic names and profiles
- Comprehensive activity patterns and login history
- Professional, technical, and social conversation types
- Industry-specific jargon and realistic business communications
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

# Initialize Faker with multiple locales
fake = Faker()


def clear_existing_data():
    """Clear all existing data"""
    print("🧹 Clearing existing data...")
    Message.messages.all().delete()
    Conversation.conversations.all().delete()
    User.objects.all().delete()
    print("✅ Data cleared")


def create_enhanced_users():
    """Create comprehensive user base with maximum diversity"""
    users = []
    now = timezone.now()

    # Extended locales for maximum diversity
    locales = [
        "en_US",
        "en_GB",
        "es_ES",
        "fr_FR",
        "de_DE",
        "it_IT",
        "ja_JP",
        "ko_KR",
        "pt_BR",
        "zh_CN",
    ]

    # Job titles for realistic profiles
    admin_titles = [
        "CEO",
        "CTO",
        "VP Engineering",
        "Director of Operations",
        "Chief Architect",
    ]
    staff_titles = [
        "Senior Software Engineer",
        "Product Manager",
        "DevOps Engineer",
        "UX Designer",
        "Data Scientist",
        "QA Engineer",
        "Technical Lead",
        "Scrum Master",
        "Business Analyst",
        "Security Specialist",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Mobile Developer",
        "Database Administrator",
        "Solutions Architect",
        "Project Manager",
        "Marketing Manager",
        "Sales Engineer",
        "Support Lead",
    ]
    user_titles = [
        "Junior Developer",
        "Intern",
        "Trainee",
        "Content Creator",
        "Customer Support",
        "Sales Representative",
        "Marketing Assistant",
        "Operations Coordinator",
        "HR Specialist",
        "Finance Analyst",
    ]

    print("👥 Creating ultimate user base...")

    # Create 5 admins (3 currently logged in)
    for i in range(5):
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
        # Set varied login times for admins
        if i < 3:
            user.last_login = now - timedelta(minutes=random.randint(5, 180))
        else:
            user.last_login = now - timedelta(hours=random.randint(1, 12))
        user.save()
        users.append(user)
        title = admin_titles[i % len(admin_titles)]
        print(
            f"  ✅ Admin ({title}): {user.first_name} {user.last_name} <{user.email}>"
        )

    # Create 20 staff members (8 currently logged in)
    for i in range(20):
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
        # Varied login patterns for staff
        if i < 8:
            user.last_login = now - timedelta(minutes=random.randint(10, 300))
        else:
            user.last_login = now - timedelta(days=random.randint(1, 10))
        user.save()
        users.append(user)
        title = staff_titles[i % len(staff_titles)]
        print(
            f"  ✅ Staff ({title}): {user.first_name} {user.last_name} <{user.email}>"
        )

    # Create 20 regular users (5 currently logged in)
    for i in range(20):
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
        # Login patterns for regular users
        if i < 5:
            user.last_login = now - timedelta(minutes=random.randint(30, 480))
        else:
            user.last_login = now - timedelta(days=random.randint(1, 20))
        user.save()
        users.append(user)
        title = user_titles[i % len(user_titles)]
        print(f"  ✅ User ({title}): {user.first_name} {user.last_name} <{user.email}>")

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
        days_ago = random.randint(15, 90)
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


def create_enhanced_conversations(active_users):
    """Create 25 diverse conversations with realistic business scenarios"""
    conversations = []
    print("💬 Creating enhanced conversations...")

    # Extended conversation scenarios
    conversation_scenarios = [
        ("Sprint Planning Meeting", 4, 8),
        ("Code Review Session", 2, 4),
        ("Client Feedback Discussion", 3, 6),
        ("Product Roadmap Planning", 5, 10),
        ("Emergency Bug Triage", 3, 7),
        ("New Feature Brainstorming", 4, 8),
        ("Performance Optimization", 2, 5),
        ("Security Vulnerability Review", 3, 6),
        ("Design System Updates", 3, 5),
        ("API Documentation Review", 2, 4),
        ("Database Migration Planning", 3, 6),
        ("User Research Findings", 4, 7),
        ("Marketing Campaign Strategy", 3, 8),
        ("Sales Pipeline Review", 4, 6),
        ("Customer Support Escalation", 2, 5),
        ("Team Building Ideas", 5, 12),
        ("Remote Work Setup", 3, 6),
        ("Training Session Feedback", 4, 8),
        ("Budget Planning Discussion", 3, 5),
        ("Vendor Evaluation Meeting", 3, 7),
        ("Compliance Review", 2, 4),
        ("Innovation Lab Project", 4, 6),
        ("Intern Mentorship Program", 3, 8),
        ("Office Space Planning", 5, 10),
        ("Technology Stack Evaluation", 3, 6),
    ]

    for i, (scenario_name, min_participants, max_participants) in enumerate(
        conversation_scenarios
    ):
        conversation = Conversation.conversations.create()

        # Determine number of participants based on scenario
        num_participants = random.randint(
            min_participants, min(max_participants, len(active_users))
        )

        # Smart participant selection based on scenario
        if "Emergency" in scenario_name or "Security" in scenario_name:
            # Include more admins and senior staff
            admins = [u for u in active_users if u.is_superuser]
            staff = [u for u in active_users if u.is_staff and not u.is_superuser]
            regular = [u for u in active_users if not u.is_staff]
            participants = (
                random.sample(admins, min(2, len(admins)))
                + random.sample(staff, min(num_participants - 2, len(staff)))
            )[:num_participants]
        elif "Client" in scenario_name or "Sales" in scenario_name:
            # Include mix of business-focused people
            staff = [u for u in active_users if u.is_staff]
            participants = random.sample(staff, min(num_participants, len(staff)))
        else:
            # General mix for other scenarios
            participants = random.sample(active_users, num_participants)

        conversation.participants.set(participants)
        conversations.append(conversation)

        # Create detailed participant info
        participant_info = []
        for p in participants:
            role = (
                "👑Admin" if p.is_superuser else ("👔Staff" if p.is_staff else "👤User")
            )
            participant_info.append(f"{role} {p.first_name} {p.last_name}")

        print(f"  ✅ {scenario_name}: {', '.join(participant_info)}")

    print(f"✅ Created {len(conversations)} realistic business conversations")
    return conversations


def create_ultimate_messages(conversations, all_users):
    """Create 250+ messages with ultra-realistic content"""
    print("📝 Creating ultimate message collection...")

    # Comprehensive message categories with industry-specific content
    executive_messages = [
        "Board meeting scheduled for next Thursday at 2 PM",
        "Q4 revenue targets are looking achievable with current projections",
        "Strategic partnership discussions with TechCorp are progressing well",
        "Annual performance reviews should be completed by month-end",
        "New office lease agreement has been finalized",
        "Company-wide all-hands meeting announcement going out tomorrow",
        "Investor presentation slides need final review by COO",
        "Merger and acquisition talks are confidential - please maintain discretion",
        "Executive compensation committee meeting moved to Friday",
        "Market research data shows positive trends in our sector",
    ]

    engineering_messages = [
        "Kubernetes deployment successful on staging environment",
        "Database migration rollback plan needs approval",
        "CI/CD pipeline optimization reduced build time by 35%",
        "Memory leak identified in user authentication service",
        "New microservice architecture documentation is ready for review",
        "Redis cache configuration updated for better performance",
        "GraphQL endpoint rate limiting implementation complete",
        "Docker container security scan revealed 3 medium vulnerabilities",
        "Load balancer health checks failing intermittently",
        "API versioning strategy proposal attached for team review",
        "PostgreSQL query optimization reduced response time to 120ms",
        "Terraform infrastructure as code templates are production-ready",
        "WebSocket connection pool exhaustion causing 503 errors",
        "Machine learning model accuracy improved to 94.2%",
        "Elasticsearch index corruption detected in logs cluster",
        "OAuth 2.0 implementation passes security penetration tests",
        "Automated testing coverage increased to 87% across codebase",
        "Service mesh implementation with Istio showing promise",
        "Event-driven architecture migration timeline needs adjustment",
        "Zero-downtime deployment strategy tested successfully",
    ]

    product_messages = [
        "User engagement metrics show 23% increase this quarter",
        "A/B testing results favor the new checkout flow design",
        "Customer feedback analysis reveals top 3 feature requests",
        "Product roadmap priorities shifted based on market research",
        "Conversion rate optimization experiment yielded 15% improvement",
        "User persona research interviews scheduled for next week",
        "Feature flag rollout at 50% traffic with positive signals",
        "Product-market fit survey responses trending very positive",
        "Competitive analysis document shared with stakeholders",
        "Customer journey mapping workshop scheduled for Thursday",
        "Product analytics dashboard shows declining churn rate",
        "User story prioritization workshop went well today",
        "MVP feature set finalized for Q1 release cycle",
        "Customer success team reports 94% satisfaction score",
        "Product requirements document (PRD) ready for engineering review",
    ]

    operations_messages = [
        "Server maintenance window scheduled for Sunday 2-4 AM",
        "Data backup verification completed successfully",
        "Network latency issues resolved in European data center",
        "SSL certificate renewal automated for all domains",
        "Monitoring alerts reduced by 40% after threshold adjustments",
        "Disaster recovery drill scheduled for next Friday",
        "CDN cache hit ratio improved to 96% after optimization",
        "Database connection pooling configuration needs review",
        "Log aggregation system processing 2TB daily without issues",
        "Application performance monitoring shows 99.98% uptime",
        "Infrastructure cost optimization saved $12K monthly",
        "Security incident response time averaged 8 minutes last month",
        "Automated scaling policies working effectively under load",
        "Service level agreement metrics exceeded targets again",
        "Backup retention policy updated per compliance requirements",
    ]

    business_messages = [
        "Client presentation went exceptionally well this morning",
        "Sales pipeline review shows strong Q4 prospects",
        "Marketing campaign ROI exceeded expectations by 120%",
        "Customer acquisition cost decreased 18% month-over-month",
        "Partnership agreement with startup accelerator signed",
        "Trade conference booth setup confirmed for next month",
        "Lead generation strategy producing quality prospects",
        "Customer retention rate improved to industry-leading 94%",
        "Brand awareness survey results are very encouraging",
        "Revenue diversification strategy showing positive results",
        "Market expansion plan approved by board of directors",
        "Customer support ticket resolution time improved significantly",
        "Pricing strategy analysis completed by finance team",
        "Competitive positioning workshop yielded actionable insights",
        "Business development pipeline worth $2.3M this quarter",
    ]

    social_messages = [
        "Coffee chat at 3 PM - anyone interested in joining?",
        "Great job on the presentation today! Really well done.",
        "Happy birthday! Hope you have a wonderful celebration! 🎉",
        "Team lunch tomorrow at the new Italian place downtown",
        "Thanks for covering my shift yesterday, really appreciate it",
        "Congratulations on the promotion! Well deserved recognition.",
        "Looking forward to the team building event next week",
        "Friday drinks at Murphy's Pub - who's joining us?",
        "Welcome to the team! Excited to work with you.",
        "Conference was amazing - learned so much about industry trends",
        "Weather is perfect for our outdoor team meeting today",
        "Book club selection for next month: 'Clean Code' by Robert Martin",
        "Yoga class starting in conference room B in 10 minutes",
        "Anyone want to join the company softball team this season?",
        "Farewell party for Sarah is Thursday at 6 PM in the break room",
        "Thanksgiving potluck signup sheet is on the kitchen bulletin board",
        "Secret Santa gift exchange signup deadline is Friday",
        "Company picnic planning committee meeting after work today",
        "Charity drive for local food bank starts next Monday",
        "Game night at my place this Saturday - board games and pizza!",
    ]

    support_messages = [
        "Customer reported login issues with mobile app",
        "Priority 1 ticket: payment processing failures",
        "User experiencing data synchronization delays",
        "Account verification emails not being delivered",
        "Customer requests feature enhancement for dashboard",
        "Billing inquiry about subscription plan changes",
        "Technical documentation update requested by enterprise client",
        "Password reset functionality working intermittently",
        "Customer satisfaction survey scores trending upward",
        "Escalated ticket requires engineering team consultation",
        "Knowledge base article needs updating for new features",
        "Training session for new support agents next Tuesday",
        "Customer feedback: UI/UX improvements highly appreciated",
        "Service status page updated with maintenance schedule",
        "Help desk software upgrade scheduled for this weekend",
    ]

    # Combine all message categories
    all_message_categories = {
        "executive": executive_messages,
        "engineering": engineering_messages,
        "product": product_messages,
        "operations": operations_messages,
        "business": business_messages,
        "social": social_messages,
        "support": support_messages,
    }

    messages_created = 0
    target_messages = 250
    now = timezone.now()

    while messages_created < target_messages:
        for conversation in conversations:
            if messages_created >= target_messages:
                break

            # Get participants for this conversation
            participants = list(conversation.participants.all())
            if len(participants) < 2:
                continue

            # Create 2-5 messages per conversation cycle for more realistic threading
            messages_in_this_cycle = random.randint(2, 5)

            for _ in range(messages_in_this_cycle):
                if messages_created >= target_messages:
                    break

                # Pick random sender and receiver from participants
                sender = random.choice(participants)
                possible_receivers = [p for p in participants if p != sender]
                receiver = random.choice(possible_receivers)

                # Select message category based on user roles and conversation context
                if sender.is_superuser or receiver.is_superuser:
                    # Admins use executive, engineering, and business messages
                    message_categories = [
                        "executive",
                        "engineering",
                        "business",
                        "operations",
                    ]
                elif sender.is_staff and receiver.is_staff:
                    # Staff use technical, product, and operational messages
                    message_categories = [
                        "engineering",
                        "product",
                        "operations",
                        "business",
                        "support",
                    ]
                else:
                    # Regular users use support, social, and business messages
                    message_categories = ["social", "business", "support"]

                # Add social messages to all categories occasionally
                if random.random() < 0.2:  # 20% chance for social interaction
                    message_categories.append("social")

                # Select category and message
                category = random.choice(message_categories)
                message_body = random.choice(all_message_categories[category])

                # Create message with realistic timestamp distribution
                if messages_created < 50:
                    # Recent messages (last 6 hours)
                    hours_ago = random.uniform(0.1, 6)
                elif messages_created < 120:
                    # Messages from yesterday
                    hours_ago = random.uniform(6, 24)
                else:
                    # Older messages (up to 1 week)
                    hours_ago = random.uniform(24, 168)

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

                # Enhanced role indicators
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

                category_emoji = {
                    "executive": "🏢",
                    "engineering": "⚙️",
                    "product": "📦",
                    "operations": "🔧",
                    "business": "💼",
                    "social": "☕",
                    "support": "🎧",
                }.get(category, "💬")

                print(
                    f"  ✅ Message {messages_created}: {category_emoji} {role_sender} {sender.first_name} → {role_receiver} {receiver.first_name}"
                )

    print(
        f"✅ Created {messages_created} ultra-realistic messages across {len(conversations)} conversations"
    )


def main():
    """Ultimate main function to populate the database with comprehensive data"""
    try:
        print("🚀 Starting ULTIMATE database population with Faker...")
        print("=" * 60)

        # Clear existing data
        clear_existing_data()

        # Create comprehensive user base
        active_users, inactive_users = create_enhanced_users()
        all_users = active_users + inactive_users

        # Create diverse conversations
        conversations = create_enhanced_conversations(active_users)

        # Create ultimate message collection
        create_ultimate_messages(conversations, all_users)

        # Comprehensive final statistics
        print("\n" + "=" * 60)
        print("📊 ULTIMATE Population Summary:")
        print("=" * 60)

        total_users = User.objects.count()
        active_count = User.objects.filter(is_active=True).count()
        inactive_count = User.objects.filter(is_active=False).count()
        admin_count = User.objects.filter(is_superuser=True).count()
        staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
        regular_count = User.objects.filter(
            is_staff=False, is_superuser=False, is_active=True
        ).count()

        print(f"👥 Total Users: {total_users}")
        print(f"   - ✅ Active: {active_count}")
        print(f"   - ❌ Inactive: {inactive_count}")
        print(f"   - 👑 Admins: {admin_count}")
        print(f"   - 👔 Staff: {staff_count}")
        print(f"   - 👤 Regular Users: {regular_count}")

        conv_count = Conversation.conversations.count()
        msg_count = Message.messages.count()

        print(f"💬 Conversations: {conv_count}")
        print(f"📝 Messages: {msg_count}")

        # Advanced activity statistics
        logged_in_today = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(hours=24)
        ).count()
        logged_in_this_week = User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=7)
        ).count()

        recent_messages = Message.messages.filter(
            created_at__gte=timezone.now() - timedelta(days=1)
        ).count()
        this_week_messages = Message.messages.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()

        print("\n📈 Advanced Activity Statistics:")
        print(f"🟢 Users logged in today: {logged_in_today}")
        print(f"🔵 Users logged in this week: {logged_in_this_week}")
        print(f"💬 Messages sent today: {recent_messages}")
        print(f"📊 Messages sent this week: {this_week_messages}")

        if conv_count > 0:
            avg_msgs_per_conv = msg_count / conv_count
            avg_users_per_conv = (
                sum(
                    conv.participants.count()
                    for conv in Conversation.conversations.all()
                )
                / conv_count
            )
            print(f"📊 Average messages per conversation: {avg_msgs_per_conv:.1f}")
            print(f"👤 Average users per conversation: {avg_users_per_conv:.1f}")

        # Message distribution by user type
        admin_messages = Message.messages.filter(sender__is_superuser=True).count()
        staff_messages = Message.messages.filter(
            sender__is_staff=True, sender__is_superuser=False
        ).count()
        user_messages = Message.messages.filter(
            sender__is_staff=False, sender__is_superuser=False
        ).count()

        print("\n📈 Message Distribution:")
        print(f"👑 Admin messages: {admin_messages}")
        print(f"👔 Staff messages: {staff_messages}")
        print(f"👤 User messages: {user_messages}")

        print("\n" + "=" * 60)
        print("🎉 ULTIMATE database population completed successfully!")
        print("Your Django chat application is now loaded with realistic,")
        print("comprehensive data for testing and demonstration purposes.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error during population: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
