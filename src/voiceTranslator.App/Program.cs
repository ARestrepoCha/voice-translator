using VoiceTranslator.App.Services;

namespace VoiceTranslator.App;

static class Program
{
    [STAThread]
    static async Task Main()
    {
        ApplicationConfiguration.Initialize();

        using var api = new TranslatorApiService();
        try
        {
            var result = await api.HealthCheckAsync();
            Console.WriteLine(result);
        }
        catch (HttpRequestException)
        {
            Console.WriteLine("Microservicio no disponible - asegúrate de correr uvicorn primero");
        }

        Application.Run(new Form1());
    }
}
