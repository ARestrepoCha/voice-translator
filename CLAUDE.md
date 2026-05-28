# CLAUDE.md — Voice Translator Project

## 📌 Descripción del Proyecto

Aplicación local de **traducción de voz en tiempo real** para reuniones virtuales (Zoom, Google Meet, Microsoft Teams, etc.).
Permite que el usuario hable en español y los demás participantes escuchen inglés, y viceversa — de forma bidireccional y con latencia mínima.

El objetivo principal es eliminar la barrera del idioma en entrevistas de trabajo y reuniones laborales internacionales,
corriendo **100% local en Windows** sin depender de suscripciones pagas (excepto APIs con plan gratuito generoso).

---

## 🎯 Casos de Uso

1. **Entrevista de trabajo:** Usuario habla español → entrevistador escucha inglés traducido
2. **Reunión laboral:** Participantes hablan inglés → usuario escucha/lee traducción en español en tiempo real
3. **Bidireccional completo:** Ambas direcciones activas simultáneamente

---

## 🏗️ Arquitectura General

```
FLUJO PRINCIPAL:

[Micrófono físico]
      ↓
[NAudio - Captura de audio] (.NET)
      ↓
[Whisper BASE - Speech to Text] (Python)
      ↓
[DeepL API free / LibreTranslate - Traducción] (Python)
      ↓
[Edge-TTS - Text to Speech] (Python)
      ↓
[VB-Cable - Dispositivo de audio virtual] (Windows)
      ↓
[Zoom / Meet / Teams escucha la voz traducida]

FLUJO INVERSO (traducción de lo que dice el otro):

[Audio del otro participante en reunión]
      ↓
[NAudio - Captura del audio del sistema] (.NET)
      ↓
[Whisper BASE - Speech to Text] (Python)
      ↓
[DeepL API free - Traducción] (Python)
      ↓
[Subtítulos en pantalla o audio en auriculares del usuario]
```

---

## 🗂️ Estructura del Repositorio (Monorepo)

```
voice-translator/
├── src/
│   ├── VoiceTranslator.Service/        # Microservicio Python
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── stt/                        # Speech to Text (Whisper)
│   │   │   └── whisper_service.py
│   │   ├── translation/                # Traducción (DeepL / LibreTranslate)
│   │   │   └── translation_service.py
│   │   ├── tts/                        # Text to Speech (Edge-TTS)
│   │   │   └── tts_service.py
│   │   ├── audio/                      # Captura y salida de audio
│   │   │   └── audio_service.py
│   │   ├── requirements.txt
│   │   └── config.py                   # Variables de configuración
│   │
│   └── VoiceTranslator.App/            # Aplicación .NET C#
│       ├── VoiceTranslator.App.csproj
│       ├── Program.cs
│       ├── Services/
│       │   ├── AudioCaptureService.cs  # NAudio - captura micrófono
│       │   ├── TranslatorApiService.cs # Llama al microservicio Python
│       │   └── VirtualAudioService.cs  # Manejo VB-Cable
│       ├── UI/
│       │   └── MainForm.cs             # Interfaz gráfica simple (WinForms o WPF)
│       └── Models/
│           └── TranslationConfig.cs    # Configuración de idiomas
│
├── docs/
│   └── setup.md                        # Guía de instalación paso a paso
├── .gitignore
├── README.md
└── CLAUDE.md                           # Este archivo
```

---

## 🛠️ Stack Tecnológico

### Python — Microservicio de IA
| Componente | Herramienta | Versión | Notas |
|---|---|---|---|
| Framework API | FastAPI | latest | Comunicación con .NET vía HTTP local |
| Speech-to-Text | OpenAI Whisper | base model | Corre en CPU, buena precisión ES/EN |
| Traducción | DeepL API | free tier | 500k chars/mes gratis |
| Traducción alternativa | LibreTranslate | self-hosted | Fallback sin internet / sin límites |
| Text-to-Speech | Edge-TTS | latest | Voces naturales Microsoft, gratis |
| Audio | PyAudio / sounddevice | latest | Captura y reproducción |
| Servidor | Uvicorn | latest | Servidor ASGI para FastAPI |

### .NET C# — Aplicación Principal
| Componente | Herramienta | Versión | Notas |
|---|---|---|---|
| Framework | .NET 8 | 8.0 LTS | Versión estable actual |
| Audio capture | NAudio | latest NuGet | Captura micrófono y audio sistema |
| UI | WinForms | .NET 8 | Simple, rápido de implementar |
| HTTP Client | HttpClient | nativo | Llamadas al microservicio Python |
| Serialización | System.Text.Json | nativo | Parseo de respuestas API |

### Infraestructura Windows
| Componente | Herramienta | Notas |
|---|---|---|
| Audio virtual | VB-Cable | Instalación manual una sola vez |
| OS | Windows 11/10 | Entorno de desarrollo y producción |
| GPU | Intel Iris Xe Graphics | GPU integrada, sin CUDA — usar CPU mode |

---

## ⚙️ Hardware del Desarrollador

```
GPU:     Intel Iris Xe Graphics (integrada, sin soporte CUDA)
VRAM:    7.8 GB compartida con RAM
OS:      Windows
IDEs:    Visual Studio + VS Code + Claude Code
```

### Implicaciones del hardware:
- **Whisper:** Usar modelo `base` o `small` — NO usar `medium` ni `large` (muy lento en CPU)
- **Coqui XTTS (voice cloning):** Descartado por ahora — latencia 15-20 seg en CPU, inviable
- **Edge-TTS:** Opción principal para TTS — natural, rápida, sin carga en CPU
- **Latencia estimada total:** 2-4 segundos por frase (aceptable para reuniones)

---

## 🔑 APIs y Credenciales

### DeepL API (Traducción principal)
- Plan: **Free** — 500,000 caracteres/mes
- Registro: https://www.deepl.com/pro-api
- Variable de entorno: `DEEPL_API_KEY`
- Suficiente para: ~8-10 horas de conversación/mes

### Edge-TTS (Text to Speech)
- Sin API key requerida
- Gratis, sin límites documentados
- Voces recomendadas:
  - Inglés: `en-US-JennyNeural` o `en-US-GuyNeural`
  - Español: `es-CO-SalomeNeural` (Colombia) o `es-ES-AlvaroNeural`

### LibreTranslate (Fallback local)
- Self-hosted, sin API key en modo local
- Docker: `docker run -ti --rm -p 5000:5000 libretranslate/libretranslate`

---

## 🌐 Comunicación entre proyectos

El microservicio Python expone una API REST local:

```
Base URL: http://localhost:8000

Endpoints:
  POST /translate-audio     → Recibe audio, devuelve audio traducido
  POST /transcribe          → Recibe audio, devuelve texto
  POST /translate-text      → Recibe texto, devuelve texto traducido
  POST /synthesize          → Recibe texto, devuelve audio
  GET  /health              → Health check
  GET  /config              → Configuración actual de idiomas
  PUT  /config              → Actualizar idiomas source/target
```

La app .NET llama estos endpoints vía `HttpClient`.

---

## 🎙️ VB-Cable — Audio Virtual

VB-Cable crea un dispositivo de audio virtual en Windows:
- **CABLE Input** → micrófono virtual (aquí envía la app el audio traducido)
- **CABLE Output** → lo que entra al CABLE Input

Configuración en Zoom/Meet/Teams:
- Micrófono: seleccionar **"CABLE Output"**
- Los participantes escuchan el audio que la app envía al CABLE Input

Descarga: https://vb-audio.com/Cable/

---

## 📋 Roadmap de Versiones

### V1 — MVP (Objetivo: entrevista de trabajo esta semana)
- [ ] Microservicio Python funcionando (Whisper + DeepL + Edge-TTS)
- [ ] App .NET con UI mínima (botón Start/Stop)
- [ ] Captura de micrófono con NAudio
- [ ] Audio traducido saliendo por VB-Cable
- [ ] Dirección: Español → Inglés únicamente
- [ ] Configuración hardcodeada (sin UI de config aún)

### V2 — Bidireccional
- [ ] Traducción bidireccional simultánea
- [ ] Captura del audio del sistema (lo que dice el otro)
- [ ] Subtítulos en pantalla en tiempo real
- [ ] UI para configurar idiomas source/target
- [ ] Selector de dispositivo de audio

### V3 — Calidad y UX
- [ ] Integración ElevenLabs API para voice cloning (~$5/mes)
- [ ] UI mejorada con indicadores de audio y estado
- [ ] Configuración guardada (appsettings.json)
- [ ] Instalador simple (NSIS o WiX)
- [ ] Soporte multi-idioma (FR, PT, DE)

### V4 — Producto Comercial
- [ ] GPU acceleration cuando disponible (NVIDIA CUDA)
- [ ] Modelo Whisper fine-tuneado para jerga técnica
- [ ] Licenciamiento y sistema de activación
- [ ] Auto-update
- [ ] Documentación completa para usuarios finales

---

## 🚀 Setup Inicial (Guía rápida)

### Prerequisitos
```bash
# Python 3.11+
python --version

# .NET 8 SDK
dotnet --version

# pip packages del microservicio
cd src/VoiceTranslator.Service
pip install -r requirements.txt

# Instalar VB-Cable manualmente desde:
# https://vb-audio.com/Cable/
```

### Correr el proyecto
```bash
# Terminal 1 — Microservicio Python
cd src/VoiceTranslator.Service
uvicorn main:app --host localhost --port 8000 --reload

# Terminal 2 — App .NET
cd src/VoiceTranslator.App
dotnet run
```

---

## 📏 Reglas y Convenciones de Código

### Python
- Estilo: PEP 8
- Type hints en todas las funciones
- Async/await para operaciones de audio e I/O
- Variables de entorno en `.env` (nunca hardcodear API keys)
- Logging con módulo `logging` estándar

### C# .NET
- Estilo: Microsoft C# Coding Conventions
- Async/await para llamadas HTTP y operaciones de audio
- Dependency Injection nativo de .NET
- Configuración en `appsettings.json`
- Nunca hardcodear URLs — usar configuración

### General
- Commits en inglés, descriptivos
- Branches: `feature/nombre`, `fix/nombre`, `v1`, `v2`
- No commitear archivos `.env`, keys, ni binarios de audio
- `.gitignore` cubre: `__pycache__`, `*.pyc`, `.env`, `bin/`, `obj/`, `*.user`

---

## ⚠️ Consideraciones Importantes

1. **Latencia:** Con Intel Iris Xe en CPU, esperar 2-4 segundos entre hablar y escuchar la traducción. Es normal y aceptable.
2. **Whisper model:** Siempre usar `base` — el modelo `small` puede usarse si la precisión no es suficiente pero será más lento.
3. **VB-Cable:** Debe estar instalado antes de correr la app. Sin él, el audio traducido no llega a Zoom/Meet.
4. **DeepL free tier:** Monitorear uso mensual. Si se agota, cambiar a LibreTranslate como fallback.
5. **Privacy:** Todo el procesamiento de audio es local. Solo el texto (no el audio) sale a DeepL API para traducción.
6. **Voice cloning (Coqui XTTS):** No implementar en V1/V2 por limitaciones de hardware. Planificado para V3 con ElevenLabs o V4 con GPU dedicada.

---

## 🔗 Referencias

- Whisper: https://github.com/openai/whisper
- Whisper.net (.NET wrapper): https://github.com/sandrohanea/whisper.net
- FastAPI: https://fastapi.tiangolo.com
- Edge-TTS: https://github.com/rany2/edge-tts
- DeepL API docs: https://developers.deepl.com/docs
- NAudio: https://github.com/naudio/NAudio
- VB-Cable: https://vb-audio.com/Cable/
- LibreTranslate: https://github.com/LibreTranslate/LibreTranslate

---

*Última actualización: Mayo 2026*
*Desarrollador: Usuario — Stack principal: Python + C# .NET 8 — OS: Windows*