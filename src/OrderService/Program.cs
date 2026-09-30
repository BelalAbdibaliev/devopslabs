using DevOpsLabs.Chaos.Observability;
using DevOpsLabs.Chaos.Extensions;
using DevOpsLabs.Chaos.Models;
using Microsoft.EntityFrameworkCore;
using OrderService.Data;
using OrderService.Services;
using Microsoft.Extensions.Http.Resilience;
using Polly;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("OrderService");
builder.Services.AddDevOpsLabsTelemetry("OrderService");

builder.Services.AddProblemDetails();
builder.Services.AddChaosEngine();

var connStr = builder.Configuration.GetConnectionString("DefaultConnection") ?? "Host=localhost;Database=orders;Username=postgres;Password=postgres";
builder.Services.AddDbContextPool<OrderDbContext>(options => options.UseNpgsql(connStr));

builder.Services.AddSingleton<RabbitMqPublisher>();

builder.Services.AddHttpClient("ProductClient", client => client.BaseAddress = new Uri("http://localhost:5003"))
    .AddStandardResilienceHandler(options => {
        options.Retry.MaxRetryAttempts = 3;
        options.Retry.BackoffType = DelayBackoffType.Exponential;
        options.Retry.UseJitter = true;
        options.CircuitBreaker.FailureRatio = 0.5;
        options.CircuitBreaker.SamplingDuration = TimeSpan.FromSeconds(10);
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(2);
    });

var rmqStr = builder.Configuration.GetConnectionString("RabbitMQ") ?? "amqp://guest:guest@localhost:5672";
builder.Services.AddHealthChecks()
    .AddNpgSql(connStr);
    // RabbitMQ HealthCheck requires custom async factory in v9;

builder.Services.AddHttpLogging(o => { });
var app = builder.Build();
app.UseHttpLogging();
app.UseDevOpsLabsMetrics();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<OrderDbContext>();
    await db.Database.EnsureCreatedAsync();
}

app.UseExceptionHandler();
app.UseChaosEngine();
app.MapHealthChecks("/health");
app.MapChaosSyncEndpoints();

app.MapPost("/api/orders", async (OrderDbContext db, RabbitMqPublisher rmq) => 
{
    var order = new Order { CustomerId = Random.Shared.Next(1, 1000), TotalAmount = Random.Shared.Next(10, 500) };
    db.Orders.Add(order);
    await db.SaveChangesAsync();
    
    try {
        await rmq.PublishAsync($"OrderCreated: {order.Id}");
    } catch { /* Swallow for chaos demo */ }
    
    return Results.Created($"/api/orders/{order.Id}", order);
});

// RabbitMQ Load Generator
app.MapPost("/api/queue/load", (QueueLoadConfig config, RabbitMqPublisher rmq) => 
{
    _ = Task.Run(async () => 
    {
        using var timer = new PeriodicTimer(TimeSpan.FromMilliseconds(1000.0 / config.MessagesPerSecond));
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(config.DurationSeconds));
        while (await timer.WaitForNextTickAsync(cts.Token) && !cts.Token.IsCancellationRequested)
        {
            _ = rmq.PublishAsync($"StressMessage: {Guid.NewGuid()}");
        }
    });
    return Results.Accepted();
});

// DB Stress Endpoint
app.MapPost("/api/db/stress", (DbStressConfig config) => 
{
    _ = Task.Run(async () => 
    {
        using var timer = new PeriodicTimer(TimeSpan.FromMilliseconds(1000.0 / config.QueriesPerSecond));
        var cts = new CancellationTokenSource(TimeSpan.FromSeconds(config.DurationSeconds));
        var sem = new SemaphoreSlim(config.Concurrency);

        while (await timer.WaitForNextTickAsync(cts.Token) && !cts.Token.IsCancellationRequested)
        {
            await sem.WaitAsync();
            _ = Task.Run(async () => 
            {
                try {
                    using var scope = app.Services.CreateScope();
                    var db = scope.ServiceProvider.GetRequiredService<OrderDbContext>();
                    if (config.Type == "Insert") {
                        db.Orders.Add(new Order { CustomerId = 999, TotalAmount = 99.99M });
                        await db.SaveChangesAsync(cts.Token);
                    }
                } catch { } 
                finally { sem.Release(); }
            });
        }
    });
    return Results.Accepted();
});

app.Run();