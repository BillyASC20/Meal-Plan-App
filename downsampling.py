import os
import random
import shutil
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# --- Configuration ---
DATASET_DIR = Path('FinalDataset')
TARGET_MAX = 5000  # Target maximum samples per class
PROTECT_THRESHOLD = 1000  # Protect classes with fewer samples
BACKUP_DIR = Path('FinalDataset_backup_before_smart_downsample')
DRY_RUN = False  # Set to False to actually delete

MASTER_NAMES = {
    'almond': 0, 'apple': 1, 'apricot': 2, 'artichoke': 3, 'asparagus': 4,
    'avocado': 5, 'bacon': 6, 'banana': 7, 'bean_curd_tofu': 8, 'beef': 9,
    'beetroot': 10, 'bell_pepper': 11, 'black_pepper': 12, 'blackberry': 13,
    'blueberry': 14, 'bread': 15, 'brie_cheese': 16, 'broccoli': 17,
    'brown_sugar': 18, 'brussels_sprouts': 19, 'butter': 20, 'buttermilk': 21,
    'button_mushroom': 22, 'cabbage': 23, 'cantaloupe': 24, 'carrot': 25,
    'cashew_nut': 26, 'cauliflower': 27, 'cayenne_pepper': 28, 'celery': 29,
    'cheese': 30, 'cherry': 31, 'chicken': 32, 'chicken_stock': 33,
    'chicken_wing': 34, 'chickpea': 35, 'chili': 36, 'cilantro': 37,
    'cinnamon': 38, 'clementine': 39, 'coconut': 40, 'corn': 41,
    'cucumber': 42, 'date': 43, 'egg': 44, 'eggplant': 45, 'fig': 46,
    'fish': 47, 'flour': 48, 'garlic': 49, 'ginger': 50, 'gourd': 51,
    'grape': 52, 'green_bean': 53, 'green_grape': 54, 'ham': 55,
    'jalapeno': 56, 'jam': 57, 'ketchup': 58, 'kiwi': 59, 'ladyfinger': 60,
    'lemon': 61, 'lettuce': 62, 'lime': 63, 'mandarin_orange': 64,
    'mayonnaise': 65, 'meat': 66, 'medjool_dates': 67, 'melon': 68,
    'milk': 69, 'mozarella_cheese': 70, 'mushroom': 71, 'mussel': 72,
    'mustard': 73, 'noodle': 74, 'olive_oil': 75, 'onion': 76, 'orange': 77,
    'oyster': 78, 'papaya': 79, 'paprika': 80, 'parmesan_cheese': 81,
    'pasta': 82, 'pea': 83, 'peach': 84, 'pear': 85, 'pickle': 86,
    'pineapple': 87, 'pork': 88, 'pork_rib': 89, 'potato': 90, 'pumpkin': 91,
    'radish': 92, 'raspberry': 93, 'red_beans': 94, 'red_pepper': 95,
    'rice': 96, 'salmon': 97, 'salt': 98, 'shrimp': 99, 'spaghetti': 100,
    'spinach': 101, 'spring_onion': 102, 'strawberry': 103, 'sweetcorn': 104,
    'sweet_potato': 105, 'tomato': 106, 'tuna': 107, 'turnip': 108,
    'vegetable_oil': 109, 'watermelon': 110, 'white_sugar': 111, 'yeast': 112,
    'yogurt': 113, 'zucchini': 114
}

INDEX_TO_NAME = {idx: name for name, idx in MASTER_NAMES.items()}

def analyze_dataset(split_dir):
    """Analyze dataset and categorize images"""
    labels_dir = split_dir / 'labels'
    
    # Map class_id -> list of (image_stem, instance_count, is_pure)
    class_to_images = defaultdict(list)
    
    # Map image_stem -> {class_id: count}
    image_to_class_counts = {}
    
    for label_file in labels_dir.glob('*.txt'):
        image_stem = label_file.stem
        class_counts = defaultdict(int)
        
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts:
                    class_id = int(parts[0])
                    class_counts[class_id] += 1
        
        image_to_class_counts[image_stem] = dict(class_counts)
        
        # Add to each class's image list
        for class_id, count in class_counts.items():
            is_pure = (len(class_counts) == 1)  # Only this class in image
            class_to_images[class_id].append((image_stem, count, is_pure))
    
    return class_to_images, image_to_class_counts

def smart_downsample(split_dir, class_to_images, image_to_class_counts, dry_run=True):
    """Intelligently downsample high-count classes"""
    
    images_dir = split_dir / 'images'
    labels_dir = split_dir / 'labels'
    
    # Step 1: Identify protected classes
    protected_classes = set()
    for class_id, image_data in class_to_images.items():
        total_instances = sum(count for _, count, _ in image_data)
        if total_instances < PROTECT_THRESHOLD:
            protected_classes.add(class_id)
    
    print(f"\n  Protected classes (<{PROTECT_THRESHOLD} instances): {len(protected_classes)}")
    
    # Step 2: For each high-count class, select images to remove
    files_to_remove = set()
    stats = []
    
    for class_id, image_data in class_to_images.items():
        class_name = INDEX_TO_NAME.get(class_id, f"unknown_{class_id}")
        
        # Calculate current totals
        total_instances = sum(count for _, count, _ in image_data)
        total_images = len(image_data)
        
        # Skip if below target
        if total_instances <= TARGET_MAX:
            continue
        
        # Separate pure images from mixed images
        pure_images = [(stem, count) for stem, count, is_pure in image_data if is_pure]
        mixed_images = [(stem, count) for stem, count, is_pure in image_data if not is_pure]
        
        # Further filter mixed images: only removable if they don't contain protected classes
        truly_removable_mixed = []
        for stem, count in mixed_images:
            classes_in_image = set(image_to_class_counts[stem].keys())
            if not (classes_in_image & protected_classes):  # No protected classes
                truly_removable_mixed.append((stem, count))
        
        pure_instances = sum(count for _, count in pure_images)
        mixed_removable_instances = sum(count for _, count in truly_removable_mixed)
        protected_mixed_instances = total_instances - pure_instances - mixed_removable_instances
        
        # Calculate how many instances to remove
        instances_to_remove = total_instances - TARGET_MAX
        
        # Strategy: Remove pure images first, then removable mixed images
        instances_removed = 0
        images_to_remove = []
        
        # Phase 1: Remove pure images (safest)
        random.seed(42 + class_id)
        random.shuffle(pure_images)
        
        for stem, count in pure_images:
            if instances_removed >= instances_to_remove:
                break
            images_to_remove.append(stem)
            instances_removed += count
        
        # Phase 2: Remove removable mixed images if needed
        if instances_removed < instances_to_remove:
            random.shuffle(truly_removable_mixed)
            for stem, count in truly_removable_mixed:
                if instances_removed >= instances_to_remove:
                    break
                images_to_remove.append(stem)
                instances_removed += count
        
        files_to_remove.update(images_to_remove)
        
        final_instances = total_instances - instances_removed
        final_images = total_images - len(images_to_remove)
        
        stats.append({
            'id': class_id,
            'name': class_name,
            'before_instances': total_instances,
            'before_images': total_images,
            'after_instances': final_instances,
            'after_images': final_images,
            'removed_images': len(images_to_remove),
            'removed_instances': instances_removed,
            'pure_images': len(pure_images),
            'pure_removed': sum(1 for stem in images_to_remove if stem in [s for s, _ in pure_images]),
            'mixed_removable': len(truly_removable_mixed),
            'protected_mixed_instances': protected_mixed_instances,
            'target': TARGET_MAX
        })
    
    # Actually remove files
    if not dry_run:
        for image_stem in tqdm(files_to_remove, desc=f"Removing from {split_dir.name}"):
            # Remove image
            for ext in ['.jpg', '.png', '.jpeg']:
                img_file = images_dir / f"{image_stem}{ext}"
                if img_file.exists():
                    img_file.unlink()
                    break
            
            # Remove label
            label_file = labels_dir / f"{image_stem}.txt"
            if label_file.exists():
                label_file.unlink()
    
    return stats, len(files_to_remove)

def main():
    print("="*80)
    print("Smart Downsampling Tool")
    print("="*80)
    print(f"Target max instances per class: {TARGET_MAX}")
    print(f"Protection threshold: {PROTECT_THRESHOLD} (classes below this are protected)")
    print(f"Strategy: Remove PURE images first, then mixed images without protected classes")
    print(f"Mode: {'DRY RUN (simulation only)' if DRY_RUN else 'LIVE (will delete files)'}")
    print("="*80)
    
    if not DRY_RUN:
        response = input("\n⚠️  WARNING: This will permanently delete files! Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
        
        # Create backup
        print(f"\nCreating backup at {BACKUP_DIR}...")
        if BACKUP_DIR.exists():
            print("Backup already exists, skipping...")
        else:
            shutil.copytree(DATASET_DIR, BACKUP_DIR)
            print("✓ Backup created")
    
    splits = ['train', 'val']
    all_stats = {}
    
    for split in splits:
        split_dir = DATASET_DIR / split
        
        if not split_dir.exists():
            print(f"\n⚠️  {split} split not found, skipping...")
            continue
        
        print(f"\n{'='*80}")
        print(f"Analyzing {split.upper()} split...")
        print(f"{'='*80}")
        
        class_to_images, image_to_class_counts = analyze_dataset(split_dir)
        stats, files_removed = smart_downsample(split_dir, class_to_images, image_to_class_counts, dry_run=DRY_RUN)
        all_stats[split] = stats
        
        if stats:
            print(f"\nClasses to downsample in {split}:")
            print(f"{'Class':<20} {'Before':<12} {'After':<12} {'Removed':<10} "
                  f"{'Pure Rm':<8} {'Protected':<10}")
            print("-"*80)
            
            for s in sorted(stats, key=lambda x: x['before_instances'], reverse=True):
                status = "✓" if s['after_instances'] <= s['target'] else f"({s['after_instances'] - s['target']} over)"
                print(f"{s['name']:<20} "
                      f"{s['before_instances']:>6} ({s['before_images']:>3}i) "
                      f"{s['after_instances']:>6} ({s['after_images']:>3}i) "
                      f"{s['removed_instances']:>4} ({s['removed_images']:>2}i) "
                      f"{s['pure_removed']:<8} "
                      f"{s['protected_mixed_instances']:<10} {status}")
            
            print(f"\n  Total files to remove from {split}: {files_removed}")
        else:
            print(f"\n  No classes need downsampling in {split}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    # Collect all classes that were downsampled
    downsampled_classes = []
    total_instances_before = 0
    total_instances_after = 0
    total_images_removed = 0
    
    for split, stats_list in all_stats.items():
        for s in stats_list:
            downsampled_classes.append({
                'split': split,
                'id': s['id'],
                'name': s['name'],
                'before_instances': s['before_instances'],
                'after_instances': s['after_instances'],
                'removed_instances': s['removed_instances'],
                'removed_images': s['removed_images']
            })
            total_instances_before += s['before_instances']
            total_instances_after += s['after_instances']
            total_images_removed += s['removed_images']
    
    if downsampled_classes:
        print(f"\nClasses that had downsampling applied:")
        print("-" * 80)
        
        # Group by class (combine train/val)
        class_summary = defaultdict(lambda: {'splits': [], 'before': 0, 'after': 0, 'removed_inst': 0, 'removed_imgs': 0})
        for dc in downsampled_classes:
            key = f"{dc['name']} (ID {dc['id']})"
            class_summary[key]['splits'].append(dc['split'])
            class_summary[key]['before'] += dc['before_instances']
            class_summary[key]['after'] += dc['after_instances']
            class_summary[key]['removed_inst'] += dc['removed_instances']
            class_summary[key]['removed_imgs'] += dc['removed_images']
        
        for class_key in sorted(class_summary.keys()):
            info = class_summary[class_key]
            splits_str = "+".join(info['splits'])
            print(f"  • {class_key:<30} [{splits_str}]")
            print(f"    Before: {info['before']:>6} instances  →  After: {info['after']:>6} instances")
            print(f"    Removed: {info['removed_inst']:>5} instances across {info['removed_imgs']:>3} images")
        
        print(f"\n{'='*80}")
        print(f"Total instances before: {total_instances_before:,}")
        print(f"Total instances after:  {total_instances_after:,}")
        print(f"Total instances removed: {total_instances_before - total_instances_after:,}")
        print(f"Total images removed: {total_images_removed:,}")
        
        print(f"\n💡 Strategy used:")
        print(f"   1. Pure images (only target class) removed first")
        print(f"   2. Mixed images without protected classes removed second")
        print(f"   3. Mixed images with protected classes (<{PROTECT_THRESHOLD}) kept")
    else:
        print("✓ No downsampling needed! All classes are balanced.")
    
    if DRY_RUN:
        print(f"\n{'='*80}")
        print("🔍 DRY RUN COMPLETE - No files were deleted")
        print("Set DRY_RUN = False to execute the downsampling")
        print(f"{'='*80}")
    else:
        print(f"\n{'='*80}")
        print("✓ DOWNSAMPLING COMPLETE")
        print(f"Backup saved at: {BACKUP_DIR}")
        print(f"{'='*80}")

if __name__ == '__main__':
    main()