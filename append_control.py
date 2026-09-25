import re

with open("src/ControlService/Program.cs", "r") as f:
    content = f.read()

endpoints = """
// -- Infrastructure Chaos Endpoints --
api.MapPost("/db/stress", async (DbStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var client = new HttpClient();
    // Assuming OrderService for Insert, ProductService for Select load
    var target = config.Type == "Insert" ? "http://localhost:5002" : "http://localhost:5003";
    var res = await client.PostAsJsonAsync($"{target}/api/db/stress", config, ct);
    return res.IsSuccessStatusCode ? Results.Accepted() : Results.StatusCode(500);
});

api.MapPost("/queue/load", async (QueueLoadConfig config, CancellationToken ct) => 
{
    var client = new HttpClient();
    var res = await client.PostAsJsonAsync("http://localhost:5002/api/queue/load", config, ct);
    return res.IsSuccessStatusCode ? Results.Accepted() : Results.StatusCode(500);
});

api.MapPost("/queue/consumer", async (QueueConsumerConfig config, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.DependencyFailure, "Consumer", System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    await wo.SyncChaosToServiceAsync("http://localhost:5008", scenario, ct); // NotificationService runs on 5008 typically, but let's sync to all
    return Results.Ok(scenario);
});

api.MapPost("/redis/outage", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var durationSeconds = payload.GetProperty("durationSeconds").GetInt32();
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.DependencyFailure, "Redis", null, DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
    await sm.AddScenarioAsync(scenario, ct);
    await wo.SyncChaosToServiceAsync("http://localhost:5003", scenario, ct); // ProductService uses Redis
    return Results.Ok(scenario);
});
"""

if "// -- Infrastructure Chaos Endpoints --" not in content:
    content = content.replace("app.Run();", endpoints + "\\napp.Run();")
    with open("src/ControlService/Program.cs", "w") as f:
        f.write(content)
