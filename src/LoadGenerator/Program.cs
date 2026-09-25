using LoadGenerator.Services;
using DevOpsLabs.Chaos.Models;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHttpClient();
builder.Services.AddSingleton<LoadEngine>();
var app = builder.Build();

app.MapGet("/api/jobs", (LoadEngine engine) => Results.Ok(engine.GetJobs()));
app.MapPost("/api/jobs", (LoadGeneratorConfig config, LoadEngine engine) => Results.Ok(engine.StartJob(config)));
app.MapDelete("/api/jobs/{id}", (string id, LoadEngine engine) => engine.StopJob(id) ? Results.NoContent() : Results.NotFound());
app.MapPost("/api/emergency-stop", (LoadEngine engine) => { engine.StopAll(); return Results.Ok(); });

app.Run();