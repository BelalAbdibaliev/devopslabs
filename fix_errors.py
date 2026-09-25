import re

# Fix ControlService literal \n
with open("src/ControlService/Program.cs", "r") as f:
    cs = f.read()
cs = cs.replace("\\napp.Run();", "\napp.Run();")
with open("src/ControlService/Program.cs", "w") as f:
    f.write(cs)

# Fix AddNpgsql conflict
def fix_npgsql(path):
    with open(path, "r") as f:
        c = f.read()
    c = c.replace(".AddNpgsql(connStr)", ".AddNpgSql(connStr)")
    with open(path, "w") as f:
        f.write(c)

fix_npgsql("src/OrderService/Program.cs")
fix_npgsql("src/ProductService/Program.cs")

# Fix Decorator (Manual Decoration without Scrutor)
with open("src/ProductService/Program.cs", "r") as f:
    pc = f.read()

# Remove builder.Services.Decorate
pc = pc.replace("builder.Services.Decorate<IDistributedCache, ChaosCache>();", "")

# We will just let ChaosCache take IDistributedCache and wrap it manually via DI factory
pc = pc.replace("builder.Services.AddStackExchangeRedisCache(options => { options.Configuration = redisConn; });", 
"""builder.Services.AddStackExchangeRedisCache(options => { options.Configuration = redisConn; });
var descriptor = builder.Services.FirstOrDefault(d => d.ServiceType == typeof(IDistributedCache));
if (descriptor != null)
{
    builder.Services.Remove(descriptor);
    builder.Services.Add(new ServiceDescriptor(typeof(IDistributedCache), sp => 
    {
        var inner = (IDistributedCache)ActivatorUtilities.CreateInstance(sp, descriptor.ImplementationType!);
        return ActivatorUtilities.CreateInstance<DevOpsLabs.Chaos.Decorators.ChaosCache>(sp, inner);
    }, descriptor.Lifetime));
}""")

with open("src/ProductService/Program.cs", "w") as f:
    f.write(pc)
