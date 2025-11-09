from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path
from typing import Iterable, List


SUPPORTED_EXTS = {
	".jpg",
	".jpeg",
	".png",
	".webp",
	".bmp",
	".tif",
	".tiff",
	".heic",
	".heif",
	".gif",  # will convert only first frame
}


def find_images(dir_path: Path) -> List[Path]:
	files: List[Path] = []
	for p in sorted(dir_path.iterdir()):
		if not p.is_file():
			continue
		if p.name.startswith("."):
			continue
		if p.suffix.lower() in SUPPORTED_EXTS:
			files.append(p)
	return files


def has_pillow() -> bool:
	try:
		import PIL  # noqa: F401
		return True
	except Exception:
		return False


def convert_to_jpg(src: Path, dst: Path) -> None:
	"""Convert an image file to JPEG and save to dst.

	- Preserves correct orientation via EXIF
	- Flattens transparency over white background
	- For GIFs, saves the first frame
	"""
	from PIL import Image, ImageOps, UnidentifiedImageError

	try:
		im = Image.open(src)
	except UnidentifiedImageError as e:
		raise RuntimeError(f"Unsupported or corrupted image: {src}") from e

	# handle animated GIF: pick first frame
	try:
		if getattr(im, "is_animated", False):
			im.seek(0)
	except Exception:
		pass

	# auto-rotate using EXIF
	try:
		im = ImageOps.exif_transpose(im)
	except Exception:
		pass

	# Convert to RGB, flatten if alpha
	if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
		background = Image.new("RGB", im.size, (255, 255, 255))
		if im.mode in ("RGBA", "LA"):
			alpha = im.split()[-1]
			background.paste(im.convert("RGB"), mask=alpha)
		else:
			# P mode with transparency
			background.paste(im.convert("RGB"))
		im = background
	else:
		im = im.convert("RGB")

	dst.parent.mkdir(parents=True, exist_ok=True)
	im.save(dst, format="JPEG", quality=90, optimize=True, progressive=True)


def main(argv: Iterable[str] | None = None) -> int:
	parser = argparse.ArgumentParser(
		description=(
			"Convert images in assets/carousel to sequential JPGs: 001.jpg, 002.jpg, ..."
		)
	)
	parser.add_argument(
		"--dir",
		default=str(Path("assets") / "carousel"),
		help="Directory to process (default: assets/carousel)",
	)
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Show planned operations without changing files",
	)
	parser.add_argument(
		"--pad",
		type=int,
		default=3,
		help="Zero-padding width for numbering (default: 3 => 001.jpg)",
	)

	args = parser.parse_args(list(argv) if argv is not None else None)

	base_dir = Path(args.dir)
	if not base_dir.exists() or not base_dir.is_dir():
		print(f"Directory not found: {base_dir}", file=sys.stderr)
		return 2

	items = find_images(base_dir)
	if not items:
		print(f"No supported images found in {base_dir}")
		return 0

	count = len(items)
	pad = max(args.pad, len(str(count)))

	# Build plan: for each input, create a unique temp jpg, then final rename
	temp_targets: List[Path] = []
	final_targets: List[Path] = []
	ops: List[str] = []

	need_pillow = any(p.suffix.lower() not in {".jpg", ".jpeg"} for p in items)
	if need_pillow and not has_pillow():
		print(
			"Pillow (PIL) is required to convert non-JPEG images.\n"
			"Install it with: pip install pillow",
			file=sys.stderr,
		)
		return 3

	# First phase: produce temp files
	for idx, src in enumerate(items, start=1):
		final_name = f"{idx:0{pad}d}.jpg"
		final_path = base_dir / final_name
		tmp_name = f".{final_name}.tmp-{uuid.uuid4().hex}.jpg"
		tmp_path = base_dir / tmp_name
		final_targets.append(final_path)
		temp_targets.append(tmp_path)

		if src.suffix.lower() in {".jpg", ".jpeg"}:
			# If already JPEG, just copy to temp (avoid re-encoding)
			ops.append(f"COPY  {src.name}  ->  {tmp_path.name}")
			if not args.dry_run:
				import shutil

				shutil.copy2(src, tmp_path)
		else:
			ops.append(f"CONVERT {src.name}  ->  {tmp_path.name}")
			if not args.dry_run:
				convert_to_jpg(src, tmp_path)

	# Second phase: remove originals (only ones that conflict), then rename temps to final
	for src in items:
		# If a file has the same name as a final target (e.g., already numbered), remove it to avoid rename conflicts
		if src.name.endswith(".jpg") and src in final_targets:
			# This case is rare due to Path vs names, keep safe behavior
			pass

		if not args.dry_run:
			try:
				src.unlink(missing_ok=True)
			except Exception as e:
				print(f"Warning: could not remove {src.name}: {e}", file=sys.stderr)

	for tmp_path, final_path in zip(temp_targets, final_targets):
		ops.append(f"RENAME {tmp_path.name} -> {final_path.name}")
		if not args.dry_run:
			try:
				# If a file with final name exists (e.g., from previous runs), replace it
				if final_path.exists():
					final_path.unlink()
				os.replace(tmp_path, final_path)
			except Exception as e:
				print(
					f"Error: could not rename {tmp_path.name} to {final_path.name}: {e}",
					file=sys.stderr,
				)
				return 4

	# Print summary
	print(f"Processed {count} image(s) in {base_dir}")
	for line in ops:
		print(line)

	if args.dry_run:
		print("\nDry-run only: no files were changed.")

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

