using MemoryWorker.Services;
using DevOpsLabs.Chaos.Models;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<MemoryStressEngine>();
builder.Services.AddHttpLogging(o => { });
var app = builder.Build();
app.UseHttpLogging();

app.MapGet("/api/jobs", (MemoryStressEngine engine) => Results.Ok(engine.GetJobs()));
app.MapPost("/api/jobs", (MemoryStressConfig config, MemoryStressEngine engine) => Results.Ok(engine.StartJob(config)));
app.MapDelete("/api/jobs/{id}", (string id, MemoryStressEngine engine) => engine.StopJob(id) ? Results.NoContent() : Results.NotFound());
app.MapPost("/api/emergency-stop", (MemoryStressEngine engine) => { engine.StopAll(); return Results.Ok(); });

app.Run();