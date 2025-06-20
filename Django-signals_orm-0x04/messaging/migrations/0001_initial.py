# Generated by Django 5.2.2 on 2025-06-12 20:51

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the message', primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField(help_text='Content of the message')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the message was sent')),
                ('recipient', models.ForeignKey(help_text='User who received the message', on_delete=django.db.models.deletion.CASCADE, related_name='messaging_received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(help_text='User who sent the message', on_delete=django.db.models.deletion.CASCADE, related_name='messaging_sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'db_table': 'messaging_message',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the notification', primary_key=True, serialize=False, unique=True)),
                ('is_read', models.BooleanField(default=False, help_text='Indicates whether the notification has been read')),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the notification was created')),
                ('message', models.ForeignKey(help_text='Message associated with the notification', on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='messaging.message')),
                ('recipient', models.ForeignKey(help_text='User who will receive the notification', on_delete=django.db.models.deletion.CASCADE, related_name='messaging_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'db_table': 'messaging_notification',
            },
        ),
    ]
