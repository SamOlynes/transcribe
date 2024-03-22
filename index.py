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
        # Конвертация mp3 файла в wav
        audio_path = os.path.join(mp3_folder, mp3_file)
        wav_path = os.path.join(mp3_folder, mp3_file.replace(".mp3", ".wav"))
        sound = AudioSegment.from_mp3(audio_path)
        sound.export(wav_path, format="wav")
        print(f"Файл {mp3_file} конвертирован в wav.")

        # Распознавание речи с использованием wave
        with wave.open(wav_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)  # Для получения слов вместо JSON

            results = []
            current_speaker = None
            start_time = 0.0
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'result' in result:
                        result_start_time = result['result'][0]['start']
                        # Определяем начало нового фрагмента речи
                        if current_speaker is None:
                            current_speaker = result['result'][0]['speaker']
                            start_time = result_start_time
                        elif result_start_time - start_time > 2.0:  # Порог для смены спикера (2 секунды)
                            end_time = result_start_time
                            results.append((current_speaker, start_time, end_time))
                            current_speaker = result['result'][0]['speaker']
                            start_time = result_start_time
            # Добавляем последний фрагмент речи
            if current_speaker is not None:
                end_time = wf.getnframes() / wf.getframerate()
                results.append((current_speaker, start_time, end_time))

        # Сохранение результатов в текстовый файл
        text_path = os.path.join(text_folder, mp3_file.replace(".mp3", ".txt"))
        with open(text_path, "w") as text_file:
            for i, (speaker, start, end) in enumerate(results):
                text_file.write(f"Speaker {i+1}: ")
                text_file.write("[" + str(start) + "-" + str(end) + "]: ")
                for result in results:
                    if result[0] == speaker:
                        text_file.write(result[1] + " ")
                text_file.write("\n")
        print(f"Распознанная речь сохранена в {text_path}.")

        # Удаляем wav файл после обработки
        os.remove(wav_path)
        print(f"Временный файл {wav_path} удален.")

print("Обработка всех файлов завершена.")
