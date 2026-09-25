import re

with open("src/ControlService/Services/IncidentManager.cs", "r") as f:
    c = f.read()

new_logic = """
        var scenarios = new List<ChaosScenario>();
        if (req.Type == "cascading-failure") {
            scenarios.Add(new LatencyScenario { Service = "dependency-service", DelayMilliseconds = 5000, DurationSeconds = req.DurationSeconds });
        } else if (req.Type == "error-storm") {
            scenarios.Add(new ErrorScenario { Service = "product-service", StatusCode = 500, Probability = 0.3, DurationSeconds = req.DurationSeconds });
        } else if (req.Type == "combined-outage") {
            scenarios.Add(new LatencyScenario { Service = "order-service", DelayMilliseconds = 2000, DurationSeconds = req.DurationSeconds });
            scenarios.Add(new ErrorScenario { Service = "product-service", StatusCode = 503, Probability = 0.15, DurationSeconds = req.DurationSeconds });
            scenarios.Add(new RedisOutageScenario { DurationSeconds = req.DurationSeconds });
        } else {
            scenarios.Add(new LatencyScenario { Service = "dependency-service", DelayMilliseconds = 5000, DurationSeconds = req.DurationSeconds });
        }

        foreach(var s in scenarios) {
            _scenarioManager.AddScenario(s);
        }
"""
# Replace the switch or if-else blocks inside StartIncidentAsync
c = re.sub(r'var scenario = new LatencyScenario.*?_scenarioManager\.AddScenario\(scenario\);', new_logic, c, flags=re.DOTALL)

with open("src/ControlService/Services/IncidentManager.cs", "w") as f:
    f.write(c)
