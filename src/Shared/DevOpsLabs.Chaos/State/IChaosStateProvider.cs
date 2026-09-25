using DevOpsLabs.Chaos.Models;
namespace DevOpsLabs.Chaos.State;
public interface IChaosStateProvider {
    Task<IEnumerable<ChaosScenario>> GetActiveScenariosAsync(CancellationToken cancellationToken = default);
    Task<ChaosScenario?> GetScenarioAsync(string id, CancellationToken cancellationToken = default);
    Task<bool> AddOrUpdateScenarioAsync(ChaosScenario scenario, CancellationToken cancellationToken = default);
    Task<bool> RemoveScenarioAsync(string id, CancellationToken cancellationToken = default);
    Task ResetAsync(CancellationToken cancellationToken = default);
}
