# Filtering in the Messaging App

This document describes the filtering capabilities in the messaging app using django-filter, and how to use them to retrieve specific conversations and messages.

## Message Filtering

### Available Filters

The `MessageFilter` class provides the following filter options:

1. **Time Range Filters**
   - `sent_after`: Filter messages sent after a specific date/time
   - `sent_before`: Filter messages sent before a specific date/time

2. **User Filters**
   - `sender`: Filter messages by sender (using the user's UUID)
   - `receiver`: Filter messages by receiver (using the user's UUID)

3. **Participant Filter**
   - `participant`: Filter messages from all conversations where the specified user is a participant

4. **Content Filter**
   - `content`: Filter messages containing specific text (case-insensitive)

> **Note**: When filtering by content, use the `content` parameter rather than `search` for more accurate results. The `content` parameter searches only in the message body, while `search` looks across multiple fields including sender and receiver emails.

### Example Usage

To filter messages in API requests, add the filter parameters to your URL query string:

```
# Get messages sent after a specific date
/api/messages/?sent_after=2025-06-01T00:00:00

# Get messages sent by a specific user
/api/messages/?sender=550e8400-e29b-41d4-a716-446655440000

# Get messages from all conversations a user is part of
/api/messages/?participant=550e8400-e29b-41d4-a716-446655440000

# Get messages containing specific text
/api/messages/?content=hello

# Combine multiple filters
/api/messages/?sent_after=2025-06-01T00:00:00&content=hello
```

## Conversation Filtering

### Available Filters

The `ConversationFilter` class provides the following filter options:

1. **Participant Filter**
   - `participant`: Filter conversations where the specified user is a participant

2. **Date Range Filters**
   - `created_after`: Filter conversations with messages created after a specific date/time
   - `created_before`: Filter conversations with messages created before a specific date/time

3. **Specific Participants Filter**
   - `specific_participants`: Filter conversations that include all the specified users (comma-separated list of user UUIDs)

### Example Usage

To filter conversations in API requests, add the filter parameters to your URL query string:

```
# Get conversations where a specific user is a participant
/api/conversations/?participant=550e8400-e29b-41d4-a716-446655440000

# Get conversations with messages created after a specific date
/api/conversations/?created_after=2025-06-01T00:00:00

# Get conversations that include specific users
/api/conversations/?specific_participants=550e8400-e29b-41d4-a716-446655440000,662e8400-e29b-41d4-a716-446655440000

# Combine multiple filters
/api/conversations/?participant=550e8400-e29b-41d4-a716-446655440000&created_after=2025-06-01T00:00:00
```

## Searching and Ordering

In addition to the filters above, both messages and conversations support:

1. **Search Fields**
   - Messages: `message_body`, `sender__email`, `receiver__email`
   - Conversations: `participants__email`, `participants__first_name`, `participants__last_name`

> **Important**: The search functionality is broader than filtering. When using `?search=term`, it will look across all search fields, not just message content. For example, searching for "test" might return messages where the word "test" appears in the sender's or receiver's email, even if it's not in the message body. Use `?content=term` for more specific content filtering.

2. **Ordering Fields**
   - Messages: `sent_at`, `created_at`
   - Conversations: `conversation_id`

### Example Usage

```
# Search for messages containing specific text in the body or from a specific email
/api/messages/?search=important

# Order messages by sent time (descending)
/api/messages/?ordering=-sent_at

# Search for conversations with participants matching a name
/api/conversations/?search=john

# Combine search, ordering and filtering
/api/messages/?search=hello&ordering=-sent_at&sender=550e8400-e29b-41d4-a716-446655440000
```

## Pagination

Both endpoints use pagination to limit the number of results returned in a single request. The default page size is 20 items, but you can customize it using the `page_size` parameter:

```
# Get the first page of results with default page size
/api/messages/

# Get the second page of results
/api/messages/?page=2

# Get results with a custom page size
/api/messages/?page_size=50
```

## Testing the Filters

Several test scripts are provided to demonstrate and validate these filtering capabilities:

1. `test_message_filters.py`: Demonstrates message filtering
2. `test_conversation_filters.py`: Demonstrates conversation filtering
3. `final_validate_filters.py`: Validates all filtering capabilities against actual data

Run these scripts to see examples of filtering in action and validate the implementation:

```bash
./test_message_filters.py
./test_conversation_filters.py
./final_validate_filters.py
```

## Best Practices

1. **For message content filtering**: Use `?content=term` rather than `?search=term` for more accurate results.
2. **For conversations with specific users**: Use `?specific_participants=id1,id2` to find conversations with all the specified users.
3. **For time-based filtering**: Ensure your timestamps are in ISO format (YYYY-MM-DDThh:mm:ss).
4. **For complex queries**: You can combine multiple filters, search, and ordering in a single request.
