using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
namespace ControlService.Services;
public class ScenarioManager : IScenarioManager {
    private readonly IChaosStateProvider _stateProvider;
    private readonly ILogger<ScenarioManager> _logger;
    public ScenarioManager(IChaosStateProvider stateProvider, ILogger<ScenarioManager> logger) { _stateProvider = stateProvider; _logger = logger; }
    public Task<IEnumerable<string>> GetAvailableServicesAsync(CancellationToken cancellationToken = default) => 
        Task.FromResult<IEnumerable<string>>(new List<string> { "OrderService", "ProductService", "DependencyService", "Gateway", "Global" });
    public async Task<IEnumerable<ChaosScenario>> GetScenariosAsync(CancellationToken cancellationToken = default) => await _stateProvider.GetActiveScenariosAsync(cancellationToken);
    public async Task<ChaosScenario?> GetScenarioAsync(string id, CancellationToken cancellationToken = default) => await _stateProvider.GetScenarioAsync(id, cancellationToken);
    public async Task<ChaosScenario> AddScenarioAsync(ChaosScenario scenario, CancellationToken cancellationToken = default) {
        var newScenario = scenario with { Id = string.IsNullOrWhiteSpace(scenario.Id) ? Guid.NewGuid().ToString() : scenario.Id, CreatedAt = DateTimeOffset.UtcNow };
        await _stateProvider.AddOrUpdateScenarioAsync(newScenario, cancellationToken); return newScenario;
    }
    public async Task<bool> RemoveScenarioAsync(string id, CancellationToken cancellationToken = default) => await _stateProvider.RemoveScenarioAsync(id, cancellationToken);
    public async Task ResetAsync(CancellationToken cancellationToken = default) => await _stateProvider.ResetAsync(cancellationToken);
    public async Task EmergencyStopAsync(CancellationToken cancellationToken = default) => await _stateProvider.ResetAsync(cancellationToken);
}
