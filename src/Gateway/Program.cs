using DevOpsLabs.Chaos.Observability;
var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("Gateway");
builder.Services.AddDevOpsLabsTelemetry("Gateway");
builder.Services.AddHttpLogging(o => { });
var app = builder.Build();
app.UseHttpLogging();
app.UseDevOpsLabsMetrics();

app.MapGet("/", () => "Hello World!");

app.Run();
