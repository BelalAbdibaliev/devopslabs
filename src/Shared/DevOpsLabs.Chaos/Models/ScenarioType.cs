namespace DevOpsLabs.Chaos.Models;

public enum ScenarioType
{
    CpuStress, MemoryStress, Load, Latency, ErrorInjection, DependencyFailure, DatabaseStress, QueueBacklog
}
