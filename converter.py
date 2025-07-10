from __future__ import annotations

import math
import subprocess
import tempfile
from enum import Enum
from pathlib import Path

from constants import (
    MAGICK_PATH,
    ImageSize,
    ImageType,
    IndexedColor,
    OutlineStyle,
)


class Dimension:
    width: int
    height: int

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @property
    def pixels(self) -> int:
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    def scale(self, factor: int) -> Dimension:
        return Dimension(self.width * factor, self.height * factor)

    def limit_pixels(self, pixels: int) -> Dimension:
        ratio = self.aspect_ratio
        height = math.sqrt(pixels / ratio)
        width = height * ratio
        return Dimension(int(width), int(height))

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, Dimension)
            and self.width == value.width
            and self.height == value.height
        )

    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

    def __lt__(self, value: object) -> bool:
        return isinstance(value, Dimension) and self.pixels < value.pixels

    def __gt__(self, value: object) -> bool:
        return isinstance(value, Dimension) and self.pixels > value.pixels


class DimensionPreset(Dimension, Enum):
    FULL = 632, 420
    YADO = 400, 260
    CARD = 74, 94

    @classmethod
    def of(cls, name: str | ImageSize):
        values = cls.__members__
        name = name.name if isinstance(name, ImageSize) else name.upper()
        return values[name] if name in values else None


def convert(
    path: str | Path,
    output_dir: str | Path,
    image_size: ImageSize = ImageSize.ASIS,
    image_size_2x: bool = False,
    image_size_4x: bool = False,
    image_type: ImageType = ImageType.BMP,
    indexed_color: IndexedColor = IndexedColor.NONE,
    color_mask: bool = False,
    outline_style: OutlineStyle = OutlineStyle.NONE,
) -> None:

    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_size = get_dimension(path)
    target_size = DimensionPreset.of(image_size)
    colors = indexed_color.number

    for x in 1, 2, 4:
        if x == 2 and not image_size_2x:
            continue
        if x == 4 and not image_size_4x:
            continue

        ext = f".{image_type.ext}" if x == 1 else f".x{x}.{image_type.ext}"
        output_path = (output_dir / path.name).with_suffix(ext)
        output_size = target_size.scale(x) if target_size else source_size

        # -remap mpr:palette ではうまくいかない
        palette_path = Path(tempfile.mktemp(suffix=".png"))

        # 左上ピクセルから背景色を設定
        # PNG圧縮は遅いので一時ファイル用に圧縮レベルを下げておく
        params = """
        -background %[pixel:p{0,0}]
        -define png:compression-level=1
        """

        if colors:
            # インデックスカラーにアルファチャンネルは不要
            params += """
            -alpha off
            """

        if color_mask:
            # ただし透過色を保護する場合はアルファチャンネルを使う
            params += """
            -alpha set
            -transparent %[pixel:p{0,0}]
            """

        if target_size:
            params += f"""
            -gravity Center
            -filter Hermite
            -resize {output_size}^
            -crop {output_size}+0+0 +repage
            """

            if output_size.pixels < 0x8000 and output_size != source_size:
                # 出力サイズが小さい場合はシャープフィルタをかける
                params += """
                -channel RGB
                -sharpen 0x.75
                """

        if color_mask:
            # リサイズでぼやけたアルファチャンネルを2値化
            params += """
            -channel A
            -threshold 50%
            """

        params += """
        -write mpr:base
        """

        if color_mask:

            if fill := outline_style.inner:
                params += f"""
                -alpha remove
                +transparent %[pixel:p{{0,0}}]
                -channel A
                -morphology Dilate Diamond
                -transparent %[pixel:p{{0,0}}]
                -channel RGB
                -fill {fill}
                -colorize 100%

                mpr:base
                +swap
                -channel RGBA
                -composite
                -write mpr:base
                """

            if fill := outline_style.outer:
                params += f"""
                -channel A
                -morphology Dilate Diamond
                -channel RGB
                -fill {fill}
                -colorize 100%

                mpr:base
                -channel RGBA
                -composite
                -write mpr:base
                """

        if colors:
            # 重いので大きな画像はピクセル数と色数を減らして計算
            temp_size = source_size.limit_pixels(0x50000)

            params += f"""
            -channel RGB
            -filter Point
            -resize {temp_size}>
            +dither
            -colors {0x800}
            -kmeans {colors}
            -channel RGBA
            -write {palette_path}
            +delete

            mpr:base
            -define dither:diffusion-amount=75%
            -dither FloydSteinberg
            -remap {palette_path}
            """

        if colors or color_mask:
            # -alpha remove で背景色を反映
            # -alpha off +remap を省くとBMPがインデックスカラーにならない
            params += """
            -alpha remove
            -alpha off +remap
            """

        if image_type == ImageType.BMP:
            params += """
            -define bmp:format=bmp2
            """

        elif image_type == ImageType.PNG:
            params += """
            -define png:compression-level=9
            -define png:compression-filter=5
            """

        elif image_type == ImageType.JPEG:
            params += """
            -define jpeg:dct-method=fast
            -sampling-factor 4:2:0
            -quality 85
            -interlace JPEG
            """

        params += "-strip"
        params = params.strip().split()

        if magick(path, *params, output_path).returncode == 0:
            print(output_path)

        palette_path.unlink(True)

        if image_size == ImageSize.ASIS:
            break


def get_dimension(path: str | Path):
    result = magick("identify", "-format", "%w %h", path)
    width, height = result.stdout.split()
    return Dimension(int(width), int(height))


def magick(*params: str | Path):
    return subprocess.run(
        (MAGICK_PATH / "magick", *params),
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
