using System.Text.Json;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;

namespace ControlService.Services;

public record Incident(string Id, string Type, DateTimeOffset StartTime);

public class IncidentManager
{
    private readonly WorkerOrchestrator _workerOrchestrator;
    private readonly IScenarioManager _scenarioManager;
    private readonly Dictionary<string, Incident> _activeIncidents = new();

    public IncidentManager(WorkerOrchestrator workerOrchestrator, IScenarioManager scenarioManager)
    {
        _workerOrchestrator = workerOrchestrator;
        _scenarioManager = scenarioManager;
    }

    public IEnumerable<Incident> GetActiveIncidents() => _activeIncidents.Values;

    public async Task<Incident> StartCascadingFailureAsync(int durationSeconds, CancellationToken ct)
    {
        var id = Guid.NewGuid().ToString();
        var incident = new Incident(id, "CascadingFailure", DateTimeOffset.UtcNow);
        _activeIncidents[id] = incident;

        // Step 1: Inject 5 seconds Latency into Product Service
        var latencyScenario = new ChaosScenario(
            $"incident-{id}-latency", 
            ScenarioType.Latency, 
            "ProductService", 
            JsonSerializer.SerializeToElement(new LatencyConfig(5000, 0, 0, 1.0)), 
            DateTimeOffset.UtcNow, 
            DateTimeOffset.UtcNow.AddSeconds(durationSeconds)
        );
        await _scenarioManager.AddScenarioAsync(latencyScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://localhost:5003", latencyScenario, ct);

        // Step 2: Generate intense load to Order Service
        var loadConfig = new LoadGeneratorConfig(
            "http://localhost:5000/api/orders", 
            RequestsPerSecond: 200, 
            DurationSeconds: durationSeconds, 
            Concurrency: 500
        );
        await _workerOrchestrator.StartLoadAsync(loadConfig, ct);

        return incident;
    }

    public async Task StopIncidentAsync(string id, CancellationToken ct)
    {
        if (_activeIncidents.Remove(id))
        {
            await _scenarioManager.RemoveScenarioAsync($"incident-{id}-latency", ct);
            
            var client = new HttpClient();
            await client.PostAsync("http://localhost:5007/api/emergency-stop", null, ct);
            await client.PostAsync("http://localhost:5003/api/chaos/clear", null, ct);
        }
    }
}