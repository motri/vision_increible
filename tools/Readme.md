# Generador de Prompts de Voz

Este script utiliza la biblioteca `gTTS` (Google Text-to-Speech) para convertir un mensaje de texto en un archivo de audio en formato MP3.

## Requisitos

Antes de ejecutar el script, asegúrate de tener instaladas las siguientes dependencias:

- `argparse`
- `gtts`

Puedes instalarlas utilizando `pip`:

```sh
pip install argparse gtts
```

## Uso

Para ejecutar el script, utiliza el siguiente comando:

```sh
python prompt_generator.py --mensaje "Tu mensaje aquí" --output "nombre_del_archivo.mp3"
```

### Argumentos

- `--mensaje`: El mensaje de texto que deseas convertir a voz.
- `--output`: El nombre del archivo de salida donde se guardará el audio generado.

### Ejemplo

```sh
python prompt_generator.py --mensaje "Corríja la postura, mantenga la espalda recta" --output "mantenga_espalda.mp3"
```

Este comando generará un archivo de audio llamado `mantenga_espalda.mp3` con el mensaje "Corríja la postura, mantenga la espalda recta".
