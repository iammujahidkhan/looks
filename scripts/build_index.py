#!/usr/bin/env python3
"""
Script to scan circular frames across categories directory,
detect duplicates, sort categories and items, and generate index.json.
"""

import os
import sys
import hashlib
import json
import re
from collections import defaultdict

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def scan_and_build_index(categories_dir='categories', output_json='index.json'):
    if not os.path.exists(categories_dir):
        print(f"Error: {categories_dir} directory does not exist.")
        sys.exit(1)

    all_image_paths = []
    for root, dirs, files in os.walk(categories_dir):
        if '.git' in root or '.gemini' in root or 'scratch' in root:
            continue
        for f in files:
            if f.lower().endswith(('.png', '.webp', '.jpg', '.jpeg')):
                full_p = os.path.join(root, f)
                rel_p = os.path.normpath(full_p)
                all_image_paths.append(rel_p)

    print(f"Total image files found in {categories_dir}: {len(all_image_paths)}")

    # Group by category name (subfolder inside categories/)
    cat_to_files = defaultdict(list)
    hash_set = set()
    duplicates = []

    for p in all_image_paths:
        # Check hash for duplicate safety
        with open(p, 'rb') as fp:
            h = hashlib.md5(fp.read()).hexdigest()
        if h in hash_set:
            duplicates.append(p)
            continue
        hash_set.add(h)

        parts = p.split(os.sep)
        if len(parts) >= 2:
            cat_name = parts[1]
        else:
            cat_name = "Other"
        cat_to_files[cat_name].append(p)

    if duplicates:
        print(f"Found {len(duplicates)} duplicate files, removing them...")
        for dup in duplicates:
            if os.path.exists(dup):
                os.remove(dup)

    sorted_cat_names = sorted(cat_to_files.keys(), key=lambda s: s.lower())

    categories_list = []
    cat_id = 1
    total_frames = 0

    for cat_name in sorted_cat_names:
        flist = cat_to_files[cat_name]
        sorted_flist = sorted(flist, key=lambda f: natural_sort_key(os.path.basename(f)))

        product_details = []
        for idx, fpath in enumerate(sorted_flist, 1):
            product_details.append({
                "id": f"{cat_name.lower()}_{idx:03d}",
                "title": f"{cat_name} {idx}",
                "image": fpath,
                "isPro": False
            })

        total_frames += len(product_details)
        categories_list.append({
            "cat_id": cat_id,
            "cat_name": cat_name,
            "total_count": len(product_details),
            "product_details": product_details
        })
        cat_id += 1

    output_data = {
        "total_categories": len(categories_list),
        "total_frames": total_frames,
        "categories": categories_list
    }

    with open(output_json, 'w') as fp:
        json.dump(output_data, fp, indent=2)

    print(f"Generated {output_json} with {len(categories_list)} categories and {total_frames} total frames.")

if __name__ == '__main__':
    scan_and_build_index()
