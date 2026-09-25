using DevOpsLabs.Chaos.Models;

namespace ControlService.Services;

public class WorkerOrchestrator
{
    private readonly IHttpClientFactory _clientFactory;
    private readonly string[] _workers = new[] { "http://localhost:5005", "http://localhost:5006", "http://localhost:5007" };

    public WorkerOrchestrator(IHttpClientFactory clientFactory) => _clientFactory = clientFactory;

    public async Task<IEnumerable<JobDto>> GetActiveJobsAsync(CancellationToken ct)
    {
        var jobs = new List<JobDto>();
        var client = _clientFactory.CreateClient();
        
        foreach (var w in _workers)
        {
            try {
                var res = await client.GetFromJsonAsync<List<JobDto>>($"{w}/api/jobs", ct);
                if (res != null) jobs.AddRange(res);
            } catch { }
        }
        return jobs;
    }

    public async Task<JobDto?> StartCpuStressAsync(CpuStressConfig config, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        var res = await client.PostAsJsonAsync("http://localhost:5005/api/jobs", config, ct);
        return await res.Content.ReadFromJsonAsync<JobDto>(cancellationToken: ct);
    }

    public async Task<JobDto?> StartMemoryStressAsync(MemoryStressConfig config, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        var res = await client.PostAsJsonAsync("http://localhost:5006/api/jobs", config, ct);
        return await res.Content.ReadFromJsonAsync<JobDto>(cancellationToken: ct);
    }

    public async Task<JobDto?> StartLoadAsync(LoadGeneratorConfig config, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        var res = await client.PostAsJsonAsync("http://localhost:5007/api/jobs", config, ct);
        return await res.Content.ReadFromJsonAsync<JobDto>(cancellationToken: ct);
    }

    public async Task<bool> StopJobAsync(string id, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        foreach (var w in _workers)
        {
            try {
                var res = await client.DeleteAsync($"{w}/api/jobs/{id}", ct);
                if (res.IsSuccessStatusCode) return true;
            } catch { }
        }
        return false;
    }

    public async Task SyncChaosToServiceAsync(string serviceUrl, ChaosScenario scenario, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        try { await client.PostAsJsonAsync($"{serviceUrl}/api/chaos/sync", scenario, ct); } catch { }
    }

    public async Task EmergencyStopAsync(CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        foreach (var w in _workers) { try { await client.PostAsync($"{w}/api/emergency-stop", null, ct); } catch { } }
        
        // Also clear business services chaos state
        var biz = new[] { "http://localhost:5002", "http://localhost:5003", "http://localhost:5004" };
        foreach (var b in biz) { try { await client.PostAsync($"{b}/api/chaos/clear", null, ct); } catch { } }
    }
}