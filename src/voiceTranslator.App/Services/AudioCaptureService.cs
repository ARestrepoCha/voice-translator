using NAudio.Wave;

namespace VoiceTranslator.App.Services;

public class AudioCaptureService : IDisposable
{
    private readonly TranslatorApiService _api;
    private WaveInEvent? _waveIn;
    private readonly List<byte> _buffer = [];
    private readonly WaveFormat _captureFormat = new(sampleRate: 16000, channels: 1);

    // 3 seconds of audio at 16kHz, 16-bit, mono
    private int ChunkSizeBytes =>
        _captureFormat.SampleRate * (_captureFormat.BitsPerSample / 8) * _captureFormat.Channels * 3;

    public AudioCaptureService(TranslatorApiService api)
    {
        _api = api;
    }

    public void Start()
    {
        _buffer.Clear();
        _waveIn = new WaveInEvent { WaveFormat = _captureFormat };
        _waveIn.DataAvailable += OnDataAvailable;
        _waveIn.StartRecording();
        Console.WriteLine("[Captura] Escuchando... habla en español.");
    }

    public void Stop()
    {
        if (_waveIn is null) return;

        // Esperar que el thread de grabación termine antes de Dispose
        // para evitar AccessViolationException en waveInAddBuffer
        var stopped = new TaskCompletionSource<bool>();
        _waveIn.RecordingStopped += (_, _) => stopped.TrySetResult(true);
        _waveIn.StopRecording();
        stopped.Task.Wait(TimeSpan.FromSeconds(2));

        _waveIn.Dispose();
        _waveIn = null;
        Console.WriteLine("[Captura] Detenida.");
    }

    private void OnDataAvailable(object? sender, WaveInEventArgs e)
    {
        _buffer.AddRange(e.Buffer[..e.BytesRecorded]);

        while (_buffer.Count >= ChunkSizeBytes)
        {
            var chunk = _buffer.Take(ChunkSizeBytes).ToArray();
            _buffer.RemoveRange(0, ChunkSizeBytes);
            _ = ProcessChunkAsync(chunk);
        }
    }

    private async Task ProcessChunkAsync(byte[] pcmBytes)
    {
        try
        {
            var wavBytes = PcmToWav(pcmBytes);
            var result = await _api.TranslateAudioAsync(wavBytes);

            Console.WriteLine($"[Original]  {result.OriginalText}");
            Console.WriteLine($"[Traducido] {result.TranslatedText}");
            Console.WriteLine($"[Latencia]  {result.TotalMs}ms\n");

            await PlayMp3Async(result.AudioBytes);
        }
        catch (HttpRequestException ex) when (ex.StatusCode == System.Net.HttpStatusCode.UnprocessableEntity)
        {
            // Silencio detectado — no loguear para no ensuciar la consola
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[Error] {ex.Message}");
        }
    }

    private byte[] PcmToWav(byte[] pcmData)
    {
        using var ms = new MemoryStream();
        using var writer = new WaveFileWriter(ms, _captureFormat);
        writer.Write(pcmData, 0, pcmData.Length);
        writer.Flush();
        return ms.ToArray();
    }

    private static async Task PlayMp3Async(byte[] mp3Bytes)
    {
        if (mp3Bytes.Length == 0) return;

        using var ms = new MemoryStream(mp3Bytes);
        using var reader = new Mp3FileReader(ms);
        using var player = new WaveOutEvent();
        var tcs = new TaskCompletionSource<bool>();
        player.PlaybackStopped += (_, _) => tcs.TrySetResult(true);
        player.Init(reader);
        player.Play();
        await tcs.Task;
    }

    public void Dispose() => Stop();
}
