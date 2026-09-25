FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ["src/CpuWorker/CpuWorker.csproj", "src/CpuWorker/"]
COPY ["src/Shared/DevOpsLabs.Chaos/DevOpsLabs.Chaos.csproj", "src/Shared/DevOpsLabs.Chaos/"]
RUN dotnet restore "src/CpuWorker/CpuWorker.csproj"
COPY src/CpuWorker/ src/CpuWorker/
COPY src/Shared/DevOpsLabs.Chaos/ src/Shared/DevOpsLabs.Chaos/
WORKDIR "/src/src/CpuWorker"
RUN dotnet publish "CpuWorker.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080
# Non-root user for security
RUN adduser -u 1000 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
ENV ASPNETCORE_URLS=http://+:8080
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "CpuWorker.dll"]