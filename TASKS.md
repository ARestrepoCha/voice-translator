# TASKS.md — Voice Translator Implementation Roadmap

## 📌 Cómo usar este archivo
- Cada task tiene un estado: `[ ]` Pendiente · `[~]` En progreso · `[x]` Completada
- Al iniciar una task en Claude Code: `"Lee el CLAUDE.md y el TASKS.md. Implementa la Task X"`
- Al completar: actualiza el estado, haz commit y pasa a la siguiente
- Cada task debe compilar/correr sin errores antes de avanzar

---

## 🏁 V1 — MVP (Español → Inglés en reuniones)

### TASK-01 — Scaffold del proyecto
**Estado:** `[x]` Completada  
**Rama:** `feature/task-01-scaffold`  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-01: crea el scaffold completo
del proyecto. Estructura de carpetas según CLAUDE.md, proyecto .NET 8
WinForms, requirements.txt de Python con todas las dependencias,
y .gitignore para Python + .NET. No implementes lógica aún,
solo la estructura base con archivos vacíos o comentarios placeholder.
```
**Entregables:**
- [ ] Estructura de carpetas completa según CLAUDE.md
- [ ] `src/VoiceTranslator.App/VoiceTranslator.App.csproj` (.NET 8 WinForms)
- [ ] `src/VoiceTranslator.Service/requirements.txt` con dependencias
- [ ] `src/VoiceTranslator.Service/config.py` con variables de entorno
- [ ] `src/VoiceTranslator.Service/.env.example` con keys necesarias
- [ ] `.gitignore` cubre Python + .NET + `.env`
- [ ] `docs/setup.md` con instrucciones de instalación

**Validación:**
```bash
cd src/VoiceTranslator.App && dotnet build        # Sin errores
cd ../VoiceTranslator.Service && pip install -r requirements.txt  # Sin errores
```
**Commit:** `feat: task-01 project scaffold`

---

### TASK-02 — Microservicio Python: Health Check
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-02-health-check`  
**Depende de:** TASK-01  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-02: crea el microservicio
FastAPI con un endpoint GET /health que retorne { "status": "ok",
"version": "1.0.0" }. En el proyecto .NET implementa una llamada
HttpClient a ese endpoint y muestra la respuesta en consola al iniciar.
```
**Entregables:**
- [ ] `src/VoiceTranslator.Service/main.py` con FastAPI configurado
- [ ] Endpoint `GET /health` funcionando en `localhost:8000`
- [ ] `src/VoiceTranslator.App/Services/TranslatorApiService.cs` con método `HealthCheckAsync()`
- [ ] `Program.cs` llama `HealthCheckAsync()` al iniciar y muestra resultado

**Validación:**
```bash
# Terminal 1
cd src/VoiceTranslator.Service && uvicorn main:app --reload
# Terminal 2
cd src/VoiceTranslator.App && dotnet run
# Resultado esperado en consola: "Microservicio OK - v1.0.0"
```
**Commit:** `feat: task-02 health check endpoint and .NET client`

---

### TASK-03 — STT: Whisper Speech-to-Text
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-03-whisper-stt`  
**Depende de:** TASK-02  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-03: integra Whisper modelo BASE
en el microservicio Python. Crea whisper_service.py con una función
que reciba un archivo de audio y retorne el texto transcrito.
Expón el endpoint POST /transcribe que reciba un archivo .wav
y retorne { "text": "...", "language": "es", "duration_ms": 000 }.
Incluye un archivo de audio de prueba en tests/.
```
**Entregables:**
- [ ] `src/VoiceTranslator.Service/stt/whisper_service.py`
- [ ] Modelo Whisper `base` cargado al iniciar el servicio (no en cada request)
- [ ] Endpoint `POST /transcribe` recibe audio, retorna texto
- [ ] Manejo de errores si el audio no es válido
- [ ] `tests/test_audio_es.wav` archivo de prueba en español

**Validación:**
```bash
# Enviar audio de prueba
curl -X POST http://localhost:8000/transcribe \
  -F "audio=@tests/test_audio_es.wav"
# Resultado esperado: { "text": "texto en español...", "language": "es" }
```
**Commit:** `feat: task-03 whisper STT integration`

---

### TASK-04 — Traducción: DeepL API
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-04-deepl-translation`  
**Depende de:** TASK-02  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-04: integra DeepL API free
en el microservicio Python. Crea translation_service.py con función
que reciba texto en español y retorne texto en inglés. Expón el
endpoint POST /translate-text. La API key se lee desde variable
de entorno DEEPL_API_KEY. Si no está configurada, retornar error
descriptivo. Agregar LibreTranslate como fallback.
```
**Entregables:**
- [ ] `src/VoiceTranslator.Service/translation/translation_service.py`
- [ ] Endpoint `POST /translate-text` con body `{ "text": "...", "source": "ES", "target": "EN" }`
- [ ] Lee `DEEPL_API_KEY` desde `.env`
- [ ] Fallback a LibreTranslate si DeepL falla
- [ ] Manejo de errores con mensajes claros
- [ ] `PUT /config` para cambiar idiomas source/target en caliente

**Validación:**
```bash
curl -X POST http://localhost:8000/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola buenos días", "source": "ES", "target": "EN"}'
# Resultado esperado: { "translated": "Hello, good morning", "provider": "deepl" }
```
**Commit:** `feat: task-04 DeepL translation with LibreTranslate fallback`

---

### TASK-05 — TTS: Edge-TTS Text-to-Speech
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-05-edge-tts`  
**Depende de:** TASK-02  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-05: integra Edge-TTS en el
microservicio Python. Crea tts_service.py que reciba texto en inglés
y genere audio. Expón el endpoint POST /synthesize que retorne
el archivo de audio generado. Voz por defecto: en-US-JennyNeural.
La voz debe ser configurable.
```
**Entregables:**
- [ ] `src/VoiceTranslator.Service/tts/tts_service.py`
- [ ] Endpoint `POST /synthesize` recibe `{ "text": "...", "voice": "en-US-JennyNeural" }`
- [ ] Retorna archivo de audio `.mp3` o `.wav`
- [ ] Voces configurables: `en-US-JennyNeural`, `en-US-GuyNeural`, `es-CO-SalomeNeural`
- [ ] `GET /voices` lista las voces disponibles

**Validación:**
```bash
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, good morning, how are you?"}' \
  --output test_output.mp3
# Abrir test_output.mp3 y verificar que suena natural
```
**Commit:** `feat: task-05 Edge-TTS synthesis`

---

### TASK-06 — Pipeline completo Python (STT → Traducción → TTS)
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-06-full-pipeline`  
**Depende de:** TASK-03, TASK-04, TASK-05  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-06: une los servicios de
Whisper, DeepL y Edge-TTS en un pipeline completo. Crea el endpoint
POST /translate-audio que reciba audio en español y retorne audio
en inglés. Medir y retornar en headers el tiempo de cada etapa
(STT, traducción, TTS) para monitorear latencia.
```
**Entregables:**
- [ ] Endpoint `POST /translate-audio` end-to-end
- [ ] Retorna audio traducido en inglés
- [ ] Headers con métricas: `X-STT-Ms`, `X-Translation-Ms`, `X-TTS-Ms`, `X-Total-Ms`
- [ ] Log en consola de cada etapa con tiempos
- [ ] Prueba manual: enviar audio .wav en español, recibir audio en inglés

**Validación:**
```bash
curl -X POST http://localhost:8000/translate-audio \
  -F "audio=@tests/test_audio_es.wav" \
  --output translated_output.mp3 -v
# Verificar headers de latencia y reproducir el audio resultado
```
**Commit:** `feat: task-06 complete STT-Translation-TTS pipeline`

---

### TASK-07 — NAudio: Captura de micrófono en .NET
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-07-naudio-capture`  
**Depende de:** TASK-06  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-07: en el proyecto .NET 8
crea AudioCaptureService.cs usando NAudio para capturar el micrófono
en fragmentos de 3 segundos. Cada fragmento se envía al endpoint
POST /translate-audio del microservicio Python. La respuesta de audio
se reproduce por los auriculares/parlantes del usuario (no por
VB-Cable aún). Mostrar en consola el texto transcrito de cada fragmento.
```
**Entregables:**
- [ ] `src/VoiceTranslator.App/Services/AudioCaptureService.cs`
- [ ] Captura micrófono en fragmentos de 3 segundos
- [ ] Envía fragmento a `/translate-audio` vía HttpClient
- [ ] Reproduce la respuesta de audio en el dispositivo de salida
- [ ] Muestra en consola: texto original + texto traducido + latencia total
- [ ] Start/Stop de captura controlado desde `Program.cs`

**Validación:**
```
1. Correr microservicio Python
2. Correr app .NET
3. Hablar en español al micrófono
4. Escuchar la traducción en inglés por los parlantes
5. Ver en consola el texto transcrito y traducido
```
**Commit:** `feat: task-07 NAudio microphone capture and audio playback`

---

### TASK-08 — VB-Cable: Salida al micrófono virtual
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-08-vbcable-output`  
**Depende de:** TASK-07  
**Prerequisito manual:** VB-Cable instalado en Windows  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-08: modifica VirtualAudioService.cs
para que el audio traducido salga por el dispositivo VB-Cable (CABLE Input)
en lugar de los parlantes. Agregar detección automática del dispositivo
VB-Cable. Si no está instalado, mostrar mensaje de error con instrucciones
de descarga. Agregar selector en consola para elegir dispositivo de salida.
```
**Entregables:**
- [ ] `src/VoiceTranslator.App/Services/VirtualAudioService.cs`
- [ ] Detecta automáticamente dispositivo "CABLE Input (VB-Audio)"
- [ ] Audio traducido sale por VB-Cable
- [ ] Error claro si VB-Cable no está instalado
- [ ] Lista dispositivos de audio disponibles al iniciar

**Validación:**
```
1. Abrir Zoom/Meet en modo prueba
2. Seleccionar micrófono: "CABLE Output (VB-Audio Virtual Cable)"
3. Correr la app
4. Hablar español → verificar que Zoom recibe audio en inglés
5. Grabar la sesión para verificar la calidad
```
**Commit:** `feat: task-08 VB-Cable virtual audio output`

---

### TASK-09 — UI WinForms básica
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-09-winforms-ui`  
**Depende de:** TASK-08  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-09: crea la UI WinForms en
MainForm.cs. Debe tener: botón Start/Stop, indicador de estado
(Idle/Listening/Translating/Playing), selector de micrófono,
selector de idioma origen y destino, y un log en pantalla que
muestre las últimas 10 traducciones con su texto original y traducido.
Diseño simple y funcional, no necesita ser elaborado.
```
**Entregables:**
- [ ] `src/VoiceTranslator.App/UI/MainForm.cs`
- [ ] Botón Start / Stop
- [ ] Indicador de estado con color (verde=ok, amarillo=procesando, rojo=error)
- [ ] Dropdown selector de micrófono de entrada
- [ ] Dropdown selector ES→EN o EN→ES
- [ ] Panel de log con últimas 10 traducciones
- [ ] Muestra latencia promedio en tiempo real

**Validación:**
```
1. Correr la app — ver UI limpia y funcional
2. Seleccionar micrófono
3. Click Start → indicador cambia a verde
4. Hablar → ver log actualizarse con traducción
5. Click Stop → todo se detiene limpiamente
```
**Commit:** `feat: task-09 WinForms basic UI`

---

### TASK-10 — Prueba end-to-end en reunión real
**Estado:** `[ ]` Pendiente  
**Rama:** `feature/task-10-e2e-testing`  
**Depende de:** TASK-09  
**Prompt para Claude Code:**
```
Lee el CLAUDE.md. Implementa la TASK-10: agrega manejo de errores
robusto en toda la app, reconexión automática si el microservicio
Python cae, y un archivo de configuración appsettings.json para
guardar preferencias del usuario (micrófono seleccionado, idiomas,
URL del microservicio). También crear un script start.bat que
levante ambos proyectos con un solo click.
```
**Entregables:**
- [ ] `src/VoiceTranslator.App/appsettings.json` con configuración persistente
- [ ] Reconexión automática al microservicio Python (retry cada 5 seg)
- [ ] `start.bat` levanta Python y .NET en orden correcto
- [ ] Manejo de errores en todos los servicios con mensajes claros en UI
- [ ] `docs/setup.md` actualizado con instrucciones completas

**Validación:**
```
1. Ejecutar start.bat
2. Unirse a una reunión de prueba en Zoom/Meet
3. Seleccionar "CABLE Output" como micrófono en Zoom
4. Hablar 5 minutos en español
5. Verificar que el otro participante escucha inglés correcto
6. Medir latencia promedio real
```
**Commit:** `feat: task-10 e2e testing, error handling and start script`

---

## 🔮 V2 — Bidireccional (Post MVP)

### TASK-11 — Captura de audio del sistema (lo que dice el otro)
**Estado:** `[ ]` Pendiente · **Depende de:** TASK-10

### TASK-12 — Subtítulos en pantalla en tiempo real
**Estado:** `[ ]` Pendiente · **Depende de:** TASK-11

### TASK-13 — UI mejorada con configuración completa
**Estado:** `[ ]` Pendiente · **Depende de:** TASK-12

---

## 💎 V3 — Voice Cloning (Futuro)

### TASK-14 — Integración ElevenLabs API (voz clonada)
**Estado:** `[ ]` Pendiente · **Depende de:** TASK-10  
**Nota:** Requiere plan ElevenLabs ~$5/mes. Reemplaza Edge-TTS con la voz del usuario.

### TASK-15 — Grabación y entrenamiento de voz del usuario
**Estado:** `[ ]` Pendiente · **Depende de:** TASK-14

---

## 📊 Progreso General

```
V1 MVP:        1/10 tasks  [x] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]
V2 Bidireccional: 0/3 tasks
V3 Voice Clone:   0/2 tasks
```

---

## 📝 Notas de implementación

| Fecha | Task | Nota |
|---|---|---|
| - | - | Agregar notas aquí durante el desarrollo |

---

*Archivo actualizado manualmente al completar cada task*  
*Stack: Python 3.11+ · .NET 8 · FastAPI · Whisper BASE · DeepL · Edge-TTS · NAudio · VB-Cable*