using System.Net.Http.Headers;
using System.Net.Http.Json;

namespace VoiceTranslator.App.Services;

public class TranslatorApiService : IDisposable
{
    private readonly HttpClient _http;

    public TranslatorApiService(string baseUrl = "http://localhost:8000")
    {
        _http = new HttpClient { BaseAddress = new Uri(baseUrl) };
        _http.Timeout = TimeSpan.FromSeconds(30);
    }

    public async Task<string> HealthCheckAsync()
    {
        var response = await _http.GetFromJsonAsync<HealthResponse>("/health");
        return response is null
            ? "Sin respuesta del microservicio"
            : $"Microservicio OK - v{response.Version}";
    }

    public async Task<TranslateAudioResult> TranslateAudioAsync(byte[] wavBytes)
    {
        using var content = new MultipartFormDataContent();
        using var audioContent = new ByteArrayContent(wavBytes);
        audioContent.Headers.ContentType = new MediaTypeHeaderValue("audio/wav");
        content.Add(audioContent, "audio", "audio.wav");

        var response = await _http.PostAsync("/translate-audio", content);
        response.EnsureSuccessStatusCode();

        var audioBytes = await response.Content.ReadAsByteArrayAsync();

        var originalText   = Uri.UnescapeDataString(GetHeader(response, "X-Original-Text"));
        var translatedText = Uri.UnescapeDataString(GetHeader(response, "X-Translated-Text"));
        var totalMs        = int.TryParse(GetHeader(response, "X-Total-Ms"), out var ms) ? ms : 0;

        return new TranslateAudioResult(audioBytes, originalText, translatedText, totalMs);
    }

    private static string GetHeader(HttpResponseMessage response, string name) =>
        response.Headers.TryGetValues(name, out var values) ? values.First() : string.Empty;

    public void Dispose() => _http.Dispose();

    private record HealthResponse(string Status, string Version);
}

public record TranslateAudioResult(
    byte[] AudioBytes,
    string OriginalText,
    string TranslatedText,
    int TotalMs
);
