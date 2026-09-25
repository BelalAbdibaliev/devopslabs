using DevOpsLabs.Chaos.Observability;
using System.Text.Json;
using DevOpsLabs.Chaos.Decorators;
using DevOpsLabs.Chaos.Extensions;
using DevOpsLabs.Chaos.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Caching.Distributed;
using ProductService.Data;

var builder = WebApplication.CreateBuilder(args);
builder.Logging.ClearProviders();
builder.Logging.AddDevOpsLabsLogging("ProductService");
builder.Services.AddDevOpsLabsTelemetry("ProductService");

builder.Services.AddProblemDetails();
builder.Services.AddChaosEngine();

// PostgreSQL Connection Pooling
var connStr = builder.Configuration.GetConnectionString("DefaultConnection") ?? "Host=localhost;Database=products;Username=postgres;Password=postgres";
builder.Services.AddDbContextPool<ProductDbContext>(options => options.UseNpgsql(connStr));

// Redis Cache (wrapped with Chaos)
var redisConn = builder.Configuration.GetConnectionString("Redis") ?? "localhost:6379";
builder.Services.AddStackExchangeRedisCache(options => { options.Configuration = redisConn; });
var descriptor = builder.Services.FirstOrDefault(d => d.ServiceType == typeof(IDistributedCache));
if (descriptor != null)
{
    builder.Services.Remove(descriptor);
    builder.Services.Add(new ServiceDescriptor(typeof(IDistributedCache), sp => 
    {
        var inner = (IDistributedCache)ActivatorUtilities.CreateInstance(sp, descriptor.ImplementationType!);
        return ActivatorUtilities.CreateInstance<DevOpsLabs.Chaos.Decorators.ChaosCache>(sp, inner);
    }, descriptor.Lifetime));
}


builder.Services.AddHealthChecks()
    .AddNpgSql(connStr)
    .AddRedis(redisConn);

var app = builder.Build();
app.UseDevOpsLabsMetrics();

// Seed Database
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ProductDbContext>();
    await db.Database.EnsureCreatedAsync();
    if (!await db.Products.AnyAsync())
    {
        db.Products.AddRange(
            new Product { Name = "Laptop", Price = 1500, Stock = 10, Category = "Electronics" },
            new Product { Name = "Phone", Price = 800, Stock = 50, Category = "Electronics" },
            new Product { Name = "Desk", Price = 300, Stock = 5, Category = "Furniture" }
        );
        await db.SaveChangesAsync();
    }
}

app.UseExceptionHandler();
app.UseChaosEngine();
app.MapHealthChecks("/health");
app.MapChaosSyncEndpoints();

app.MapGet("/api/products/{id}", async (int id, ProductDbContext db, IDistributedCache cache, ILogger<Program> logger) =>
{
    string cacheKey = $"product_{id}";
    string? cachedData = null;
    
    try {
        cachedData = await cache.GetStringAsync(cacheKey);
    } catch (Exception ex) {
        logger.LogWarning(ex, "Cache unavailable, falling back to database");
    }

    if (!string.IsNullOrEmpty(cachedData))
    {
        logger.LogInformation("Cache hit for {Key}", cacheKey);
        return Results.Ok(JsonSerializer.Deserialize<Product>(cachedData));
    }

    logger.LogInformation("Cache miss for {Key}. Simulating heavy DB query...", cacheKey);
    await Task.Delay(200); // Simulate cache stampede impact when cache misses

    var product = await db.Products.FindAsync(id);
    if (product == null) return Results.NotFound();

    try {
        await cache.SetStringAsync(cacheKey, JsonSerializer.Serialize(product), new DistributedCacheEntryOptions { AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5) });
    } catch { } // Ignore cache write failures during outage

    return Results.Ok(product);
});

// DB Stress Endpoint
app.MapPost("/api/db/stress", (DbStressConfig config, IServiceProvider sp) => 
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
                    using var scope = sp.CreateScope();
                    var db = scope.ServiceProvider.GetRequiredService<ProductDbContext>();
                    if (config.Type == "Select") {
                        await db.Products.AsNoTracking().Where(p => p.Category == "Electronics").ToListAsync(cts.Token);
                    } else if (config.Type == "Insert") {
                        db.Products.Add(new Product { Name = "Stress Item", Price = 1, Stock = 1, Category = "Stress" });
                        await db.SaveChangesAsync(cts.Token);
                    } else if (config.Type == "Update") {
                        var p = await db.Products.FirstOrDefaultAsync(cts.Token);
                        if (p != null) { p.Stock++; await db.SaveChangesAsync(cts.Token); }
                    }
                } catch { } 
                finally { sem.Release(); }
            });
        }
    });
    return Results.Accepted();
});

app.Run();