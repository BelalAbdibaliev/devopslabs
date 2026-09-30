import os

prog = "src/ControlService/Program.cs"
with open(prog, "r") as f:
    content = f.read()

# Replace the incident routing block
old_block = """    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    return Results.BadRequest();"""

new_block = """    if (type == "cascading-failure") return Results.Ok(await im.StartCascadingFailureAsync(duration, ct));
    if (type == "error-storm") return Results.Ok(await im.StartErrorStormAsync(duration, ct));
    if (type == "combined-outage") return Results.Ok(await im.StartCombinedOutageAsync(duration, ct));
    return Results.BadRequest();"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(prog, "w") as f:
        f.write(content)
