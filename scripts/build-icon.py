"""Render the approved purple 引 seal as the Windows application icon."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
target = root / "assets" / "mortal-quota-card.ico"
size = 256
image = Image.new("RGBA", (size, size), (7, 19, 15, 255))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((20, 20, 236, 236), radius=54, fill=(23, 20, 50, 255), outline=(159, 133, 220, 230), width=10)
draw.rounded_rectangle((48, 48, 208, 208), radius=34, outline=(113, 226, 220, 90), width=5)
font_paths = [Path(r"C:\Windows\Fonts\simkai.ttf"), Path(r"C:\Windows\Fonts\msyh.ttc")]
font_path = next((path for path in font_paths if path.exists()), None)
font = ImageFont.truetype(str(font_path), 132) if font_path else ImageFont.load_default()
box = draw.textbbox((0, 0), "引", font=font)
draw.text(((size - (box[2] - box[0])) / 2 - box[0], (size - (box[3] - box[1])) / 2 - box[1] - 3), "引", font=font, fill=(235, 222, 255, 245))
target.parent.mkdir(parents=True, exist_ok=True)
image.save(target, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(target)
