# data.py
# Небольшая база примеров. Добавляй реальные модели и значения.
# score — условная производительность (чем больше, тем мощнее)
# price — в долларах (примерно)

CPUS = {
    "Intel Core i3-10100": {"score": 4200, "price": 120},
    "Intel Core i5-10400": {"score": 5000, "price": 180},
    "Intel Core i7-9700K": {"score": 6000, "price": 300},
    "AMD Ryzen 5 3600": {"score": 8000, "price": 200},
    "AMD Ryzen 7 5800X": {"score": 10000, "price": 350},
    "Intel Core i5-12400f": {"score": 8000, "price": 300},
    "AMD Ryzen 9 9950X3D": {"score": 25000, "price": 850},
    "AMD Ryzen 5 7500f": {"score": 12000, "price": 350}
}

GPUS = {
    "GTX 1050 Ti": {"score": 5000, "price": 120},
    "GTX 1660 Super": {"score": 7000, "price": 250},
    "RTX 2060": {"score": 9000, "price": 350},
    "RTX 3060": {"score": 14000, "price": 400},
    "RTX 3070": {"score": 15000, "price": 450},
    "RTX 3080": {"score": 17000, "price": 500},
    "RTX 4060": {"score": 18000, "price": 600},
    "RTX 4070": {"score": 24000, "price": 800},
    "RTX 4090": {"score": 30000, "price": 1000},
}

# Разрешение -> масштаб (чем выше разрешение, тем больше нагрузка)
RESOLUTION_SCALE = {
    "1280x720": 0.6,
    "1920x1080": 1.0,
    "2560x1440": 1.8,
    "3840x2160": 4.0,
}