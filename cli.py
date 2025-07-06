# sensifilter/cli.py

# Command-line interface for batch image analysis
# cli.py

import os
import argparse
from tqdm import tqdm
from sensifilter.analyze import analyze_image


def find_images(path):
    """
    Returns a list of image file paths in given directory or single file.
    """
    exts = [".jpg", ".jpeg", ".png", ".webp"]
    if os.path.isdir(path):
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if os.path.splitext(f)[-1].lower() in exts
        ]
    elif os.path.isfile(path):
        return [path]
    else:
        return []


def main():
    parser = argparse.ArgumentParser(description="Analyze images for sensitive content")
    parser.add_argument("input", help="Image file or folder to scan")
    parser.add_argument("--output", help="Optional output file (json or csv)")
    parser.add_argument("--verbose", action="store_true", help="Print full results to console")
    args = parser.parse_args()

    images = find_images(args.input)
    if not images:
        print("No valid images found.")
        return

    results = []

    with tqdm(total=len(images), desc="Analyzing") as pbar:
        for img_path in images:
            result = analyze_image(img_path)
            result["path"] = img_path
            results.append(result)
            if args.verbose:
                print(f"\n{img_path}\n→ {result['label'].upper()} ({result.get('caption', '-')})\n")
            pbar.update(1)

    if args.output:
        if args.output.endswith(".json"):
            import json
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
        elif args.output.endswith(".csv"):
            import csv
            keys = results[0].keys()
            with open(args.output, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)

if __name__ == "__main__":
    main()
