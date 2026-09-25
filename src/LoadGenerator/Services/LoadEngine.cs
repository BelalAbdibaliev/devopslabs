using System.Collections.Concurrent;
using System.Diagnostics;
using DevOpsLabs.Chaos.Models;

namespace LoadGenerator.Services;

public class LoadEngine
{
    private readonly ConcurrentDictionary<string, (JobDto Job, CancellationTokenSource Cts)> _jobs = new();
    private readonly IHttpClientFactory _clientFactory;

    public LoadEngine(IHttpClientFactory clientFactory) => _clientFactory = clientFactory;

    public IEnumerable<JobDto> GetJobs() => _jobs.Values.Select(v => v.Job);

    public JobDto StartJob(LoadGeneratorConfig config)
    {
        var id = Guid.NewGuid().ToString();
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(config.DurationSeconds));
        var job = new JobDto { Id = id, Type = "LoadGenerator", Status = JobStatus.Running, StartTime = DateTimeOffset.UtcNow, Configuration = config };
        
        _jobs[id] = (job, cts);

        Task.Run(async () => await GenerateLoad(config, cts.Token), cts.Token);
        
        cts.Token.Register(() => { job.Status = JobStatus.Completed; job.EndTime = DateTimeOffset.UtcNow; });
        return job;
    }

    private async Task GenerateLoad(LoadGeneratorConfig config, CancellationToken ct)
    {
        var client = _clientFactory.CreateClient();
        int maxConcurrency = config.Concurrency > 0 ? config.Concurrency : 1;
        using var semaphore = new SemaphoreSlim(maxConcurrency, maxConcurrency);
        
        var requestInterval = config.RequestsPerSecond > 0 ? 1000.0 / config.RequestsPerSecond : 0;
        using var timer = new PeriodicTimer(TimeSpan.FromMilliseconds(requestInterval > 0 ? requestInterval : 1));
        
        try
        {
            while (!ct.IsCancellationRequested && (requestInterval == 0 || await timer.WaitForNextTickAsync(ct)))
            {
                await semaphore.WaitAsync(ct);
                _ = Task.Run(async () =>
                {
                    try
                    {
                        var req = new HttpRequestMessage(new HttpMethod(config.Method), config.TargetUrl);
                        if (!string.IsNullOrEmpty(config.Payload))
                            req.Content = new StringContent(config.Payload, System.Text.Encoding.UTF8, "application/json");
                        await client.SendAsync(req, ct);
                    }
                    catch { /* swallow */ }
                    finally { semaphore.Release(); }
                }, ct);
            }
        }
        catch (OperationCanceledException) { }
    }

    public bool StopJob(string id)
    {
        if (_jobs.TryGetValue(id, out var activeJob))
        {
            if (!activeJob.Cts.IsCancellationRequested) activeJob.Cts.Cancel();
            activeJob.Job.Status = JobStatus.Cancelled;
            return true;
        }
        return false;
    }

    public void StopAll()
    {
        foreach (var kvp in _jobs) StopJob(kvp.Key);
    }
}