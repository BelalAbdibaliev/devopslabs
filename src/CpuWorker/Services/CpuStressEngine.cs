using System.Collections.Concurrent;
using System.Diagnostics;
using DevOpsLabs.Chaos.Models;

namespace CpuWorker.Services;

public class CpuStressEngine
{
    private readonly ConcurrentDictionary<string, (JobDto Job, CancellationTokenSource Cts)> _jobs = new();
    private readonly ILogger<CpuStressEngine> _logger;

    public CpuStressEngine(ILogger<CpuStressEngine> logger) => _logger = logger;

    public IEnumerable<JobDto> GetJobs() => _jobs.Values.Select(v => v.Job);

    public JobDto StartJob(CpuStressConfig config)
    {
        var id = Guid.NewGuid().ToString();
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(config.DurationSeconds));
        var job = new JobDto { Id = id, Type = "CpuStress", Status = JobStatus.Running, StartTime = DateTimeOffset.UtcNow, Configuration = config };
        
        _jobs[id] = (job, cts);

        int workers = config.WorkerCount > 0 ? config.WorkerCount : 1;
        for (int i = 0; i < workers; i++)
        {
            Task.Run(() => StressThread(config.TargetPercentage, cts.Token), cts.Token);
        }

        cts.Token.Register(() => { job.Status = JobStatus.Completed; job.EndTime = DateTimeOffset.UtcNow; });
        return job;
    }

    public bool StopJob(string id)
    {
        if (_jobs.TryGetValue(id, out var activeJob))
        {
            if (!activeJob.Cts.IsCancellationRequested) activeJob.Cts.Cancel();
            activeJob.Job.Status = JobStatus.Cancelled;
            activeJob.Job.EndTime = DateTimeOffset.UtcNow;
            return true;
        }
        return false;
    }

    public void StopAll()
    {
        foreach (var kvp in _jobs)
            StopJob(kvp.Key);
    }

    private void StressThread(int targetPercentage, CancellationToken ct)
    {
        var watch = new Stopwatch();
        while (!ct.IsCancellationRequested)
        {
            watch.Restart();
            while (watch.ElapsedMilliseconds < targetPercentage)
            {
                if (ct.IsCancellationRequested) break;
                _ = Math.Sqrt(new Random().NextDouble());
            }
            var sleepTime = 100 - targetPercentage;
            if (sleepTime > 0) Thread.Sleep(sleepTime);
        }
    }
}