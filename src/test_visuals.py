"""
Test için sinematik arka plan görselleri üreten yardımcı araç.
Google Flow'dan görseller gelene kadar testlerin estetik görünmesini sağlar.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_cinematic_card(
    output_path: str,
    width: int,
    height: int,
    title: str,
    subtitle: str,
    theme_color: tuple = (30, 80, 180)
):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img = Image.new("RGB", (width, height), color=(10, 12, 20))
    draw = ImageDraw.Draw(img)

    # 1. Radyal / dairesel degrade parıltı (Merkez ışığı)
    cx, cy = width // 2, height // 2
    max_radius = min(width, height) // 2
    for r in range(max_radius, 0, -8):
        alpha = int((1.0 - (r / max_radius)) * 55)
        color = (
            min(255, theme_color[0] + alpha),
            min(255, theme_color[1] + alpha),
            min(255, theme_color[2] + alpha)
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # 2. İnce ızgara (Grid) / Teknoloji çizgileri
    grid_spacing = 80
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=(20, 30, 50), width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=(20, 30, 50), width=1)

    # 3. Şık Köşe Çerçevesi
    margin = 40
    frame_w = 2
    frame_color = (60, 120, 220)
    draw.rectangle([margin, margin, width - margin, height - margin], outline=frame_color, width=frame_w)

    # Köşe süsleri
    cs = 30
    for (kx, ky) in [(margin, margin), (width - margin, margin), (margin, height - margin), (width - margin, height - margin)]:
        draw.rectangle([kx - 5, ky - 5, kx + 5, ky + 5], fill=(120, 180, 255))

    # 4. Metinler
    try:
        font_large = ImageFont.truetype("arial.ttf", size=int(width * 0.05))
        font_sub = ImageFont.truetype("arial.ttf", size=int(width * 0.028))
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((cx, cy - 60), title, fill=(240, 245, 255), font=font_large, anchor="mm")
    draw.text((cx, cy + 50), subtitle, fill=(160, 190, 240), font=font_sub, anchor="mm")

    img.save(output_path, quality=95)
    return output_path


if __name__ == "__main__":
    create_cinematic_card("test_visual.png", 1080, 1920, "1950: ALAN TURING", "Makineler Düşünebilir mi?")
    print("Test görseli oluşturuldu.")
