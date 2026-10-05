#!/usr/bin/env python3
"""
Automation script to organize backgrounds and stickers into structured folders
and generate standardized index JSONs matching the index.json schema.
"""

import os
import sys
import shutil
import json
import re
from PIL import Image

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def organize_backgrounds():
    print("=== Organizing Backgrounds ===")
    src_dir = "background_images"
    dest_dir = "backgrounds"
    
    if not os.path.exists(src_dir):
        print(f"Directory {src_dir} not found!")
        return

    os.makedirs(dest_dir, exist_ok=True)
    
    bg_cat_map = {
        'autumn': 'Autumn',
        'circle': 'Circle',
        'clr': 'Color',
        'deg': 'Gradient',
        'fantasy': 'Fantasy',
        'graphic': 'Graphic',
        'house': 'House',
        'nature': 'Nature',
        'neon': 'Neon',
        'pattern': 'Pattern',
        'road': 'Road',
        'school': 'School',
        'sky': 'Sky',
        'smooke': 'Smoke',
        'summer': 'Summer',
        'travel': 'Travel',
        'vehicle': 'Vehicle',
        'wall': 'Wall',
        'wals': 'WallArt',
        'wedding': 'Wedding',
        'winter': 'Winter'
    }

    # Load existing background.json metadata if available
    metadata_map = {}
    if os.path.exists("background.json"):
        try:
            with open("background.json") as f:
                raw_bg = json.load(f)
            if "data" in raw_bg and len(raw_bg["data"]) > 0 and "details" in raw_bg["data"][0]:
                for d in raw_bg["data"][0]["details"]:
                    bname = os.path.basename(d.get("image", ""))
                    metadata_map[bname] = d
        except Exception as e:
            print(f"Notice: Could not load old background.json metadata: {e}")

    # Gather all normal images and their thumbnail pairs
    all_files = os.listdir(src_dir)
    normal_files = [f for f in all_files if not f.endswith('i.png') and f != 'ops.png']
    
    cat_to_files = {cat: [] for cat in bg_cat_map.values()}
    for f in normal_files:
        prefix = f.split('-')[0]
        cat = bg_cat_map.get(prefix, 'Other')
        if cat not in cat_to_files:
            cat_to_files[cat] = []
        cat_to_files[cat].append(f)

    sorted_cat_names = sorted(cat_to_files.keys(), key=lambda s: s.lower())

    categories_list = []
    cat_id = 1
    total_items = 0

    for cat_name in sorted_cat_names:
        files = sorted(cat_to_files[cat_name], key=natural_sort_key)
        cat_folder = os.path.join(dest_dir, cat_name)
        os.makedirs(cat_folder, exist_ok=True)

        product_details = []
        for idx, orig_filename in enumerate(files, 1):
            stem, ext = os.path.splitext(orig_filename)
            new_img_name = f"{idx}{ext}"
            new_thumb_name = f"{idx}_thumb{ext}"
            
            src_img_path = os.path.join(src_dir, orig_filename)
            dest_img_path = os.path.join(cat_folder, new_img_name)
            
            orig_thumb_name = f"{stem}i{ext}"
            src_thumb_path = os.path.join(src_dir, orig_thumb_name)
            dest_thumb_path = os.path.join(cat_folder, new_thumb_name)

            # Move image
            if os.path.exists(src_img_path):
                shutil.move(src_img_path, dest_img_path)
            
            # Move thumbnail
            if os.path.exists(src_thumb_path):
                shutil.move(src_thumb_path, dest_thumb_path)
            elif not os.path.exists(dest_thumb_path) and os.path.exists(dest_img_path):
                # Auto-generate if thumb was missing
                try:
                    im = Image.open(dest_img_path).convert('RGBA')
                    thumb = im.resize((100, 100), Image.Resampling.LANCZOS)
                    thumb.save(dest_thumb_path)
                except Exception as e:
                    print(f"Thumb generation failed for {dest_img_path}: {e}")

            # Lookup original metadata
            meta = metadata_map.get(stem, {})
            is_pro = meta.get("isPro", False)
            title = meta.get("title") or f"{cat_name} {idx}"

            product_details.append({
                "id": f"bg_{cat_name.lower()}_{idx:03d}",
                "title": title,
                "image": dest_img_path,
                "thumb": dest_thumb_path,
                "isPro": is_pro
            })

        total_items += len(product_details)
        categories_list.append({
            "cat_id": cat_id,
            "cat_name": cat_name,
            "total_count": len(product_details),
            "product_details": product_details
        })
        cat_id += 1

    # Clean up empty background_images or ops.png if remaining
    ops_path = os.path.join(src_dir, "ops.png")
    if os.path.exists(ops_path):
        os.remove(ops_path)
    
    if os.path.exists(src_dir) and not os.listdir(src_dir):
        os.rmdir(src_dir)

    output_data = {
        "total_categories": len(categories_list),
        "total_items": total_items,
        "categories": categories_list
    }

    with open("background.json", "w") as fp:
        json.dump(output_data, fp, indent=2)

    print(f"Backgrounds complete: {len(categories_list)} categories, {total_items} items written to background.json.")


def organize_stickers():
    print("=== Organizing Stickers ===")
    src_dir = "iStickers_images"
    dest_dir = "stickers"

    if not os.path.exists(src_dir):
        print(f"Directory {src_dir} not found!")
        return

    os.makedirs(dest_dir, exist_ok=True)

    # 108 categories definitions mapping group index / prefix to clean TitleCase
    sticker_groups_def = [
        ('Emoji', 'emoji'),
        ('Aesthetic', 'aesthetic'),
        ('BabyWish', 'babywish'),
        ('BirthdayParty', 'birthdayparty'),
        ('GraduationCap', 'grad'),
        ('Arrow', 'arrow'),
        ('Balloon', 'ballon'),
        ('Dalis', 'dalis'),
        ('Party', 'party'),
        ('Butterfly', 'butterfly'),
        ('Cactus', 'cactus'),
        ('Cheers', 'cheers'),
        ('Chicken', 'chicken'),
        ('Child', 'child'),
        ('Like', 'like'),
        ('Cloud', 'cloud'),
        ('Cute', 'cute'),
        ('Besties', 'besties'),
        ('Dairy', 'dairy'),
        ('DoubleExposure', 'double'),
        ('Eid', 'eid'),
        ('Emoticon', 'emj'),
        ('Emoji3D', 'emoj'),
        ('Heart', 'heart'),
        ('Era', 'era'),
        ('Funny', 'funny'),
        ('Fun', 'fun'),
        ('Glitch', 'glitch'),
        ('Neon', 'neon'),
        ('NeoArt', 'neo'),
        ('Pixel', 'pixel'),
        ('Word', 'word'),
        ('Numbers', '1'),
        ('Graduation', 'graduation'),
        ('Graduate', 'gradu'),
        ('Healthy', 'healthy'),
        ('Hearts', 'hearts'),
        ('HeartLove', 'hlove'),
        ('Hot', 'hot'),
        ('LoveDiary', 'ldiary'),
        ('Lips', 'lips'),
        ('Love', 'love'),
        ('Lucky', 'lucky'),
        ('Makeup', 'mac'),
        ('Mask', 'maske'),
        ('Mood', 'mood'),
        ('Paint', 'paint'),
        ('Paper', 'paper'),
        ('Praise', 'praise'),
        ('Ramadan', 'ramadan'),
        ('Rock', 'rock'),
        ('School', 'school'),
        ('SelfieDecor', 'selfiedecoration'),
        ('Sticker', 'sticker'),
        ('Tag', 'tag'),
        ('Time', 'time'),
        ('Bash', 'bash'),
        ('Blast', 'blast'),
        ('Blocks', 'blocks'),
        ('Charm', 'charm'),
        ('Clipart', 'clipart'),
        ('Doodle', 'doodle'),
        ('Family', 'fam'),
        ('Favors', 'favors'),
        ('Followers', 'followers'),
        ('Free', 'free'),
        ('Fruit', 'fruit'),
        ('Gems', 'gems'),
        ('Happy', 'happy'),
        ('Happiness', 'happ'),
        ('Icons', 'icons'),
        ('Kids', 'kids'),
        ('Letters', 'letters'),
        ('SummerLove', 'lsum'),
        ('Memo', 'memo'),
        ('Peace', 'peace'),
        ('Post', 'pst'),
        ('SoOnline', 'soonline'),
        ('SpeechBubble', 'speechbubble'),
        ('Star', 'star'),
        ('StickFigure', 'stick'),
        ('Stripe', 'stipe'),
        ('Study', 'study'),
        ('SummerTime', 'sumtime'),
        ('Sunrise', 'sunrise'),
        ('Sweet', 'sweet'),
        ('Travel', 'travel'),
        ('Zodiac', 'zodiac'),
        ('Club', 'club'),
        ('Selfie', 'selfe'),
        ('Text', 'text'),
        ('Thug', 'thug'),
        ('Vaporwave', 'vapor'),
        ('Vibe', 'vibe'),
        ('Warm', 'warm'),
        ('Water', 'water'),
        ('Wedding', 'wedding'),
        ('Christmas', 'xmas'),
        ('Bird', 'bird'),
        ('CuteAnimals', 'cute_animals'),
        ('Flower', 'flower'),
        ('Food', 'food'),
        ('FreshFruit', 'fresh_fruit'),
        ('Kitty', 'kitty'),
        ('LoveTheme', 'love_theme'),
        ('NatureTheme', 'nature_theme'),
        ('NumberTag', 'number_tag'),
        ('Badges', 'badges')
    ]

    # Load original iStickers.json groups
    with open("iStickers.json") as f:
        old_st = json.load(f)

    all_files = set(os.listdir(src_dir))

    # Match each group from iStickers.json
    cat_to_files = {}
    for i, g in enumerate(old_st["data"]):
        cat_name, _ = sticker_groups_def[i]
        matched_files = []
        for d in g.get("details", []):
            b = os.path.basename(d.get("image", ""))
            candidates = [b, f"{b}.png", f"{b}.webp", f"{b}.jpg"]
            for cand in candidates:
                if cand in all_files:
                    matched_files.append(cand)
                    all_files.remove(cand)
                    break
        cat_to_files[cat_name] = matched_files

    # Category 108: Badges for remaining 10 files (1_1.png ... 10_1.png)
    cat_to_files['Badges'] = sorted(list(all_files), key=natural_sort_key)

    sorted_cat_names = sorted(cat_to_files.keys(), key=lambda s: s.lower())

    categories_list = []
    cat_id = 1
    total_items = 0

    for cat_name in sorted_cat_names:
        files = sorted(cat_to_files[cat_name], key=natural_sort_key)
        cat_folder = os.path.join(dest_dir, cat_name)
        os.makedirs(cat_folder, exist_ok=True)

        product_details = []
        for idx, orig_filename in enumerate(files, 1):
            stem, ext = os.path.splitext(orig_filename)
            new_filename = f"{idx}{ext}"
            src_path = os.path.join(src_dir, orig_filename)
            dest_path = os.path.join(cat_folder, new_filename)

            if os.path.exists(src_path):
                shutil.move(src_path, dest_path)

            product_details.append({
                "id": f"st_{cat_name.lower()}_{idx:03d}",
                "title": f"{cat_name} {idx}",
                "image": dest_path,
                "isPro": False
            })

        total_items += len(product_details)
        categories_list.append({
            "cat_id": cat_id,
            "cat_name": cat_name,
            "total_count": len(product_details),
            "product_details": product_details
        })
        cat_id += 1

    if os.path.exists(src_dir) and not os.listdir(src_dir):
        os.rmdir(src_dir)

    output_data = {
        "total_categories": len(categories_list),
        "total_items": total_items,
        "categories": categories_list
    }

    with open("iStickers.json", "w") as fp:
        json.dump(output_data, fp, indent=2)

    print(f"Stickers complete: {len(categories_list)} categories, {total_items} items written to iStickers.json.")


if __name__ == '__main__':
    organize_backgrounds()
    organize_stickers()
