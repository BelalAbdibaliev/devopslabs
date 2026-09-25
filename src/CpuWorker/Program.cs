using CpuWorker.Services;
using DevOpsLabs.Chaos.Models;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<CpuStressEngine>();
var app = builder.Build();

app.MapGet("/api/jobs", (CpuStressEngine engine) => Results.Ok(engine.GetJobs()));
app.MapPost("/api/jobs", (CpuStressConfig config, CpuStressEngine engine) => Results.Ok(engine.StartJob(config)));
app.MapDelete("/api/jobs/{id}", (string id, CpuStressEngine engine) => engine.StopJob(id) ? Results.NoContent() : Results.NotFound());
app.MapPost("/api/emergency-stop", (CpuStressEngine engine) => { engine.StopAll(); return Results.Ok(); });

app.Run();