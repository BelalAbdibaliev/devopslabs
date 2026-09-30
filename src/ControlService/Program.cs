using DevOpsLabs.Chaos.Observability;
using ControlService.Handlers;
using ControlService.Services;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("ControlService");
builder.Services.AddDevOpsLabsTelemetry("ControlService");

builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddHealthChecks();
builder.Services.AddHttpClient();

builder.Services.AddSingleton<IChaosStateProvider, InMemoryChaosStateProvider>();
builder.Services.AddSingleton<IScenarioManager, ScenarioManager>();
builder.Services.AddSingleton<WorkerOrchestrator>();
builder.Services.AddSingleton<IncidentManager>();

builder.Services.AddHttpLogging(o => { });
var app = builder.Build();
app.UseHttpLogging();
app.UseDefaultFiles();
app.UseStaticFiles();
app.UseDevOpsLabsMetrics();

app.UseExceptionHandler();
app.MapHealthChecks("/health");

var api = app.MapGroup("/api/control");

api.MapGet("/services", async (IScenarioManager sm, CancellationToken ct) => Results.Ok(await sm.GetAvailableServicesAsync(ct)));
api.MapGet("/scenarios", async (IScenarioManager sm, CancellationToken ct) => Results.Ok(await sm.GetScenariosAsync(ct)));
api.MapPost("/scenarios", async (ChaosScenario scenario, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var created = await sm.AddScenarioAsync(scenario, ct);
    string url = created.TargetService switch { "OrderService" => "http://orderservice:8080", "ProductService" => "http://productservice:8080", "DependencyService" => "http://dependencyservice:8080", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, created, ct);
    return Results.Created($"/api/control/scenarios/{created.Id}", created);
});
api.MapDelete("/scenarios/{id}", async (string id, IScenarioManager sm, CancellationToken ct) => await sm.RemoveScenarioAsync(id, ct) ? Results.NoContent() : Results.NotFound());
api.MapMethods("/reset", new[] { "POST", "GET", "PUT", "DELETE" }, async (IScenarioManager sm, CancellationToken ct) => { await sm.ResetAsync(ct); return Results.Ok(new { Message = "Reset" }); });
api.MapGet("/jobs", async (WorkerOrchestrator wo, CancellationToken ct) => Results.Ok(await wo.GetActiveJobsAsync(ct)));
api.MapDelete("/jobs/{id}", async (string id, WorkerOrchestrator wo, CancellationToken ct) => await wo.StopJobAsync(id, ct) ? Results.NoContent() : Results.NotFound());

api.MapPost("/cpu", async (CpuStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartCpuStressAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapPost("/memory", async (MemoryStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartMemoryStressAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapPost("/load", async (LoadGeneratorConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartLoadAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapMethods("/emergency-stop", new[] { "POST", "GET" }, async (IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{ await sm.EmergencyStopAsync(ct); await wo.EmergencyStopAsync(ct); return Results.Ok(new { Message = "Emergency stop executed" }); });

api.MapPost("/latency", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var target = payload.GetProperty("service").GetString() ?? "ProductService";
    var config = System.Text.Json.JsonSerializer.Deserialize<LatencyConfig>(payload.GetRawText(), new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.Latency, target, System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    string url = target switch { "OrderService" => "http://orderservice:8080", "ProductService" => "http://productservice:8080", "DependencyService" => "http://dependencyservice:8080", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, scenario, ct);
    return Results.Ok(scenario);
});

api.MapPost("/errors", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var target = payload.GetProperty("service").GetString() ?? "ProductService";
    var config = System.Text.Json.JsonSerializer.Deserialize<ErrorConfig>(payload.GetRawText(), new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.ErrorInjection, target, System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    string url = target switch { "OrderService" => "http://orderservice:8080", "ProductService" => "http://productservice:8080", "DependencyService" => "http://dependencyservice:8080", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, scenario, ct);
    return Results.Ok(scenario);
});

api.MapPost("/incidents/start", async (System.Text.Json.JsonElement payload, IncidentManager im, CancellationToken ct) => 
{
    var type = payload.GetProperty("type").GetString();
    var duration = payload.GetProperty("durationSeconds").GetInt32();
    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    if (type == "error-storm") return Results.Ok(await im.StartErrorStormAsync(duration, ct));
    if (type == "combined-outage") return Results.Ok(await im.StartCombinedOutageAsync(duration, ct));
    return Results.BadRequest();
});

api.MapGet("/incidents", (IncidentManager im) => Results.Ok(im.GetActiveIncidents()));
api.MapPost("/incidents/{id}/stop", async (string id, IncidentManager im, CancellationToken ct) => { await im.StopIncidentAsync(id, ct); return Results.Ok(); });


// -- Infrastructure Chaos Endpoints --
api.MapPost("/db/stress", async (DbStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var client = new HttpClient();
    // Assuming OrderService for Insert, ProductService for Select load
    var target = config.Type == "Insert" ? "http://orderservice:8080" : "http://productservice:8080";
    var res = await client.PostAsJsonAsync($"{target}/api/db/stress", config, ct);
    return res.IsSuccessStatusCode ? Results.Accepted() : Results.StatusCode(500);
});

api.MapPost("/queue/load", async (QueueLoadConfig config, CancellationToken ct) => 
{
    var client = new HttpClient();
    var res = await client.PostAsJsonAsync("http://orderservice:8080/api/queue/load", config, ct);
    return res.IsSuccessStatusCode ? Results.Accepted() : Results.StatusCode(500);
});

api.MapPost("/queue/consumer", async (QueueConsumerConfig config, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.DependencyFailure, "Consumer", System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    await wo.SyncChaosToServiceAsync("http://notificationservice:8080", scenario, ct); // NotificationService runs on 5008 typically, but let's sync to all
    return Results.Ok(scenario);
});

api.MapPost("/redis/outage", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var durationSeconds = payload.GetProperty("durationSeconds").GetInt32();
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.DependencyFailure, "Redis", null, DateTimeOffset.UtcNow, DateTimeOffset.UtcNow.AddSeconds(durationSeconds));
    await sm.AddScenarioAsync(scenario, ct);
    await wo.SyncChaosToServiceAsync("http://productservice:8080", scenario, ct); // ProductService uses Redis
    return Results.Ok(scenario);
});

app.Run();