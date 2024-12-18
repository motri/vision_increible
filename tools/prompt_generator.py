import argparse
from gtts import gTTS

def main():
    parser = argparse.ArgumentParser(description="Generate a speech prompt using gTTS.")
    parser.add_argument('--mensaje', type=str, required=True, help='The message to convert to speech.')
    parser.add_argument('--output', type=str, required=True, help='The output file name for the speech prompt.')

    args = parser.parse_args()

    tts = gTTS(args.mensaje, lang='es')
    tts.save(args.output)

if __name__ == "__main__":
    main()