"""Image de présentation Google Play : 1024 × 500, PNG sans transparence (python tools/feature_graphic.py)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'fastlane/metadata/android/fr-FR/images/featureGraphic.png'
ICON = ROOT / 'web/icons/icon-512.png'


def font(size, bold=True):
    for path in ('/usr/share/fonts/opentype/inter/Inter-Bold.otf' if bold else '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                 'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


W, H = 1024, 500
img = Image.new('RGB', (W, H), (243, 245, 251))
d = ImageDraw.Draw(img)
# bandes pastel (une par matière)
pastels = [(253, 227, 214), (215, 241, 227), (218, 233, 251), (235, 224, 250), (250, 240, 198), (250, 219, 231)]
for i, c in enumerate(pastels):
    d.rounded_rectangle([600 + i * 70, -40 + (i % 2) * 30, 660 + i * 70, 540], 30, fill=c)
icon = Image.open(ICON).convert('RGBA').resize((210, 210), Image.LANCZOS)
img.paste(icon, (60, 70), icon)
ink = (30, 34, 64)
d.text((300, 95), 'Bialingo', font=font(92), fill=ink)
d.text((304, 205), 'Langues · Maths · Échecs · Musique', font=font(34), fill=(59, 74, 174))
d.text((64, 330), 'Gratuit, sans publicité, sans collecte de données.', font=font(30, False), fill=ink)
d.text((64, 378), 'En famille, hors ligne, logiciel libre.', font=font(30, False), fill=ink)
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, optimize=True)
print('Image de présentation :', OUT, img.size)
