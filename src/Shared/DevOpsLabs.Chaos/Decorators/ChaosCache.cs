using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
using Microsoft.Extensions.Caching.Distributed;
using Microsoft.Extensions.Logging;

namespace DevOpsLabs.Chaos.Decorators;

public class ChaosCache : IDistributedCache
{
    private readonly IDistributedCache _inner;
    private readonly IChaosStateProvider _state;
    private readonly ILogger<ChaosCache> _logger;

    public ChaosCache(IDistributedCache inner, IChaosStateProvider state, ILogger<ChaosCache> logger)
    {
        _inner = inner;
        _state = state;
        _logger = logger;
    }

    private async Task CheckChaosAsync(CancellationToken token = default)
    {
        var scenarios = await _state.GetActiveScenariosAsync(token);
        if (scenarios.Any(s => s.Type == ScenarioType.DependencyFailure && s.TargetService == "Redis"))
        {
            _logger.LogWarning("Chaos: Simulating Redis Outage!");
            throw new Exception("Simulated Redis Outage");
        }
        if (scenarios.Any(s => s.Type == ScenarioType.Latency && s.TargetService == "Redis"))
        {
            _logger.LogWarning("Chaos: Simulating Redis Latency!");
            await Task.Delay(2000, token);
        }
    }

    public byte[]? Get(string key) => GetAsync(key).GetAwaiter().GetResult();
    public async Task<byte[]?> GetAsync(string key, CancellationToken token = default)
    {
        await CheckChaosAsync(token);
        return await _inner.GetAsync(key, token);
    }
    public void Refresh(string key) => RefreshAsync(key).GetAwaiter().GetResult();
    public async Task RefreshAsync(string key, CancellationToken token = default)
    {
        await CheckChaosAsync(token);
        await _inner.RefreshAsync(key, token);
    }
    public void Remove(string key) => RemoveAsync(key).GetAwaiter().GetResult();
    public async Task RemoveAsync(string key, CancellationToken token = default)
    {
        await CheckChaosAsync(token);
        await _inner.RemoveAsync(key, token);
    }
    public void Set(string key, byte[] value, DistributedCacheEntryOptions options) => SetAsync(key, value, options).GetAwaiter().GetResult();
    public async Task SetAsync(string key, byte[] value, DistributedCacheEntryOptions options, CancellationToken token = default)
    {
        await CheckChaosAsync(token);
        await _inner.SetAsync(key, value, options, token);
    }
}