using DevOpsLabs.Chaos.Observability;
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("Gateway");
builder.Services.AddDevOpsLabsTelemetry("Gateway");
var app = builder.Build();
app.UseDevOpsLabsMetrics();

app.MapGet("/", () => "Hello World!");

app.Run();
