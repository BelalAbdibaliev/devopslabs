import glob
for p in glob.glob("src/*/Program.cs"):
    with open(p, "r") as f:
        prog = f.read()

    if "AddHttpLogging" not in prog:
        prog = prog.replace("var app = builder.Build();", "builder.Services.AddHttpLogging(o => { });\nvar app = builder.Build();")
        with open(p, "w") as f:
            f.write(prog)

