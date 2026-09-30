import os

replacements = {
    "http://localhost:5002": "http://orderservice:8080",
    "http://localhost:5003": "http://productservice:8080",
    "http://localhost:5004": "http://dependencyservice:8080",
    "http://localhost:5005": "http://cpuworker:8080",
    "http://localhost:5006": "http://memoryworker:8080",
    "http://localhost:5007": "http://loadgenerator:8080",
    "http://localhost:5008": "http://notificationservice:8080"
}

files_to_fix = [
    "src/ControlService/Program.cs",
    "src/ControlService/Services/WorkerOrchestrator.cs",
    "src/ControlService/Services/IncidentManager.cs"
]

for fpath in files_to_fix:
    if os.path.exists(fpath):
        with open(fpath, "r") as f:
            content = f.read()
        
        for k, v in replacements.items():
            content = content.replace(k, v)
            
        with open(fpath, "w") as f:
            f.write(content)

