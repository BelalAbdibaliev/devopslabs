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
        await _workerOrchestrator.SyncChaosToServiceAsync("http://productservice:8080", latencyScenario, ct);

        // Step 2: Generate intense load to Order Service
        var loadConfig = new LoadGeneratorConfig(
            "http://gateway:8080/api/orders", 
            RequestsPerSecond: 200, 
            DurationSeconds: durationSeconds, 
            Concurrency: 500
        );
        await _workerOrchestrator.StartLoadAsync(loadConfig, ct);

        return incident;
    }


    public async Task<Incident> StartErrorStormAsync(int durationSeconds, CancellationToken ct)
    {
        var id = Guid.NewGuid().ToString();
        var incident = new Incident(id, "ErrorStorm", DateTimeOffset.UtcNow);
        _activeIncidents[id] = incident;

        var errScenario = new ChaosScenario($"incident-{id}-err", ScenarioType.ErrorInjection, "OrderService", 
            JsonSerializer.SerializeToElement(new ErrorConfig(500, 0.4)), DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
        
        await _scenarioManager.AddScenarioAsync(errScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://orderservice:8080", errScenario, ct);
        return incident;
    }

    public async Task<Incident> StartCombinedOutageAsync(int durationSeconds, CancellationToken ct)
    {
        var id = Guid.NewGuid().ToString();
        var incident = new Incident(id, "CombinedOutage", DateTimeOffset.UtcNow);
        _activeIncidents[id] = incident;

        // Redis outage + Latency
        var redisScenario = new ChaosScenario($"incident-{id}-redis", ScenarioType.DependencyFailure, "ProductService", 
            null, DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
        
        var latencyScenario = new ChaosScenario($"incident-{id}-lat", ScenarioType.Latency, "OrderService", 
            JsonSerializer.SerializeToElement(new LatencyConfig(3000, 0, 0, 1.0)), DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
            
        await _scenarioManager.AddScenarioAsync(redisScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://productservice:8080", redisScenario, ct);

        await _scenarioManager.AddScenarioAsync(latencyScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://orderservice:8080", latencyScenario, ct);
        return incident;
    }

    public async Task StopIncidentAsync(string id, CancellationToken ct)
    {
        if (_activeIncidents.Remove(id))
        {
            await _scenarioManager.RemoveScenarioAsync($"incident-{id}-latency", ct);
            
            var client = new HttpClient();
            await client.PostAsync("http://loadgenerator:8080/api/emergency-stop", null, ct);
            await client.PostAsync("http://productservice:8080/api/chaos/clear", null, ct);
        }
    }
}