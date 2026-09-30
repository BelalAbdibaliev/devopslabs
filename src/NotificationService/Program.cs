using DevOpsLabs.Chaos.Observability;
using DevOpsLabs.Chaos.Extensions;
using NotificationService.Services;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("NotificationService");
builder.Services.AddDevOpsLabsTelemetry("NotificationService");

builder.Services.AddProblemDetails();
builder.Services.AddChaosEngine();

builder.Services.AddHostedService<RabbitMqConsumer>();

var rmqStr = builder.Configuration.GetConnectionString("RabbitMQ") ?? "amqp://guest:guest@localhost:5672";
builder.Services.AddHealthChecks();
    // RabbitMQ HealthCheck requires custom async factory in v9;

builder.Services.AddHttpLogging(o => { });
var app = builder.Build();
app.UseHttpLogging();

app.UseExceptionHandler();
app.UseChaosEngine();
app.MapHealthChecks("/health");
app.MapChaosSyncEndpoints();

app.Run();