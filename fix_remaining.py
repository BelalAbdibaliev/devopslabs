import re

# Fix NotificationService CSPROJ to Web SDK
with open("src/NotificationService/NotificationService.csproj", "r") as f:
    c = f.read()
c = c.replace('Sdk="Microsoft.NET.Sdk"', 'Sdk="Microsoft.NET.Sdk.Web"')
with open("src/NotificationService/NotificationService.csproj", "w") as f:
    f.write(c)

# Fix AddRabbitMQ health checks (v9 uses string instead of Uri)
for p in ["src/OrderService/Program.cs", "src/NotificationService/Program.cs"]:
    with open(p, "r") as f:
        c = f.read()
    c = c.replace("AddRabbitMQ(new Uri(rmqStr))", "AddRabbitMQ(rmqStr)")
    with open(p, "w") as f:
        f.write(c)

# Fix ControlService \n
with open("src/ControlService/Program.cs", "r") as f:
    c = f.read()
c = c.replace("\\napp.Run();", "\napp.Run();")
with open("src/ControlService/Program.cs", "w") as f:
    f.write(c)

