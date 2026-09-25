using DevOpsLabs.Chaos.Models;
namespace ControlService.Services;
public interface IScenarioManager {
    Task<IEnumerable<string>> GetAvailableServicesAsync(CancellationToken cancellationToken = default);
    Task<IEnumerable<ChaosScenario>> GetScenariosAsync(CancellationToken cancellationToken = default);
    Task<ChaosScenario?> GetScenarioAsync(string id, CancellationToken cancellationToken = default);
    Task<ChaosScenario> AddScenarioAsync(ChaosScenario scenario, CancellationToken cancellationToken = default);
    Task<bool> RemoveScenarioAsync(string id, CancellationToken cancellationToken = default);
    Task ResetAsync(CancellationToken cancellationToken = default);
    Task EmergencyStopAsync(CancellationToken cancellationToken = default);
}
