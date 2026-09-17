#!/usr/bin/env python3
"""
Intake tool for new JL Fitness photos.

Sorts a folder of incoming photos into <target>/<YYYY-MM>/ (falling back to
<target>/Unknown_Date/) based on EXIF capture date, and flags exact
duplicates by content hash so they don't get added to the gallery twice.

Usage:
    python scripts/organize_photos.py <source_dir> <target_dir> [--move]

By default files are copied, leaving the source folder untouched; pass
--move to relocate them instead.
"""
import argparse
import hashlib
import os
import shutil
from datetime import datetime

from PIL import Image

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg')


def get_file_hash(filepath, chunk_size=1024 * 1024):
    """Generates an MD5 hash to identify exact duplicate files."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_category_folder(filepath):
    """Returns a YYYY-MM folder name from EXIF DateTimeOriginal, or Unknown_Date."""
    try:
        with Image.open(filepath) as img:
            exif = img.getexif()
            date_str = exif.get(36867)  # DateTimeOriginal
        if date_str:
            dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            return dt.strftime('%Y-%m')
    except Exception:
        pass
    return 'Unknown_Date'


def unique_destination(dest_folder, filename):
    """Avoids overwriting an existing file with a different one of the same name."""
    dest_path = os.path.join(dest_folder, filename)
    if not os.path.exists(dest_path):
        return dest_path
    stem, ext = os.path.splitext(filename)
    n = 1
    while True:
        candidate = os.path.join(dest_folder, f'{stem}_{n}{ext}')
        if not os.path.exists(candidate):
            return candidate
        n += 1


def organize_and_find_duplicates(source_dir, target_dir, move=False):
    seen_hashes = {}
    duplicates = []
    transfer = shutil.move if move else shutil.copy2

    for root, _, files in os.walk(source_dir):
        for file in files:
            if not file.lower().endswith(IMAGE_EXTENSIONS):
                continue

            filepath = os.path.join(root, file)
            file_hash = get_file_hash(filepath)

            if file_hash in seen_hashes:
                duplicates.append((filepath, seen_hashes[file_hash]))
                continue
            seen_hashes[file_hash] = filepath

            category_folder = get_category_folder(filepath)
            dest_folder = os.path.join(target_dir, category_folder)
            os.makedirs(dest_folder, exist_ok=True)
            transfer(filepath, unique_destination(dest_folder, file))

    return duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_dir', help='Folder of incoming photos to sort')
    parser.add_argument('target_dir', help='Folder to organize photos into, by month')
    parser.add_argument('--move', action='store_true',
                         help='Move files instead of copying them')
    args = parser.parse_args()

    duplicates = organize_and_find_duplicates(args.source_dir, args.target_dir, args.move)

    print(f'Found {len(duplicates)} duplicate(s).')
    for dup, original in duplicates:
        print(f'  {dup} is a duplicate of {original}')


if __name__ == '__main__':
    main()
