from PIL import Image
from struct import Struct
from argparse import ArgumentParser, FileType
from pathlib import Path
import json
import sys
import os


SIZE = (64, 32)

# Unpack an int to bytes
int_to_bytes = Struct('>I').pack


def create_image(pixel_matrix: list[list[int]]) -> Image.Image:
    bytearr = []
    for row in pixel_matrix:
        for p in row:
            bytearr += int_to_bytes(p & 0xFFFFFF)  # masked to fill the bytes
    im = Image.frombuffer("RGB", SIZE, bytes(bytearr))
    return im


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("log", type=FileType('r'),
                        help="log file to parse")
    parser.add_argument("destination", type=Path, nargs='?', default='./images',
                        help="folder to put the generated images into")

    args = parser.parse_args()

    if not args.destination.is_dir():
        print(f"Cannot find directory: {args.destination}", file=sys.stderr)
        sys.exit(1)

    last_ts = None
    frame_id = 1
    for line in args.log:
        line = line.strip()
        if not line:
            continue
        ts = line[:10]  # timestamp
        data = json.loads(line[11:])

        # Ignore lines with duplicate timestamps
        if last_ts and ts == last_ts:
            continue

        image = create_image(data['matrix'])
        target_image = args.destination.joinpath(f'{frame_id:08d}.png')
        print(f'[{ts}] {target_image}')
        image.save(target_image)
        last_ts = ts
        frame_id += 1
