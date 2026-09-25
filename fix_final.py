import re

# Fix NotificationService CSPROJ to Web SDK
with open("src/NotificationService/NotificationService.csproj", "r") as f:
    c = f.read()
c = c.replace('Sdk="Microsoft.NET.Sdk.Worker"', 'Sdk="Microsoft.NET.Sdk.Web"')
with open("src/NotificationService/NotificationService.csproj", "w") as f:
    f.write(c)

# Fix AddRabbitMQ
for p in ["src/OrderService/Program.cs", "src/NotificationService/Program.cs"]:
    with open(p, "r") as f:
        c = f.read()
    c = c.replace("AddRabbitMQ(rmqStr)", 'AddRabbitMQ(rabbitConnectionString: rmqStr)')
    with open(p, "w") as f:
        f.write(c)

