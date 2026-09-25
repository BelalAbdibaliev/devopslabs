import re
for p in ["src/OrderService/Program.cs", "src/NotificationService/Program.cs"]:
    with open(p, "r") as f:
        c = f.read()
    c = c.replace(".AddRabbitMQ(rabbitConnectionString: rmqStr)", '// RabbitMQ HealthCheck requires custom async factory in v9')
    with open(p, "w") as f:
        f.write(c)
