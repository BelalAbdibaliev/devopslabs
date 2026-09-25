namespace DevOpsLabs.Chaos.Models;

public record DbStressConfig(int QueriesPerSecond, int Concurrency, int DurationSeconds, string Type);
public record QueueLoadConfig(int MessagesPerSecond, int DurationSeconds);
public record QueueConsumerConfig(int ProcessingTimeMilliseconds, bool StopConsumers, int ConsumerCount);