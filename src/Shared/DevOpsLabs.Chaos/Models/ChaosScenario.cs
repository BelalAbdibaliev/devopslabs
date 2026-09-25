using System.Text.Json;
namespace DevOpsLabs.Chaos.Models;
public record ChaosScenario(string Id, ScenarioType Type, string TargetService, JsonElement? Parameters, DateTimeOffset CreatedAt, DateTimeOffset? ExpiresAt);
