import streamlit as st
from data import CPUS, GPUS, RESOLUTION_SCALE
import pandas as pd

st.set_page_config(page_title="GPU/CPU Analyzer", layout="wide")

# --- FUNCTIONS ---
def estimate_fps(cpu_score, gpu_score, ram_gb, ssd, resolution_scale, quality="medium"):
    base = gpu_score / max(0.001, resolution_scale)
    cpu_factor = cpu_score / max(1, gpu_score)
    cpu_factor = max(0.5, min(cpu_factor, 1.2))

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

    fps = (base * cpu_factor * ram_factor * ssd_bonus * qmod) / 80
    return round(max(1, fps), 1)


def analyze_bottleneck(cpu_score, gpu_score):
    ratio = cpu_score / max(1, gpu_score)
    if ratio < 0.7:
        return "CPU (процессор) явно слабее — возможны фризы при нагрузке на CPU"
    elif ratio > 1.4:
        return "GPU (видеокарта) ограничивает производительность — стоит апгрейдить GPU"
    else:
        return "Система в целом сбалансирована"


def price_performance(cpu_score, cpu_price, gpu_score, gpu_price):
    cpu_pp = cpu_score / max(1, cpu_price)
    gpu_pp = gpu_score / max(1, gpu_price)
    return round(cpu_pp, 2), round(gpu_pp, 2)

# --- UI ---
st.title("Анализ игровой производительности — CPU / GPU")
st.write("Выберите комплектующие и получите прогноз FPS и рекомендации.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Ввод данных")
    cpu_model = st.selectbox("Процессор", CPUS.keys())
    gpu_model = st.selectbox("Видеокарта", GPUS.keys())
    ram = st.selectbox("ОЗУ (GB)", [4, 8, 12, 16, 24, 32, 64], index=3)
    storage = st.radio("Накопитель", ["hdd", "ssd"], index=1)
    resolution = st.selectbox("Разрешение", RESOLUTION_SCALE.keys())
    quality = st.selectbox("Качество", ["low", "medium", "high", "ultra"], index=1)

    if st.button("Анализировать"):
        cpu = CPUS[cpu_model]
        gpu = GPUS[gpu_model]
        ssd = storage == "ssd"
        resolution_scale = RESOLUTION_SCALE[resolution]

        fps = estimate_fps(cpu["score"], gpu["score"], ram, ssd, resolution_scale, quality)
        bottleneck = analyze_bottleneck(cpu["score"], gpu["score"])
        cpu_pp, gpu_pp = price_performance(cpu["score"], cpu["price"], gpu["score"], gpu["price"])

        recs = []
        if "CPU" in bottleneck:
            recs.append("Апгрейд CPU или снижение CPU-нагрузки.")
        if "GPU" in bottleneck:
            recs.append("Апгрейд GPU или снижение графики.")
        if ram < 16:
            recs.append("Рекомендуется 16 ГБ ОЗУ для современных игр.")
        if not ssd:
            recs.append("SSD ускорит загрузку, но FPS почти не изменится.")
        if not recs:
            recs.append("Система сбалансирована.")

        st.session_state['result'] = {
            "fps": fps,
            "bottleneck": bottleneck,
            "cpu_pp": cpu_pp,
            "gpu_pp": gpu_pp,
            "recs": recs,
            "cpu_model": cpu_model,
            "gpu_model": gpu_model,
            "ram": ram,
            "storage": storage,
            "resolution": resolution,
            "quality": quality
        }

with col2:
    st.header("Результаты")
    if 'result' in st.session_state:
        r = st.session_state['result']
        st.metric("Оценочный FPS", f"{r['fps']} fps")
        st.write(f"**Узкое место:** {r['bottleneck']}")
        st.write(f"**CPU PP:** {r['cpu_pp']}")
        st.write(f"**GPU PP:** {r['gpu_pp']}")

        st.write("### Рекомендации")
        for rec in r['recs']:
            st.write("- ", rec)

        perf = min(100, int(r['fps'] * 1.5))
        st.progress(perf)

        table = pd.DataFrame([
            ["CPU", r['cpu_model']],
            ["GPU", r['gpu_model']],
            ["RAM", r['ram']],
            ["Storage", r['storage']],
            ["Resolution", r['resolution']],
            ["Quality", r['quality']],
        ], columns=["Параметр", "Значение"])

        st.table(table)

st.caption("Streamlit версия вашего Flask-приложения.")