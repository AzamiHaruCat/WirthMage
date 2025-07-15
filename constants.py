import sys
from enum import StrEnum
from functools import cached_property
from pathlib import Path

APP_NAME = "WirthMage🧙"
WINDOW_TITLE = f"{APP_NAME} :: CardWirth用画像コンバータ"

ROOT_PATH = (
    Path(__file__).parent
    if Path(sys.executable).name.startswith("python")
    else Path(sys.executable).parent
)
RESOURCE_PATH = Path(__file__).parent
ASSETS_PATH = RESOURCE_PATH / "assets"
MAGICK_PATH = RESOURCE_PATH / "lib/ImageMagick"
INPUT_PATH = Path.home() / "Pictures"
OUTPUT_PATH = ROOT_PATH / "output"
CONFIG_JSON = ROOT_PATH / "config.json"

INPUT_FILES_LABEL = "入力ファイル"
ADD_LABEL = "追加"
REMOVE_LABEL = "除外"
CLEAR_LABEL = "クリア"
OUTPUT_DIR_LABEL = "出力フォルダ"
CHANGE_LABEL = "変更"
OPEN_LABEL = "開く"
OUTPUT_SIZE_LABEL = "出力サイズ"
OUTPUT_X2_LABEL = "2倍サイズ"
OUTPUT_X4_LABEL = "4倍サイズ"
OUTPUT_FORMAT_LABEL = "出力形式"
INDEXED_COLOR_LABEL = "減色"
COLOR_MASK_LABEL = "透過色を保護"
OUTLINE_STYLE_LABEL = "縁取り"
NOTICE_MESSAGES = (
    "※入力ファイルを変換し、出力フォルダに保存します。",
    "※出力フォルダ内の同名ファイルは上書きされます。",
)
EXECUTE_LABEL = "実行"
QUIT_LABEL = "終了"

PROGRESS_TITLE = "進行中..."
PROGRESS_LABEL = "{total}件中{current}番目が進行中..."
CANCEL_LABEL = "キャンセル"

FILE_DIALOG_TITLE = f"入力ファイルを選択 :: {APP_NAME}"
FOLDER_DIALOG_TITLE = f"出力フォルダを選択 :: {APP_NAME}"
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
        c = self.name[-4]
        return 1 << int(c) if c.isdigit() else 0


class OutlineStyle(StrEnum):
    NONE = "なし"
    INNER_BLACK = "黒"
    OUTER_BLACK = "黒(外側)"
    INNER_WHITE = "白"
    OUTER_WHITE = "白(外側)"
    INNER_BLACK_OUTER_WHITE = "黒+白(外側)"
    INNER_WHITE_OUTER_BLACK = "白+黒(外側)"

    @cached_property
    def inner(self) -> str | None:
        return (
            "black"
            if "INNER_BLACK" in self.name
            else "white" if "INNER_WHITE" in self.name else None
        )

    @cached_property
    def outer(self) -> str | None:
        return (
            "black"
            if "OUTER_BLACK" in self.name
            else "white" if "OUTER_WHITE" in self.name else None
        )
