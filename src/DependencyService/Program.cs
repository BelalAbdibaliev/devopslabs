using DevOpsLabs.Chaos.Extensions;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddProblemDetails();
builder.Services.AddHealthChecks();
builder.Services.AddChaosEngine();

var app = builder.Build();

app.UseExceptionHandler();
app.UseChaosEngine();
app.MapHealthChecks("/health");
app.MapChaosSyncEndpoints();

app.MapGet("/api/external/status", () => Results.Ok(new { Status = "OK" }));
app.Run();