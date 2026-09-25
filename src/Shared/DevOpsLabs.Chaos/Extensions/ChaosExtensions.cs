using DevOpsLabs.Chaos.Middleware;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.Extensions.DependencyInjection;

namespace DevOpsLabs.Chaos.Extensions;

public static class ChaosExtensions
{
    public static IServiceCollection AddChaosEngine(this IServiceCollection services)
    {
        services.AddSingleton<IChaosStateProvider, InMemoryChaosStateProvider>();
        return services;
    }

    public static IApplicationBuilder UseChaosEngine(this IApplicationBuilder app)
    {
        return app.UseMiddleware<ChaosMiddleware>();
    }

    public static IEndpointRouteBuilder MapChaosSyncEndpoints(this IEndpointRouteBuilder endpoints)
    {
        endpoints.MapPost("/api/chaos/sync", async (ChaosScenario scenario, IChaosStateProvider state) => 
        {
            await state.AddOrUpdateScenarioAsync(scenario);
            return Results.Ok();
        });

        endpoints.MapPost("/api/chaos/clear", async (IChaosStateProvider state) => 
        {
            await state.ResetAsync();
            return Results.Ok();
        });

        return endpoints;
    }
}