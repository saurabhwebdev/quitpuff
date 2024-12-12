function AIChatMessage({ message }: { message: Message }) {
  // ... existing imports and code ...

  const formatTimestamp = (timestamp: string) => {
    // Convert UTC timestamp to local time
    const date = new Date(timestamp);
    return date.toLocaleTimeString(); // This will use the system's local timezone
  };

  return (
    <div className={/* ... existing classes ... */}>
      {/* ... other message content ... */}
      <div className="text-xs text-gray-400">
        {formatTimestamp(message.created_at)}
      </div>
    </div>
  );
} 