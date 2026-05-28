namespace VoiceTranslator.App.Models;

public class TranslationConfig
{
    // Language configuration — expanded in TASK-04
    public string SourceLanguage { get; set; } = "ES";
    public string TargetLanguage { get; set; } = "EN";
    public string MicrophoneDeviceName { get; set; } = string.Empty;
    public string ServiceBaseUrl { get; set; } = "http://localhost:8000";
}
