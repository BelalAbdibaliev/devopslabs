import os

os.makedirs("src/ControlService/wwwroot", exist_ok=True)
with open("src/ControlService/wwwroot/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Labs - Control Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #e0e0e0; }
        .card { background-color: #1e1e1e; border: 1px solid #333; }
        .card-header { background-color: #2c2c2c; border-bottom: 1px solid #333; font-weight: bold; }
        .btn { border-radius: 2px; }
        .log-box { background: #000; color: #0f0; font-family: monospace; height: 150px; overflow-y: scroll; padding: 10px; font-size: 12px; }
    </style>
</head>
<body>
<div class="container py-4">
    <h2 class="mb-4 text-center text-primary">DevOps Labs - Control Center</h2>
    
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header text-danger">Emergency Controls</div>
                <div class="card-body text-center">
                    <button class="btn btn-outline-danger mx-2" onclick="postAction('/api/control/reset', {})">Reset All Scenarios</button>
                    <button class="btn btn-danger mx-2" onclick="postAction('/api/control/emergency-stop', {})">EMERGENCY STOP (Panic)</button>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <!-- CPU Stress -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header">CPU Stress</div>
                <div class="card-body">
                    <input type="number" id="cpuTarget" class="form-control mb-2" value="90" placeholder="Target CPU %">
                    <input type="number" id="cpuDuration" class="form-control mb-3" value="300" placeholder="Duration (s)">
                    <button class="btn btn-warning w-100" onclick="startCpu()">Start CPU Stress</button>
                </div>
            </div>
        </div>

        <!-- Memory Stress -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header">Memory Pressure</div>
                <div class="card-body">
                    <input type="number" id="memMb" class="form-control mb-2" value="256" placeholder="Target Megabytes">
                    <input type="number" id="memDuration" class="form-control mb-3" value="300" placeholder="Duration (s)">
                    <button class="btn btn-warning w-100" onclick="startMem()">Start Memory Pressure</button>
                </div>
            </div>
        </div>

        <!-- DB Stress -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header">Database Degradation</div>
                <div class="card-body">
                    <input type="number" id="dbQps" class="form-control mb-2" value="1000" placeholder="Queries/sec">
                    <select id="dbType" class="form-control mb-3"><option>Select</option><option>Insert</option><option>Update</option></select>
                    <button class="btn btn-warning w-100" onclick="startDb()">Start DB Stress</button>
                </div>
            </div>
        </div>

        <!-- Queue Backlog -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header">RabbitMQ Backlog</div>
                <div class="card-body">
                    <input type="number" id="queueRps" class="form-control mb-2" value="5000" placeholder="Produce msg/sec">
                    <button class="btn btn-warning w-100 mb-2" onclick="startQueueLoad()">Flood Queue (Producer)</button>
                    <button class="btn btn-danger w-100" onclick="stopQueueConsumers()">Stall Consumers</button>
                </div>
            </div>
        </div>

        <!-- Redis Outage -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header">Redis Outage</div>
                <div class="card-body">
                    <input type="number" id="redisDuration" class="form-control mb-3" value="120" placeholder="Duration (s)">
                    <button class="btn btn-danger w-100" onclick="startRedisOutage()">Simulate Redis Failure</button>
                </div>
            </div>
        </div>

        <!-- Incidents -->
        <div class="col-md-4">
            <div class="card h-100">
                <div class="card-header bg-danger text-white">Production Incidents</div>
                <div class="card-body">
                    <select id="incidentSelect" class="form-control mb-3">
                        <option value="cascading-failure">Cascading Failure (Incident 9)</option>
                        <option value="error-storm">Error Storm (Incident 5)</option>
                        <option value="combined-outage">Combined Outage (Incident 10)</option>
                    </select>
                    <button class="btn btn-danger w-100" onclick="startIncident()">Trigger Incident</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">Action Logs</div>
                <div class="card-body log-box" id="logs"></div>
            </div>
        </div>
    </div>
</div>

<script>
    function log(msg) {
        const box = document.getElementById('logs');
        box.innerHTML += `[${new Date().toISOString().split('T')[1].split('.')[0]}] ${msg}<br>`;
        box.scrollTop = box.scrollHeight;
    }

    async function postAction(url, body) {
        log(`POST ${url} - ${JSON.stringify(body)}`);
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            log(`Response: ${res.status}`);
        } catch (e) {
            log(`Error: ${e.message}`);
        }
    }

    function startCpu() { postAction('/api/control/cpu', { service: 'cpu-worker', targetPercentage: +document.getElementById('cpuTarget').value, durationSeconds: +document.getElementById('cpuDuration').value }); }
    function startMem() { postAction('/api/control/memory', { megabytes: +document.getElementById('memMb').value, durationSeconds: +document.getElementById('memDuration').value }); }
    function startDb() { postAction('/api/control/db/stress', { queriesPerSecond: +document.getElementById('dbQps').value, type: document.getElementById('dbType').value, durationSeconds: 120 }); }
    function startQueueLoad() { postAction('/api/control/queue/load', { messagesPerSecond: +document.getElementById('queueRps').value, durationSeconds: 60 }); }
    function stopQueueConsumers() { postAction('/api/control/queue/consumer', { stopConsumers: true, durationSeconds: 120 }); }
    function startRedisOutage() { postAction('/api/control/redis/outage', { durationSeconds: +document.getElementById('redisDuration').value }); }
    function startIncident() { postAction('/api/control/incidents/start', { type: document.getElementById('incidentSelect').value, durationSeconds: 300 }); }
</script>
</body>
</html>
""")

with open("src/ControlService/Program.cs", "r") as f:
    c = f.read()

if "app.UseDefaultFiles();" not in c:
    c = c.replace("var app = builder.Build();", "var app = builder.Build();\napp.UseDefaultFiles();\napp.UseStaticFiles();")

with open("src/ControlService/Program.cs", "w") as f:
    f.write(c)
