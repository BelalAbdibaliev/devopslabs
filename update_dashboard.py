import os

html_content = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Labs | Control Center</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #0d1117; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .navbar { background-color: #161b22; border-bottom: 1px solid #30363d; }
        .card { background-color: #21262d; border: 1px solid #30363d; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); border-color: #8b949e; }
        .card-header { background-color: transparent; border-bottom: 1px solid #30363d; font-weight: 600; padding: 15px 20px; }
        .card-body { padding: 20px; }
        .help-text { font-size: 0.85rem; color: #8b949e; margin-bottom: 15px; min-height: 40px; }
        
        .terminal { background-color: #010409; border: 1px solid #30363d; border-radius: 6px; padding: 15px; height: 350px; overflow-y: auto; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.9rem; line-height: 1.5; }
        .log-time { color: #8b949e; }
        .log-info { color: #58a6ff; }
        .log-success { color: #3fb950; }
        .log-error { color: #f85149; }
        .log-detail { color: #8b949e; margin-left: 15px; border-left: 2px solid #30363d; padding-left: 10px; }
        
        .btn-danger-outline { border: 1px solid #f85149; color: #f85149; background: transparent; }
        .btn-danger-outline:hover { background: #f85149; color: white; }
    </style>
</head>
<body>

<nav class="navbar navbar-dark mb-4 shadow-sm">
    <div class="container-fluid px-4">
        <a class="navbar-brand" href="#"><i class="bi bi-activity text-danger me-2"></i> DevOps Laboratory Control Center</a>
        <div class="d-flex">
            <a href="http://localhost:3000" target="_blank" class="btn btn-outline-warning btn-sm me-2"><i class="bi bi-graph-up"></i> Open Grafana</a>
        </div>
    </div>
</nav>

<div class="container-fluid px-4 pb-5">
    
    <!-- Emergency Row -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card border-danger" style="background-color: rgba(248, 81, 73, 0.05);">
                <div class="card-body d-flex justify-content-between align-items-center py-3">
                    <div>
                        <h5 class="text-danger mb-1"><i class="bi bi-exclamation-triangle-fill me-2"></i> Emergency Recovery Controls</h5>
                        <p class="text-muted mb-0 small">Use these if the system is completely locked up and you need to abort all chaos scenarios.</p>
                    </div>
                    <div>
                        <button class="btn btn-outline-light me-2" onclick="postAction('/api/control/reset', {}, 'Soft Reset', 'Clearing all active chaos scenarios safely.')">
                            <i class="bi bi-arrow-counterclockwise"></i> Reset Scenarios
                        </button>
                        <button class="btn btn-danger" onclick="postAction('/api/control/emergency-stop', {}, 'EMERGENCY STOP', 'Hard aborting all workers and clearing states!')">
                            <i class="bi bi-stop-octagon-fill"></i> Panic Stop
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <!-- Main Controls (Left Column) -->
        <div class="col-lg-8">
            <h5 class="mb-3"><i class="bi bi-tools"></i> Targeted Chaos Generators</h5>
            <div class="row g-4">
                
                <!-- CPU -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header text-warning"><i class="bi bi-cpu me-2"></i>CPU Starvation</div>
                        <div class="card-body">
                            <div class="help-text">Simulates a runaway process burning CPU cycles on the CpuWorker service.</div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Target CPU %</span>
                                <input type="number" id="cpuTarget" class="form-control bg-dark text-light border-secondary" value="95">
                            </div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Duration (sec)</span>
                                <input type="number" id="cpuDuration" class="form-control bg-dark text-light border-secondary" value="300">
                            </div>
                            <button class="btn btn-warning w-100" onclick="startCpu()"><i class="bi bi-play-fill"></i> Start CPU Burn</button>
                        </div>
                    </div>
                </div>

                <!-- Memory -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header text-info"><i class="bi bi-memory me-2"></i>Memory Leak (OOM)</div>
                        <div class="card-body">
                            <div class="help-text">Allocates unmanaged byte arrays. Requests > 128MB will trigger K8s OOMKilled.</div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Target MB</span>
                                <input type="number" id="memMb" class="form-control bg-dark text-light border-secondary" value="256">
                            </div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Duration (sec)</span>
                                <input type="number" id="memDuration" class="form-control bg-dark text-light border-secondary" value="300">
                            </div>
                            <button class="btn btn-info w-100 text-dark" onclick="startMem()"><i class="bi bi-play-fill"></i> Start Memory Leak</button>
                        </div>
                    </div>
                </div>

                <!-- RabbitMQ -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header" style="color: #ff6600;"><i class="bi bi-envelope-x me-2"></i>RabbitMQ Backlog</div>
                        <div class="card-body">
                            <div class="help-text">Floods the message broker or stalls consumers to test KEDA auto-scaling.</div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Produce Msg/s</span>
                                <input type="number" id="queueRps" class="form-control bg-dark text-light border-secondary" value="5000">
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-warning w-50" onclick="startQueueLoad()">Flood Queue</button>
                                <button class="btn btn-outline-danger w-50" onclick="stopQueueConsumers()">Stall Consumers</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- DB & Redis -->
                <div class="col-md-6">
                    <div class="card h-100">
                        <div class="card-header text-primary"><i class="bi bi-database-exclamation me-2"></i>Database & Cache</div>
                        <div class="card-body">
                            <div class="help-text">Stresses Postgres DB queries or simulates a hard Redis outage (Cache Stampede).</div>
                            <div class="input-group mb-3">
                                <span class="input-group-text bg-dark text-light border-secondary">Queries/sec</span>
                                <input type="number" id="dbQps" class="form-control bg-dark text-light border-secondary" value="1000">
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-primary w-50" onclick="startDb()">Stress DB</button>
                                <button class="btn btn-outline-danger w-50" onclick="startRedisOutage()">Kill Redis</button>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <!-- Right Column (Incidents & Logs) -->
        <div class="col-lg-4">
            
            <h5 class="mb-3"><i class="bi bi-fire text-danger"></i> Complex Incidents</h5>
            <div class="card border-danger mb-4">
                <div class="card-body">
                    <p class="text-muted small mb-3">Pre-packaged production outages. Find the root cause in Grafana!</p>
                    <select id="incidentSelect" class="form-select bg-dark text-light border-secondary mb-3">
                        <option value="cascading-failure">💥 Cascading Failure (Gateway Timeout)</option>
                        <option value="error-storm">🌧️ Error Storm (Random 500s)</option>
                        <option value="combined-outage">🔥 Combined Outage (DB + Cache)</option>
                    </select>
                    <button class="btn btn-danger w-100 fw-bold" onclick="startIncident()">
                        <i class="bi bi-lightning-charge-fill"></i> Trigger Incident
                    </button>
                </div>
            </div>

            <h5 class="mb-3"><i class="bi bi-terminal"></i> Execution Logs</h5>
            <div class="terminal" id="logs">
                <span class="log-time">[System]</span> <span class="log-info">Control UI Initialized. Ready for commands.</span><br>
            </div>
            <button class="btn btn-sm btn-outline-secondary mt-2 w-100" onclick="document.getElementById('logs').innerHTML=''">Clear Logs</button>

        </div>
    </div>
</div>

<script>
    function addLog(message, type = 'info') {
        const box = document.getElementById('logs');
        const time = new Date().toISOString().split('T')[1].split('.')[0];
        
        let colorClass = 'log-info';
        let prefix = 'ℹ️';
        if(type === 'success') { colorClass = 'log-success'; prefix = '✅'; }
        if(type === 'error') { colorClass = 'log-error'; prefix = '❌'; }
        if(type === 'detail') { colorClass = 'log-detail'; prefix = '↳'; }
        if(type === 'warning') { colorClass = 'text-warning'; prefix = '⚠️'; }

        if(type === 'detail') {
            box.innerHTML += `<div class="${colorClass}">${prefix} ${message}</div>`;
        } else {
            box.innerHTML += `<div><span class="log-time">[${time}]</span> <span class="${colorClass}">${prefix} ${message}</span></div>`;
        }
        
        box.scrollTop = box.scrollHeight;
    }

    async function postAction(url, body, title, description) {
        addLog(`Initiating: ${title}`, 'info');
        if (description) addLog(description, 'detail');
        addLog(`POST ${url}`, 'detail');
        
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            
            if (res.ok) {
                addLog(`Command accepted by orchestration engine (HTTP ${res.status})`, 'success');
            } else {
                addLog(`Command rejected! Server returned HTTP ${res.status}`, 'error');
            }
        } catch (e) {
            addLog(`Network Failure: ${e.message}. Is ControlService reachable?`, 'error');
        }
        addLog('---', 'detail');
    }

    // Wrappers
    function startCpu() { 
        const target = +document.getElementById('cpuTarget').value;
        const dur = +document.getElementById('cpuDuration').value;
        postAction('/api/control/cpu', { service: 'cpu-worker', targetPercentage: target, durationSeconds: dur }, 'CPU Starvation', `Requesting ${target}% utilization for ${dur}s`); 
    }
    
    function startMem() { 
        const mb = +document.getElementById('memMb').value;
        const dur = +document.getElementById('memDuration').value;
        postAction('/api/control/memory', { megabytes: mb, durationSeconds: dur }, 'Memory Leak', `Allocating ${mb} MB for ${dur}s`); 
    }
    
    function startDb() { 
        const qps = +document.getElementById('dbQps').value;
        postAction('/api/control/db/stress', { queriesPerSecond: qps, type: 'Select', durationSeconds: 120 }, 'DB Stress', `Sending ${qps} Queries/sec`); 
    }
    
    function startQueueLoad() { 
        const msg = +document.getElementById('queueRps').value;
        postAction('/api/control/queue/load', { messagesPerSecond: msg, durationSeconds: 60 }, 'Queue Flood', `Publishing ${msg} msg/s to RabbitMQ`); 
    }
    
    function stopQueueConsumers() { 
        postAction('/api/control/queue/consumer', { stopConsumers: true, durationSeconds: 120 }, 'Consumer Stall', 'Halting all RabbitMQ workers'); 
    }
    
    function startRedisOutage() { 
        postAction('/api/control/redis/outage', { durationSeconds: 120 }, 'Redis Outage', 'Simulating Cache Stampede'); 
    }
    
    function startIncident() { 
        const inc = document.getElementById('incidentSelect').value;
        postAction('/api/control/incidents/start', { type: inc, durationSeconds: 300 }, `Complex Incident: ${inc}`, 'Deploying multi-service chaos scenario'); 
    }
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open("src/ControlService/wwwroot/index.html", "w") as f:
    f.write(html_content)

