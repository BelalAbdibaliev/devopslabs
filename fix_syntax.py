with open("src/OrderService/Program.cs", "r") as f:
    c = f.read()
c = c.replace(".AddNpgSql(connStr)", ".AddNpgSql(connStr);")
with open("src/OrderService/Program.cs", "w") as f:
    f.write(c)
