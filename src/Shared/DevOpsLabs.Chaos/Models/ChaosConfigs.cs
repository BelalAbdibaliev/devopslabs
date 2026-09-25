using System.Text.Json;

namespace DevOpsLabs.Chaos.Models;

public record LatencyConfig(int DelayMilliseconds = 0, int MinDelayMilliseconds = 0, int MaxDelayMilliseconds = 0, double Probability = 1.0);
public record ErrorConfig(int StatusCode, double Probability = 1.0);
public record RateLimitConfig(string Type, int PermitLimit, int WindowSeconds);