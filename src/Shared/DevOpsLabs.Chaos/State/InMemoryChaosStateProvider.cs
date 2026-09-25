using System.Collections.Concurrent;
using DevOpsLabs.Chaos.Models;
namespace DevOpsLabs.Chaos.State;
public class InMemoryChaosStateProvider : IChaosStateProvider {
    private readonly ConcurrentDictionary<string, ChaosScenario> _scenarios = new();
    public Task<IEnumerable<ChaosScenario>> GetActiveScenariosAsync(CancellationToken cancellationToken = default) {
        var now = DateTimeOffset.UtcNow;
        return Task.FromResult<IEnumerable<ChaosScenario>>(_scenarios.Values.Where(s => !s.ExpiresAt.HasValue || s.ExpiresAt.Value > now).ToList());
    }
    public Task<ChaosScenario?> GetScenarioAsync(string id, CancellationToken cancellationToken = default) {
        _scenarios.TryGetValue(id, out var s);
        if (s != null && s.ExpiresAt.HasValue && s.ExpiresAt.Value <= DateTimeOffset.UtcNow) {
            _scenarios.TryRemove(id, out _); return Task.FromResult<ChaosScenario?>(null);
        }
        return Task.FromResult(s);
    }
    public Task<bool> AddOrUpdateScenarioAsync(ChaosScenario scenario, CancellationToken cancellationToken = default) {
        _scenarios.AddOrUpdate(scenario.Id, scenario, (_, _) => scenario); return Task.FromResult(true);
    }
    public Task<bool> RemoveScenarioAsync(string id, CancellationToken cancellationToken = default) {
        return Task.FromResult(_scenarios.TryRemove(id, out _));
    }
    public Task ResetAsync(CancellationToken cancellationToken = default) {
        _scenarios.Clear(); return Task.FromResult(true);
    }
}
