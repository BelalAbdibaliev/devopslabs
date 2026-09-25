using System.Text.Json.Serialization;

namespace DevOpsLabs.Chaos.Models;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum JobStatus { Running, Completed, Cancelled, Failed }

public class JobDto
{
    public string Id { get; set; } = "";
    public string Type { get; set; } = "";
    public JobStatus Status { get; set; }
    public DateTimeOffset StartTime { get; set; }
    public DateTimeOffset? EndTime { get; set; }
    public object? Configuration { get; set; }
}

public record CpuStressConfig(int TargetPercentage, int DurationSeconds, int WorkerCount = 1);
public record MemoryStressConfig(int TargetMegabytes, int DurationSeconds, int StartMegabytes = 0, int IncreaseEverySeconds = 0);
public record LoadGeneratorConfig(string TargetUrl, int RequestsPerSecond, int DurationSeconds, int Concurrency, string Method = "GET", string? Payload = null);