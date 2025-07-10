import sys
from enum import StrEnum
from pathlib import Path

APP_NAME = "WirthMage🧙"
WINDOW_TITLE = f"{APP_NAME} :: CardWirth用画像コンバータ"
FILE_DIALOG_TITLE = f"入力ファイルを選択 :: {APP_NAME}"
FOLDER_FIALOG_TITLE = f"出力フォルダを選択 :: {APP_NAME}"
ROOT_PATH = Path(
    __file__
    if Path(sys.executable).name.startswith("python")
    else sys.executable
).parent
INPUT_PATH = Path.home() / "Pictures"
OUTPUT_PATH = ROOT_PATH / "output"
MAGICK_PATH = ROOT_PATH / "lib/ImageMagick"
CONFIG_JSON = ROOT_PATH / "config.json"
IMAGE_TYPES = (
    ("画像ファイル", "*.bmp;*.png;*.jpg;*.jpeg;*.gif"),
    ("すべてのファイル", "*.*"),
)


class ImageSize(StrEnum):
    ASIS = "そのまま"
    FULL = "フルサイズ"
    YADO = "冒険者の宿"
    CARD = "カード"


class ImageType(StrEnum):
    BMP = "BMP"
    PNG = "PNG"
    JPEG = "JPEG"

    @property
    def ext(self):
        return self.lower() if self.name != "JPEG" else "jpg"


class IndexedColor(StrEnum):
    NONE = "なし"
    INDEXED_8BIT = "256色 (8-bit)"
    INDEXED_7BIT = "128色"
    INDEXED_6BIT = "64色"
    INDEXED_5BIT = "32色"
    INDEXED_4BIT = "16色 (4-bit)"
    INDEXED_3BIT = "8色"
    INDEXED_2BIT = "4色"
    INDEXED_1BIT = "2色"

    @property
    def number(self):
        return 0 if self.name == "NONE" else 1 << int(self.name[-4])


class OutlineStyle(StrEnum):
    NONE = "なし"
    INNER_BLACK = "黒"
    OUTER_BLACK = "黒(外側)"
    INNER_WHITE = "白"
    OUTER_WHITE = "白(外側)"
    INNER_BLACK_OUTER_WHITE = "黒+白(外側)"
    INNER_WHITE_OUTER_BLACK = "白+黒(外側)"

    @property
    def inner(self) -> str | None:
        return (
            "black"
            if "INNER_BLACK" in self.name
            else "white" if "INNER_WHITE" in self.name else None
        )

    @property
    def outer(self) -> str | None:
        return (
            "black"
            if "OUTER_BLACK" in self.name
            else "white" if "OUTER_WHITE" in self.name else None
        )
