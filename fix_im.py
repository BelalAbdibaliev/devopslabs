import os

im_file = "src/ControlService/Services/IncidentManager.cs"
with open(im_file, "r") as f:
    content = f.read()

content = content.replace("ScenarioType.Error", "ScenarioType.ErrorInjection")
content = content.replace("JsonSerializer.SerializeToElement(new DependencyConfig(\"Redis\", DependencyFailureType.Unavailable))", "null")

with open(im_file, "w") as f:
    f.write(content)

