# app.py
from flask import Flask, render_template, request
from data import CPUS, GPUS, RESOLUTION_SCALE

app = Flask(__name__)

def estimate_fps(cpu_score, gpu_score, ram_gb, ssd, resolution_scale, quality="medium"):
    """
    Простая модель оценки FPS:
      base = gpu_score / resolution_scale
      cpu_factor = min(1.2, cpu_score / gpu_score)  # если CPU сильнее — ограничение небольшое
      ram_factor = 1.0 if ram_gb >= 16 else (0.85 if ram_gb >= 8 else 0.6)
      ssd_bonus = 1.02 if ssd else 1.0
      quality_modifier = {"low":1.2, "medium":1.0, "high":0.8, "ultra":0.6}
    В реальном проекте эту формулу заменяют на статистику по играм.
    """
    base = gpu_score / max(0.001, resolution_scale)
    cpu_factor = cpu_score / max(1, gpu_score)
    # ограничиваем cpu_factor в диапазоне [0.5, 1.2]
    if cpu_factor < 0.5:
        cpu_factor = 0.5
    if cpu_factor > 1.2:
        cpu_factor = 1.2

    if ram_gb >= 32:
        ram_factor = 1.1
    elif ram_gb >= 16:
        ram_factor = 1.0
    elif ram_gb >= 8:
        ram_factor = 0.85
    else:
        ram_factor = 0.5

    ssd_bonus = 1.02 if ssd else 1.0
    quality_map = {"low": 1.2, "medium": 1.0, "high": 0.8, "ultra": 0.6}
    qmod = quality_map.get(quality, 1.0)

    fps = (base * cpu_factor * ram_factor * ssd_bonus * qmod)/80
    # Ограничим FPS реалистично
    return round(max(1, fps), 1)

def analyze_bottleneck(cpu_score, gpu_score):
    """
    Простое правило:
      - ratio = cpu_score / gpu_score
      - если ratio < 0.7 -> CPU bottleneck
      - если ratio > 1.4 -> GPU bottleneck (GPU слабее относительно CPU)
      - иначе — сбалансировано
    """
    ratio = cpu_score / max(1, gpu_score)
    if ratio < 0.7:
        return "CPU (процессор) явно слабее — возможны фризы при нагрузке на CPU"
    elif ratio > 1.4:
        return "GPU (видеокарта) ограничивает производительность — стоит апгрейдить GPU"
    else:
        return "Система в целом сбалансирована"

def price_performance(cpu_score, cpu_price, gpu_score, gpu_price):
    # простая метрика: score / price
    cpu_pp = cpu_score / max(1, cpu_price)
    gpu_pp = gpu_score / max(1, gpu_price)
    return round(cpu_pp, 2), round(gpu_pp, 2)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", cpus=CPUS.keys(), gpus=GPUS.keys(), resolutions=RESOLUTION_SCALE.keys())

@app.route("/analyze", methods=["POST"])
def analyze():
    cpu_model = request.form.get("cpu")
    gpu_model = request.form.get("gpu")
    ram = int(request.form.get("ram", 8))
    storage = request.form.get("storage", "hdd")
    resolution = request.form.get("resolution", "1920x1080")
    quality = request.form.get("quality", "medium")

    cpu = CPUS.get(cpu_model)
    gpu = GPUS.get(gpu_model)
    if not cpu or not gpu:
        return "Модель CPU или GPU не найдена в базе. Добавьте модель в data.py", 400

    cpu_score = cpu["score"]
    gpu_score = gpu["score"]
    cpu_price = cpu["price"]
    gpu_price = gpu["price"]
    resolution_scale = RESOLUTION_SCALE.get(resolution, 1.0)
    ssd = storage == "ssd"

    fps_est = estimate_fps(cpu_score, gpu_score, ram, ssd, resolution_scale, quality)
    bottleneck = analyze_bottleneck(cpu_score, gpu_score)
    cpu_pp, gpu_pp = price_performance(cpu_score, cpu_price, gpu_score, gpu_price)

    # Рекомендации простые
    recs = []
    if "CPU" in bottleneck:
        recs.append("Рассмотрите апгрейд процессора или снижение настроек CPU- intensive игр. Проверьте фоновые процессы.")
    if "GPU" in bottleneck:
        recs.append("Рассмотрите апгрейд видеокарты или снижение графических настроек.")
    if ram < 16:
        recs.append("Добавьте оперативную память до 16 ГБ для комфортной игры в современные игры.")
    if not ssd:
        recs.append("Установка SSD ускорит загрузку уровней и приложений (не всегда повысит FPS).")
    if not recs:
        recs.append("Система сбалансирована — следите за температурой и драйверами.")

    result = {
        "cpu_model": cpu_model,
        "gpu_model": gpu_model,
        "ram": ram,
        "storage": storage,
        "resolution": resolution,
        "quality": quality,
        "fps_est": fps_est,
        "bottleneck": bottleneck,
        "cpu_pp": cpu_pp,
        "gpu_pp": gpu_pp,
        "recs": recs
    }

    return render_template("result.html", result=result)

if __name__ == "__main__":

    app.run(debug=True)

