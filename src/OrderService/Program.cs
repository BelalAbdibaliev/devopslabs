var builder = WebApplication.CreateBuilder(args);
builder.Services.AddProblemDetails();
builder.Services.AddHealthChecks();

var app = builder.Build();
app.UseExceptionHandler();
app.MapHealthChecks("/health");

app.MapGet("/api/orders", () => Results.Ok(new[] { new { Id = 1, Status = "Created" } }));
app.MapPost("/api/orders", () => Results.Created("/api/orders/2", new { Id = 2, Status = "Created" }));

app.Run();
