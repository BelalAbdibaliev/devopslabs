using System.Text;
using System.Text.Json;
using DevOpsLabs.Chaos.Models;
using DevOpsLabs.Chaos.State;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

namespace NotificationService.Services;

public class RabbitMqConsumer : BackgroundService
{
    private readonly IConfiguration _config;
    private readonly IChaosStateProvider _state;
    private readonly ILogger<RabbitMqConsumer> _logger;
    private IConnection? _connection;
    private IChannel? _channel;

    public RabbitMqConsumer(IConfiguration config, IChaosStateProvider state, ILogger<RabbitMqConsumer> logger)
    {
        _config = config;
        _state = state;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        var connStr = _config.GetConnectionString("RabbitMQ") ?? "amqp://guest:guest@localhost:5672";
        var factory = new ConnectionFactory { Uri = new Uri(connStr) };
        
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                _connection = await factory.CreateConnectionAsync(stoppingToken);
                _channel = await _connection.CreateChannelAsync(cancellationToken: stoppingToken);
                await _channel.QueueDeclareAsync(queue: "notifications-queue", durable: true, exclusive: false, autoDelete: false, arguments: null);
                
                // Allow dynamic scaling logic preparation for KEDA
                await _channel.BasicQosAsync(prefetchSize: 0, prefetchCount: 50, global: false);
                
                var consumer = new AsyncEventingBasicConsumer(_channel);
                consumer.ReceivedAsync += async (model, ea) =>
                {
                    // Check Chaos State
                    var scenarios = await _state.GetActiveScenariosAsync();
                    var qScen = scenarios.FirstOrDefault(s => s.Type == ScenarioType.DependencyFailure && s.TargetService == "Consumer");
                    
                    if (qScen != null)
                    {
                        var qConf = qScen.Parameters?.Deserialize<QueueConsumerConfig>(new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                        if (qConf != null)
                        {
                            if (qConf.StopConsumers) 
                            {
                                await Task.Delay(5000, stoppingToken); // Block without acking
                                await _channel.BasicNackAsync(ea.DeliveryTag, false, true);
                                return;
                            }
                            if (qConf.ProcessingTimeMilliseconds > 0)
                            {
                                await Task.Delay(qConf.ProcessingTimeMilliseconds, stoppingToken);
                            }
                        }
                    }

                    var body = ea.Body.ToArray();
                    var message = Encoding.UTF8.GetString(body);
                    _logger.LogInformation("Processed message: {Msg}", message);
                    await _channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
                };

                await _channel.BasicConsumeAsync(queue: "notifications-queue", autoAck: false, consumer: consumer, cancellationToken: stoppingToken);
                
                // Wait indefinitely until cancellation
                await Task.Delay(Timeout.Infinite, stoppingToken);
            }
            catch (Exception ex) when (!stoppingToken.IsCancellationRequested)
            {
                _logger.LogError(ex, "RabbitMQ Consumer Error. Retrying in 5s...");
                await Task.Delay(5000, stoppingToken);
            }
        }
    }
}