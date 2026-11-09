"""
SNEAKER SQUAD - PRODUCT IMAGE NORMALIZATION SCRIPT (Pillow)
-----------------------------------------------------------
Resizes and pads sneaker/accessory product photos to an exact 800x800 square 
on a pure white (or studio light grey) background without stretching or cropping.

Usage:
  python scripts/process_product_images.py
  python scripts/process_product_images.py --input static/img --output static/img/uniform --size 800 --bg white
"""

import os
import sys
import argparse
from PIL import Image

def process_product_image(input_path, output_path, target_size=(800, 800), bg_color=(255, 255, 255), padding_ratio=0.08):
    """
    Takes an input image, preserves aspect ratio, resizes it with high quality Lanczos resampling,
    and pastes it centered onto a target_size background canvas.
    """
    try:
        with Image.open(input_path) as img:
            # Handle alpha channel / transparency
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGBA')
                alpha_canvas = Image.new('RGBA', img.size, bg_color + (255,))
                alpha_canvas.paste(img, mask=img.split()[3])
                img = alpha_canvas.convert('RGB')
            else:
                img = img.convert('RGB')

            src_w, src_h = img.size
            max_w = int(target_size[0] * (1.0 - (padding_ratio * 2)))
            max_h = int(target_size[1] * (1.0 - (padding_ratio * 2)))

            # Calculate proportional scale factor
            scale = min(max_w / src_w, max_h / src_h)
            new_w = max(1, int(src_w * scale))
            new_h = max(1, int(src_h * scale))

            # High-fidelity Lanczos resampling
            resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Create clean background canvas
            canvas = Image.new('RGB', target_size, bg_color)
            paste_x = (target_size[0] - new_w) // 2
            paste_y = (target_size[1] - new_h) // 2
            canvas.paste(resized_img, (paste_x, paste_y))

            # Ensure parent output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save optimized JPEG
            canvas.save(output_path, 'JPEG', quality=95, optimize=True)
            return True, f"OK: {os.path.basename(input_path)} -> 800x800"
            
    except Exception as e:
        return False, f"ERROR {os.path.basename(input_path)}: {str(e)}"

def process_folder(input_dir, output_dir, size=800, light_grey=False):
    bg = (248, 249, 250) if light_grey else (255, 255, 255)
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp')

    if not os.path.exists(input_dir):
        print(f"Directory not found: {input_dir}")
        return

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_exts)]
    print(f"\n🚀 Processing {len(files)} product images from '{input_dir}' to '{output_dir}'...")
    print(f"📐 Target Resolution: {size}x{size} px | Canvas Color: {'#F8F9FA (Light Grey)' if light_grey else '#FFFFFF (Pure White)'}")

    success_count = 0
    for filename in files:
        in_file = os.path.join(input_dir, filename)
        out_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.jpg')
        ok, msg = process_product_image(in_file, out_file, target_size=(size, size), bg_color=bg)
        if ok:
            success_count += 1
            print(f"  ✔ {msg}")
        else:
            print(f"  ✖ {msg}")

    print(f"\n🎉 Successfully normalized {success_count}/{len(files)} images to 800x800 square!\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Normalize product images to 800x800 uniform canvas.")
    parser.add_argument('--input', default='static/img', help="Input image directory")
    parser.add_argument('--output', default='static/img/processed', help="Output directory")
    parser.add_argument('--size', type=int, default=800, help="Target square dimensions in pixels")
    parser.add_argument('--grey', action='store_true', help="Use light grey #F8F9FA canvas instead of pure white")
    
    args = parser.parse_args()
    process_folder(args.input, args.output, size=args.size, light_grey=args.grey)
