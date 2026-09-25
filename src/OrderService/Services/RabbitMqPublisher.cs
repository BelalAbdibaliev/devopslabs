using System.Text;
using RabbitMQ.Client;

namespace OrderService.Services;

public class RabbitMqPublisher : IAsyncDisposable
{
    private readonly IConnectionFactory _factory;
    private IConnection? _connection;
    private IChannel? _channel;

    public RabbitMqPublisher(IConfiguration config)
    {
        var connStr = config.GetConnectionString("RabbitMQ") ?? "amqp://guest:guest@localhost:5672";
        _factory = new ConnectionFactory { Uri = new Uri(connStr) };
    }

    public async Task InitializeAsync()
    {
        _connection = await _factory.CreateConnectionAsync();
        _channel = await _connection.CreateChannelAsync();
        await _channel.QueueDeclareAsync(queue: "notifications-queue", durable: true, exclusive: false, autoDelete: false, arguments: null);
    }

    public async Task PublishAsync(string message)
    {
        if (_channel == null) await InitializeAsync();
        var body = Encoding.UTF8.GetBytes(message);
        await _channel!.BasicPublishAsync(exchange: "", routingKey: "notifications-queue", body: body);
    }

    public async ValueTask DisposeAsync()
    {
        if (_channel != null) await _channel.CloseAsync();
        if (_connection != null) await _connection.CloseAsync();
    }
}