from vosk import Model, KaldiRecognizer
import os
import wave
from pydub import AudioSegment
import json

# Указываем путь к модели vosk
model_path = "/Users/alexanderkondrashov/models/vosk-model-ru-0.42"
if not os.path.exists(model_path):
    print("Модель vosk не найдена. Пожалуйста, скачайте и распакуйте модель в указанный путь.")
    exit(1)

# Папки с mp3 файлами и для сохранения текста
mp3_folder = "calls"
text_folder = "text"

# Создаем папку для текстовых файлов, если она еще не существует
os.makedirs(text_folder, exist_ok=True)

# Загрузка модели
model = Model(model_path)
print("Модель загружена успешно.")

# Обработка каждого mp3 файла в папке
for mp3_file in os.listdir(mp3_folder):
    if mp3_file.endswith(".mp3"):
        # Определение участников диалога (здесь просто пример для двух участников)
        speakers = ["Speaker 1", "Speaker 2"]
        current_speaker = 0

        # Конвертация mp3 файла в wav
        audio_path = os.path.join(mp3_folder, mp3_file)
        sound = AudioSegment.from_mp3(audio_path)
        wav_path = audio_path.replace(".mp3", ".wav")
        sound.export(wav_path, format="wav")
        print(f"Файл {mp3_file} конвертирован в wav.")

        # Распознавание речи с использованием wave
        with wave.open(wav_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)  # Для получения слов вместо JSON

            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    results.append(json.loads(rec.Result()))

        # Сохранение результатов в текстовый файл
        text_path = os.path.join(text_folder, mp3_file.replace(".mp3", ".txt"))
        with open(text_path, "w") as text_file:
            for result in results:
                if 'result' in result:
                    for word_info in result['result']:
                        # Записываем фразу с указанием участника
                        text_file.write(f"{speakers[current_speaker]}: {word_info['word']} ")
                        current_speaker = (current_speaker + 1) % len(speakers)
            text_file.write("\n")
        print(f"Распознанная речь сохранена в {text_path}.")

        # Удаляем wav файл после обработки
        os.remove(wav_path)
        print(f"Временный файл {wav_path} удален.")

print("Обработка всех файлов завершена.")
