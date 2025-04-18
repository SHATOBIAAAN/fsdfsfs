import os
import subprocess
from pathlib import Path

# Пути к шрифтам
FONTS_DIR = Path('NESTRAH/static/fonts')
FONTS_TO_CONVERT = [
    'Montserrat/Montserrat-Medium.ttf',
    'Montserrat/Montserrat-Light.ttf',
    'Unbounded/Unbounded-Extralight.ttf',
    'Unbounded/Unbounded-Regular.ttf'
]

# Пути к инструментам
WOFF2_PATH = '/opt/homebrew/bin/woff2_compress'
WOFF_PATH = '/Users/shatobiaan/.nvm/versions/node/v20.17.0/bin/ttf2woff'

def convert_fonts():
    for font_path in FONTS_TO_CONVERT:
        full_path = FONTS_DIR / font_path
        if not full_path.exists():
            print(f"Шрифт не найден: {full_path}")
            continue
            
        # Конвертация в WOFF2
        try:
            subprocess.run([
                WOFF2_PATH, 
                str(full_path)
            ], check=True)
            print(f"Конвертирован в WOFF2: {full_path.with_suffix('.woff2')}")
        except Exception as e:
            print(f"Ошибка при конвертации в WOFF2: {e}")
        
        # Конвертация в WOFF
        woff_path = full_path.with_suffix('.woff')
        try:
            subprocess.run([
                WOFF_PATH, 
                str(full_path), 
                str(woff_path)
            ], check=True)
            print(f"Конвертирован в WOFF: {woff_path}")
        except Exception as e:
            print(f"Ошибка при конвертации в WOFF: {e}")

if __name__ == '__main__':
    convert_fonts() 