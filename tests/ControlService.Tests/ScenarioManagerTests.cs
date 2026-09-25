using ControlService.Services;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;
namespace ControlService.Tests;
public class ScenarioManagerTests {
    private readonly IScenarioManager _sut;
    private readonly InMemoryChaosStateProvider _stateProvider = new();
    public ScenarioManagerTests() { _sut = new ScenarioManager(_stateProvider, new Mock<ILogger<ScenarioManager>>().Object); }
    [Fact] public async Task AddScenario_ShouldCreateIdAndStore() {
        var result = await _sut.AddScenarioAsync(new ChaosScenario("", ScenarioType.Latency, "OrderService", null, DateTimeOffset.UtcNow, null));
        Assert.NotNull(result.Id);
    }
}
