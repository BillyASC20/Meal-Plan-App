#!/usr/bin/env python3
"""
Create a small, fast-training subset of the YOLOv8 dataset.

This samples K classes and up to N images per class for both train and val,
and writes a new dataset folder with its own data.yaml.

Usage:
  python create_mini_dataset.py [--classes 15] [--per_class 100]

Defaults:
  Source dataset: datasets/food41-yolo
  Output dataset: datasets/food41-mini
"""

from pathlib import Path
import argparse
import shutil
import ast


def parse_names_from_yaml(yaml_path: Path):
    names_line = None
    with open(yaml_path, 'r') as f:
        for line in f:
            if line.strip().startswith('names:'):
                names_line = line.split(':', 1)[1].strip()
                break
    if not names_line:
        raise RuntimeError("Couldn't find 'names:' in data.yaml")
    # names: [a, b, c]
    names = ast.literal_eval(names_line)
    return names


def copy_subset(split_dir: Path, labels_dir: Path, out_images: Path, out_labels: Path,
                keep_ids: set[int], per_class: int, class_counts: dict[int, int]):
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    for lbl in labels_dir.glob('*.txt'):
        with open(lbl, 'r') as f:
            line = f.readline().strip()
        if not line:
            continue
        cls_id = int(line.split()[0])
        if cls_id not in keep_ids:
            continue
        # respect per-class cap
        if class_counts.get(cls_id, 0) >= per_class:
            continue

        img = split_dir / (lbl.stem + '.jpg')
        if not img.exists():
            # try png
            alt = split_dir / (lbl.stem + '.png')
            if not alt.exists():
                continue
            img = alt

        shutil.copy(img, out_images / img.name)
        shutil.copy(lbl, out_labels / lbl.name)
        class_counts[cls_id] = class_counts.get(cls_id, 0) + 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--classes', type=int, default=15, help='number of classes to keep')
    parser.add_argument('--per_class', type=int, default=100, help='max images per class per split')
    parser.add_argument('--src', default='datasets/food41-yolo', help='source YOLO dataset folder')
    parser.add_argument('--dst', default='datasets/food41-mini', help='output subset folder')
    args = parser.parse_args()

    src = Path(args.src)
    dst = Path(args.dst)
    yaml_path = src / 'data.yaml'
    if not yaml_path.exists():
        raise SystemExit(f"Source data.yaml not found: {yaml_path}")

    names = parse_names_from_yaml(yaml_path)
    keep_names = names[: args.classes]
    keep_ids = set(range(len(keep_names)))

    # Folder structure
    (dst / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (dst / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (dst / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (dst / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

    # Copy subsets
    class_counts_train = {}
    class_counts_val = {}
    copy_subset(src / 'images' / 'train', src / 'labels' / 'train', dst / 'images' / 'train', dst / 'labels' / 'train', keep_ids, args.per_class, class_counts_train)
    copy_subset(src / 'images' / 'val', src / 'labels' / 'val', dst / 'images' / 'val', dst / 'labels' / 'val', keep_ids, args.per_class, class_counts_val)

    # Write new data.yaml
    yaml = f"""# Mini Food-41 subset for quick training
path: {dst.resolve()}
train: images/train
val: images/val

nc: {len(keep_names)}
names: {keep_names}
"""
    with open(dst / 'data.yaml', 'w') as f:
        f.write(yaml)

    print('✅ Created mini dataset at', dst)
    print('   data.yaml:', dst / 'data.yaml')
    print('   Train images:', len(list((dst / 'images' / 'train').glob('*'))))
    print('   Val images:', len(list((dst / 'images' / 'val').glob('*'))))


if __name__ == '__main__':
    main()
