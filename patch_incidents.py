import os

# 1. Update IncidentManager.cs
im_file = "src/ControlService/Services/IncidentManager.cs"
with open(im_file, "r") as f:
    im_content = f.read()

new_methods = """
    public async Task<Incident> StartErrorStormAsync(int durationSeconds, CancellationToken ct)
    {
        var id = Guid.NewGuid().ToString();
        var incident = new Incident(id, "ErrorStorm", DateTimeOffset.UtcNow);
        _activeIncidents[id] = incident;

        var errScenario = new ChaosScenario($"incident-{id}-err", ScenarioType.Error, "OrderService", 
            JsonSerializer.SerializeToElement(new ErrorConfig(500, 0.4)), DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
        
        await _scenarioManager.AddScenarioAsync(errScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://orderservice:8080", errScenario, ct);
        return incident;
    }

    public async Task<Incident> StartCombinedOutageAsync(int durationSeconds, CancellationToken ct)
    {
        var id = Guid.NewGuid().ToString();
        var incident = new Incident(id, "CombinedOutage", DateTimeOffset.UtcNow);
        _activeIncidents[id] = incident;

        // Redis outage + Latency
        var redisScenario = new ChaosScenario($"incident-{id}-redis", ScenarioType.DependencyFailure, "ProductService", 
            JsonSerializer.SerializeToElement(new DependencyConfig("Redis", DependencyFailureType.Unavailable)), DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
        
        var latencyScenario = new ChaosScenario($"incident-{id}-lat", ScenarioType.Latency, "OrderService", 
            JsonSerializer.SerializeToElement(new LatencyConfig(3000, 0, 0, 1.0)), DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
            
        await _scenarioManager.AddScenarioAsync(redisScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://productservice:8080", redisScenario, ct);

        await _scenarioManager.AddScenarioAsync(latencyScenario, ct);
        await _workerOrchestrator.SyncChaosToServiceAsync("http://orderservice:8080", latencyScenario, ct);
        return incident;
    }
"""
if "StartErrorStormAsync" not in im_content:
    im_content = im_content.replace("    public async Task StopIncidentAsync", new_methods + "\n    public async Task StopIncidentAsync")
    with open(im_file, "w") as f:
        f.write(im_content)

# 2. Update Program.cs
prog_file = "src/ControlService/Program.cs"
with open(prog_file, "r") as f:
    prog = f.read()

# Fix the routing
prog = prog.replace(
"""    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    return Results.BadRequest();""",
"""    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    if (type == "error-storm") return Results.Ok(await im.StartErrorStormAsync(duration, ct));
    if (type == "combined-outage") return Results.Ok(await im.StartCombinedOutageAsync(duration, ct));
    return Results.BadRequest();"""
)

# Robust Reset mapping (accept any request, discard body)
if "api.MapPost(\"/reset\", async (IScenarioManager sm, CancellationToken ct)" in prog:
    prog = prog.replace("api.MapPost(\"/reset\", async (IScenarioManager sm, CancellationToken ct) => { await sm.ResetAsync(ct); return Results.Ok(new { Message = \"Reset\" }); });",
"""api.MapMethods("/reset", new[] { "POST", "GET", "PUT", "DELETE" }, async (IScenarioManager sm, CancellationToken ct) => { await sm.ResetAsync(ct); return Results.Ok(new { Message = "Reset" }); });""")

if "api.MapPost(\"/emergency-stop\"" in prog:
    prog = prog.replace("api.MapPost(\"/emergency-stop\", async (IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) =>",
"""api.MapMethods("/emergency-stop", new[] { "POST", "GET" }, async (IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) =>""")

with open(prog_file, "w") as f:
    f.write(prog)
