using System.Text.Json;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;

namespace DevOpsLabs.Chaos.Middleware;

public class ChaosMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ChaosMiddleware> _logger;

    public ChaosMiddleware(RequestDelegate next, ILogger<ChaosMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, IChaosStateProvider state)
    {
        if (context.Request.Path.StartsWithSegments("/api/chaos") || context.Request.Path.StartsWithSegments("/health"))
        {
            await _next(context);
            return;
        }

        var scenarios = await state.GetActiveScenariosAsync(context.RequestAborted);

        foreach (var s in scenarios)
        {
            if (s.Type == ScenarioType.Latency)
            {
                var config = s.Parameters?.Deserialize<LatencyConfig>(new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                if (config != null && Random.Shared.NextDouble() <= config.Probability)
                {
                    int delay = config.DelayMilliseconds > 0 
                        ? config.DelayMilliseconds 
                        : Random.Shared.Next(config.MinDelayMilliseconds, config.MaxDelayMilliseconds);
                    
                    _logger.LogWarning("Injecting latency of {Delay}ms", delay);
                    await Task.Delay(delay, context.RequestAborted);
                }
            }
            else if (s.Type == ScenarioType.ErrorInjection)
            {
                var config = s.Parameters?.Deserialize<ErrorConfig>(new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                if (config != null && Random.Shared.NextDouble() <= config.Probability)
                {
                    _logger.LogWarning("Injecting HTTP Error {StatusCode}", config.StatusCode);
                    context.Response.StatusCode = config.StatusCode;
                    return; 
                }
            }
        }

        await _next(context);
    }
}