using System.Collections.Concurrent;
using DevOpsLabs.Chaos.Models;

namespace MemoryWorker.Services;

public class MemoryStressEngine
{
    private readonly ConcurrentDictionary<string, (JobDto Job, CancellationTokenSource Cts, List<byte[]> Memory)> _jobs = new();
    private readonly ILogger<MemoryStressEngine> _logger;

    public MemoryStressEngine(ILogger<MemoryStressEngine> logger) => _logger = logger;

    public IEnumerable<JobDto> GetJobs() => _jobs.Values.Select(v => v.Job);

    public JobDto StartJob(MemoryStressConfig config)
    {
        var id = Guid.NewGuid().ToString();
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(config.DurationSeconds));
        var job = new JobDto { Id = id, Type = "MemoryStress", Status = JobStatus.Running, StartTime = DateTimeOffset.UtcNow, Configuration = config };
        
        var memoryHolders = new List<byte[]>();
        _jobs[id] = (job, cts, memoryHolders);

        Task.Run(async () => await AllocationLoop(config, memoryHolders, cts.Token), cts.Token);

        cts.Token.Register(() => { 
            job.Status = JobStatus.Completed; 
            job.EndTime = DateTimeOffset.UtcNow; 
            _jobs[id].Memory.Clear();
            GC.Collect();
        });
        return job;
    }

    private async Task AllocationLoop(MemoryStressConfig config, List<byte[]> memoryHolders, CancellationToken ct)
    {
        try 
        {
            int currentMb = config.StartMegabytes > 0 ? config.StartMegabytes : config.TargetMegabytes;
            Allocate(currentMb, memoryHolders);

            if (config.IncreaseEverySeconds > 0 && config.StartMegabytes < config.TargetMegabytes)
            {
                while (!ct.IsCancellationRequested && currentMb < config.TargetMegabytes)
                {
                    await Task.Delay(TimeSpan.FromSeconds(config.IncreaseEverySeconds), ct);
                    int step = 100; 
                    if (currentMb + step > config.TargetMegabytes) step = config.TargetMegabytes - currentMb;
                    Allocate(step, memoryHolders);
                    currentMb += step;
                }
            }
            await Task.Delay(Timeout.Infinite, ct);
        }
        catch (OperationCanceledException) { }
    }

    private void Allocate(int megabytes, List<byte[]> memoryHolders)
    {
        for(int i = 0; i < megabytes; i++) {
            var chunk = new byte[1024 * 1024];
            new Random().NextBytes(chunk);
            memoryHolders.Add(chunk);
        }
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