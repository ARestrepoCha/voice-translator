using System.Net.Http.Json;

namespace VoiceTranslator.App.Services;

public class TranslatorApiService : IDisposable
{
    private readonly HttpClient _http;

    public TranslatorApiService(string baseUrl = "http://localhost:8000")
    {
        _http = new HttpClient { BaseAddress = new Uri(baseUrl) };
        _http.Timeout = TimeSpan.FromSeconds(5);
    }

    public async Task<string> HealthCheckAsync()
    {
        var response = await _http.GetFromJsonAsync<HealthResponse>("/health");
        return response is null
            ? "Sin respuesta del microservicio"
            : $"Microservicio OK - v{response.Version}";
    }

    public void Dispose() => _http.Dispose();

    private record HealthResponse(string Status, string Version);
}
