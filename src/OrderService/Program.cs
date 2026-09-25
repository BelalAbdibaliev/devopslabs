using DevOpsLabs.Chaos.Extensions;
using Microsoft.Extensions.Http.Resilience;
using Polly;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddProblemDetails();
builder.Services.AddHealthChecks();
builder.Services.AddChaosEngine();

// RESILIENCE CONFIGURATION
// We do not retry blindly. Non-retryable errors (e.g., 400 Bad Request, 401 Unauthorized, 404 Not Found)
// should fail fast. Retrying them wastes resources and can cause a Retry Storm.
// Retryable errors (e.g., 503 Service Unavailable, 429 Too Many Requests, timeouts) are retried.
// To avoid Thundering Herd, we use Exponential Backoff with Jitter.
builder.Services.AddHttpClient("ProductClient", client => client.BaseAddress = new Uri("http://localhost:5003"))
    .AddStandardResilienceHandler(options => 
    {
        options.Retry.MaxRetryAttempts = 3;
        options.Retry.BackoffType = DelayBackoffType.Exponential;
        options.Retry.UseJitter = true; 
        
        // Circuit breaker opens after 50% failure rate over 10 seconds, shedding load to let downstream recover.
        options.CircuitBreaker.FailureRatio = 0.5;
        options.CircuitBreaker.SamplingDuration = TimeSpan.FromSeconds(10);
        
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(2); 
    });

builder.Services.AddHttpClient("DependencyClient", client => client.BaseAddress = new Uri("http://localhost:5004"))
    .AddStandardResilienceHandler();

var app = builder.Build();

app.UseExceptionHandler();
app.UseChaosEngine();
app.MapHealthChecks("/health");
app.MapChaosSyncEndpoints();

app.MapGet("/api/orders", async (IHttpClientFactory factory, CancellationToken ct) => 
{
    var pClient = factory.CreateClient("ProductClient");
    var res = await pClient.GetAsync("/api/products", ct);
    if (!res.IsSuccessStatusCode) return Results.StatusCode((int)res.StatusCode);
    
    return Results.Ok(new[] { new { Id = 1, Status = "Created", ProductInfo = "Fetched" } });
});

app.MapPost("/api/orders", () => Results.Created("/api/orders/2", new { Id = 2, Status = "Created" }));

app.Run();