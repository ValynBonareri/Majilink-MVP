from pathlib import Path
import struct
import numpy as np
import tifffile


FLOOD_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "flood"
)


def get_tags(data):
    # BigTIFF, little endian
    if data[:4] != b"II+\x00":
        raise ValueError("Expected little-endian BigTIFF.")

    ifd_offset = struct.unpack_from("<Q", data, 8)[0]
    count = struct.unpack_from("<Q", data, ifd_offset)[0]

    tags = {}

    for i in range(count):
        pos = ifd_offset + 8 + i * 20

        tag, dtype = struct.unpack_from("<HH", data, pos)
        count_value = struct.unpack_from("<Q", data, pos + 4)[0]

        sizes = {
            1: 1,
            2: 1,
            3: 2,
            4: 4,
            5: 8,
            12: 8,
            16: 8,
            17: 8,
            18: 8,
        }

        if dtype not in sizes:
            continue

        total = sizes[dtype] * count_value

        if total <= 8:
            raw = data[pos + 12:pos + 12 + total]
        else:
            value_offset = struct.unpack_from(
                "<Q",
                data,
                pos + 12
            )[0]

            raw = data[
                value_offset:value_offset + total
            ]

        if dtype == 3:
            values = struct.unpack(
                "<" + "H" * count_value,
                raw
            )

        elif dtype == 4:
            values = struct.unpack(
                "<" + "I" * count_value,
                raw
            )

        elif dtype == 16:
            values = struct.unpack(
                "<" + "Q" * count_value,
                raw
            )

        else:
            continue

        tags[tag] = values

    return tags


def lzw_decode(encoded):
    """
    TIFF LZW decoder.

    TIFF LZW codes are MSB-first.
    """

    CLEAR = 256
    EOI = 257

    dictionary = {
        i: bytes([i])
        for i in range(256)
    }

    next_code = 258
    code_size = 9
    bit_position = 0

    output = bytearray()
    previous = None

    def read_code():
        nonlocal bit_position

        if bit_position + code_size > len(encoded) * 8:
            return None

        value = 0

        for _ in range(code_size):
            byte_index = bit_position // 8
            bit_index = 7 - (bit_position % 8)

            value = (
                value << 1
            ) | (
                (encoded[byte_index] >> bit_index) & 1
            )

            bit_position += 1

        return value

    while True:
        code = read_code()

        if code is None:
            break

        if code == EOI:
            break

        if code == CLEAR:
            dictionary = {
                i: bytes([i])
                for i in range(256)
            }

            next_code = 258
            code_size = 9
            previous = None

            continue

        if code in dictionary:
            entry = dictionary[code]

        elif code == next_code and previous is not None:
            entry = previous + previous[:1]

        else:
            raise ValueError(
                f"Invalid LZW code {code} "
                f"(next={next_code}, "
                f"bits={code_size})"
            )

        output.extend(entry)

        if previous is not None:
            dictionary[next_code] = (
                previous + entry[:1]
            )

            next_code += 1

            # TIFF LZW changes from 9 bits to 10 bits
            # when the next available code reaches 511.
            if next_code == (1 << code_size) - 1:
                if code_size < 12:
                    code_size += 1

        previous = entry

    return bytes(output)
    


def read_flood_tiff(path):
    with open(path, "rb") as f:
        data = f.read()

    tags = get_tags(data)

    width = tags[256][0]
    height = tags[257][0]
    bits = tags[258][0]
    compression = tags[259][0]

    tile_width = tags[322][0]
    tile_height = tags[323][0]

    tile_offsets = tags[324]
    tile_byte_counts = tags[325]

    print(
        f"  image: {width} x {height}"
    )

    print(
        f"  tile: {tile_width} x {tile_height}"
    )

    print(
        f"  compression: {compression}"
    )

    if bits != 32:
        raise ValueError(
            "Expected 32-bit floating point data."
        )

    if compression != 5:
        raise ValueError(
            "Expected LZW compression."
        )

    tiles_across = (
        (width + tile_width - 1)
        // tile_width
    )

    tiles_down = (
        (height + tile_height - 1)
        // tile_height
    )

    raster = np.zeros(
        (height, width),
        dtype=np.float32
    )

    tile_number = 0

    for tile_row in range(tiles_down):

        for tile_col in range(tiles_across):

            offset = tile_offsets[tile_number]
            byte_count = tile_byte_counts[tile_number]

            compressed = data[
                offset:offset + byte_count
            ]

            decoded = lzw_decode(compressed)

            values = np.frombuffer(
                decoded,
                dtype="<f4"
            )

            expected_values = (
                tile_width * tile_height
            )

            if values.size < expected_values:
                raise ValueError(
                    f"Tile {tile_number} decoded "
                    f"to {values.size} values; "
                    f"expected {expected_values}."
                )

            tile = values[
                :expected_values
            ].reshape(
                tile_height,
                tile_width
            )

            row_start = (
                tile_row * tile_height
            )

            col_start = (
                tile_col * tile_width
            )

            row_end = min(
                row_start + tile_height,
                height
            )

            col_end = min(
                col_start + tile_width,
                width
            )

            raster[
                row_start:row_end,
                col_start:col_end
            ] = tile[
                :row_end - row_start,
                :col_end - col_start
            ]

            tile_number += 1

    return raster


def write_uncompressed(
    source,
    destination,
    raster
):
    with tifffile.TiffFile(source) as tif:
        page = tif.pages[0]

        scale = page.tags[
            "ModelPixelScaleTag"
        ].value

        tiepoint = page.tags[
            "ModelTiepointTag"
        ].value

        geokeys = page.tags[
            "GeoKeyDirectoryTag"
        ].value

        ascii_params = page.tags[
            "GeoAsciiParamsTag"
        ].value

        double_params = page.tags.get(
            "GeoDoubleParamsTag"
        )

        extratags = [
            (
                33550,
                "d",
                3,
                scale,
                False
            ),
            (
                33922,
                "d",
                6,
                tiepoint,
                False
            ),
            (
                34735,
                "H",
                len(geokeys),
                geokeys,
                False
            ),
            (
                34737,
                "s",
                len(ascii_params),
                ascii_params,
                False
            ),
        ]

        if double_params is not None:
            extratags.append(
                (
                    34736,
                    "d",
                    len(double_params.value),
                    double_params.value,
                    False
                )
            )

    tifffile.imwrite(
        destination,
        raster.astype(np.float32),
        compression=None,
        metadata=None,
        extratags=extratags,
    )


def main():

    files = {
        "10yr":
            "nairobi_aqueduct_riverine_10yr_baseline.tif",

        "25yr":
            "nairobi_aqueduct_riverine_25yr_baseline.tif",

        "50yr":
            "nairobi_aqueduct_riverine_50yr_baseline.tif",

        "100yr":
            "nairobi_aqueduct_riverine_100yr_baseline_v2.tif",
    }

    for period, filename in files.items():

        source = FLOOD_DIR / filename

        destination = (
            FLOOD_DIR
            / f"converted_{period}.tif"
        )

        print()
        print(f"Converting {filename}...")

        raster = read_flood_tiff(source)

        print(
            f"  minimum: "
            f"{np.nanmin(raster)}"
        )

        print(
            f"  maximum: "
            f"{np.nanmax(raster)}"
        )

        write_uncompressed(
            source,
            destination,
            raster
        )

        print(
            f"  saved: {destination}"
        )

    print()
    print(
        "Flood TIFF conversion completed."
    )


if __name__ == "__main__":
    main()