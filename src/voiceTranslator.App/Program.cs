using VoiceTranslator.App.Services;

namespace VoiceTranslator.App;

static class Program
{
    [STAThread]
    static async Task Main()
    {
        ApplicationConfiguration.Initialize();

        using var api = new TranslatorApiService();

        // Verificar que el microservicio esté corriendo
        try
        {
            var health = await api.HealthCheckAsync();
            Console.WriteLine(health);
        }
        catch (HttpRequestException)
        {
            Console.WriteLine("ERROR: Microservicio no disponible.");
            Console.WriteLine("Corre primero: uvicorn main:app --host localhost --port 8000");
            Console.WriteLine("\nPresiona cualquier tecla para salir...");
            Console.ReadKey();
            return;
        }

        using var capture = new AudioCaptureService(api);

        Console.WriteLine("\nPresiona ENTER para iniciar/detener la captura.");
        Console.WriteLine("Presiona Ctrl+C para salir.\n");

        var capturing = false;

        Console.CancelKeyPress += (_, e) =>
        {
            e.Cancel = true;
            if (capturing) capture.Stop();
            Environment.Exit(0);
        };

        while (true)
        {
            var input = Console.ReadLine();
            if (input is null) break; // stdin cerrado

            if (!capturing)
            {
                capture.Start();
                capturing = true;
                Console.WriteLine(">>> Capturando — presiona ENTER para detener\n");
            }
            else
            {
                capture.Stop();
                capturing = false;
                Console.WriteLine(">>> Detenido — presiona ENTER para iniciar\n");
            }
        }
    }
}
