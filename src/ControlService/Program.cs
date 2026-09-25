using ControlService.Handlers;
using ControlService.Services;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddHealthChecks();
builder.Services.AddHttpClient();

builder.Services.AddSingleton<IChaosStateProvider, InMemoryChaosStateProvider>();
builder.Services.AddSingleton<IScenarioManager, ScenarioManager>();
builder.Services.AddSingleton<WorkerOrchestrator>();
builder.Services.AddSingleton<IncidentManager>();

var app = builder.Build();

app.UseExceptionHandler();
app.MapHealthChecks("/health");

var api = app.MapGroup("/api/control");

api.MapGet("/services", async (IScenarioManager sm, CancellationToken ct) => Results.Ok(await sm.GetAvailableServicesAsync(ct)));
api.MapGet("/scenarios", async (IScenarioManager sm, CancellationToken ct) => Results.Ok(await sm.GetScenariosAsync(ct)));
api.MapPost("/scenarios", async (ChaosScenario scenario, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var created = await sm.AddScenarioAsync(scenario, ct);
    string url = created.TargetService switch { "OrderService" => "http://localhost:5002", "ProductService" => "http://localhost:5003", "DependencyService" => "http://localhost:5004", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, created, ct);
    return Results.Created($"/api/control/scenarios/{created.Id}", created);
});
api.MapDelete("/scenarios/{id}", async (string id, IScenarioManager sm, CancellationToken ct) => await sm.RemoveScenarioAsync(id, ct) ? Results.NoContent() : Results.NotFound());
api.MapPost("/reset", async (IScenarioManager sm, CancellationToken ct) => { await sm.ResetAsync(ct); return Results.Ok(new { Message = "Reset" }); });
api.MapGet("/jobs", async (WorkerOrchestrator wo, CancellationToken ct) => Results.Ok(await wo.GetActiveJobsAsync(ct)));
api.MapDelete("/jobs/{id}", async (string id, WorkerOrchestrator wo, CancellationToken ct) => await wo.StopJobAsync(id, ct) ? Results.NoContent() : Results.NotFound());

api.MapPost("/cpu", async (CpuStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartCpuStressAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapPost("/memory", async (MemoryStressConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartMemoryStressAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapPost("/load", async (LoadGeneratorConfig config, WorkerOrchestrator wo, CancellationToken ct) => 
{ var job = await wo.StartLoadAsync(config, ct); return job != null ? Results.Created($"/api/control/jobs/{job.Id}", job) : Results.StatusCode(500); });

api.MapPost("/emergency-stop", async (IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{ await sm.EmergencyStopAsync(ct); await wo.EmergencyStopAsync(ct); return Results.Ok(new { Message = "Emergency stop executed" }); });

api.MapPost("/latency", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var target = payload.GetProperty("service").GetString() ?? "ProductService";
    var config = System.Text.Json.JsonSerializer.Deserialize<LatencyConfig>(payload.GetRawText(), new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.Latency, target, System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    string url = target switch { "OrderService" => "http://localhost:5002", "ProductService" => "http://localhost:5003", "DependencyService" => "http://localhost:5004", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, scenario, ct);
    return Results.Ok(scenario);
});

api.MapPost("/errors", async (System.Text.Json.JsonElement payload, IScenarioManager sm, WorkerOrchestrator wo, CancellationToken ct) => 
{
    var target = payload.GetProperty("service").GetString() ?? "ProductService";
    var config = System.Text.Json.JsonSerializer.Deserialize<ErrorConfig>(payload.GetRawText(), new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true });
    var scenario = new ChaosScenario(Guid.NewGuid().ToString(), ScenarioType.ErrorInjection, target, System.Text.Json.JsonSerializer.SerializeToElement(config), DateTimeOffset.UtcNow, null);
    await sm.AddScenarioAsync(scenario, ct);
    string url = target switch { "OrderService" => "http://localhost:5002", "ProductService" => "http://localhost:5003", "DependencyService" => "http://localhost:5004", _ => "" };
    if(url != "") await wo.SyncChaosToServiceAsync(url, scenario, ct);
    return Results.Ok(scenario);
});

api.MapPost("/incidents/start", async (System.Text.Json.JsonElement payload, IncidentManager im, CancellationToken ct) => 
{
    var type = payload.GetProperty("type").GetString();
    var duration = payload.GetProperty("durationSeconds").GetInt32();
    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    return Results.BadRequest();
});

api.MapGet("/incidents", (IncidentManager im) => Results.Ok(im.GetActiveIncidents()));
api.MapPost("/incidents/{id}/stop", async (string id, IncidentManager im, CancellationToken ct) => { await im.StopIncidentAsync(id, ct); return Results.Ok(); });

app.Run();