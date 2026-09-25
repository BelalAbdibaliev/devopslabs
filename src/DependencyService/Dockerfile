FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ["src/DependencyService/DependencyService.csproj", "src/DependencyService/"]
COPY ["src/Shared/DevOpsLabs.Chaos/DevOpsLabs.Chaos.csproj", "src/Shared/DevOpsLabs.Chaos/"]
RUN dotnet restore "src/DependencyService/DependencyService.csproj"
COPY src/DependencyService/ src/DependencyService/
COPY src/Shared/DevOpsLabs.Chaos/ src/Shared/DevOpsLabs.Chaos/
WORKDIR "/src/src/DependencyService"
RUN dotnet publish "DependencyService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080
# Non-root user for security
RUN adduser -u 1000 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
ENV ASPNETCORE_URLS=http://+:8080
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "DependencyService.dll"]