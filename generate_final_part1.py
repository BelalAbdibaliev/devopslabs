import os

# 1. GitHub Actions CI/CD
os.makedirs(".github/workflows", exist_ok=True)
with open(".github/workflows/ci-cd.yml", "w") as f:
    f.write("""
name: DevOps Labs CI/CD

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository_owner }}/devopslabs

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup .NET
      uses: actions/setup-dotnet@v3
      with:
        dotnet-version: 10.0.x
    - name: Cache NuGet packages
      uses: actions/cache@v3
      with:
        path: ~/.nuget/packages
        key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
        restore-keys: |
          ${{ runner.os }}-nuget-
    - name: Restore dependencies
      run: dotnet restore DevOpsLabs.sln
    - name: Build
      run: dotnet build DevOpsLabs.sln --no-restore -c Release
    - name: Unit Tests
      run: dotnet test DevOpsLabs.sln --no-build --verbosity normal -c Release

  docker-build-push:
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        service: [Gateway, ControlService, OrderService, ProductService, NotificationService, DependencyService, CpuWorker, MemoryWorker, LoadGenerator]
    steps:
    - uses: actions/checkout@v3
    - name: Log in to the Container registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: src/${{ matrix.service }}/Dockerfile
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-${{ matrix.service }}:latest

  kubernetes-deploy:
    needs: docker-build-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Set up Helm
      uses: azure/setup-helm@v3
    - name: Set up Kubectl
      uses: azure/setup-kubectl@v3
    # Configure kubeconfig using secrets
    - name: Deploy to K8s
      run: |
        echo "Helm upgrade..."
        # helm upgrade --install devopslabs ./deploy/kubernetes/helm/devopslabs -n devopslabs --create-namespace
""")

# 2. k6 Scenarios
os.makedirs("tests/k6", exist_ok=True)
scenarios = {
    "normal.js": "vus: 10, duration: '1m'",
    "load.js": "vus: 100, duration: '5m'",
    "stress.js": "vus: 500, duration: '10m'",
    "spike.js": "stages: [{ duration: '10s', target: 100 }, { duration: '10s', target: 2000 }, { duration: '3m', target: 2000 }, { duration: '10s', target: 100 }]",
    "soak.js": "vus: 200, duration: '2h'",
    "ramp-up.js": "stages: [{ duration: '1m', target: 50 }, { duration: '2m', target: 200 }, { duration: '2m', target: 500 }, { duration: '1m', target: 0 }]"
}

for name, options in scenarios.items():
    with open(f"tests/k6/{name}", "w") as f:
        f.write(f"""
import http from 'k6/http';
import {{ sleep }} from 'k6';

export const options = {{
    {options}
}};

export default function () {{
    const res = http.post('http://localhost:5000/api/orders'); // Hits Gateway
    sleep(1);
}}
""".strip())

