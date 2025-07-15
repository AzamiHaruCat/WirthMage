import json
from enum import Enum
from pathlib import Path
from typing import Any

from constants import (
    OUTPUT_PATH,
    ImageSize,
    ImageType,
    IndexedColor,
    OutlineStyle,
)


class ConverterParams:
    input_files: dict[str, Path]
    output_dir: Path
    image_size: ImageSize = ImageSize.ASIS
    output_x2: bool = False
    output_x4: bool = False
    image_type: ImageType = ImageType.BMP
    indexed_color: IndexedColor = IndexedColor.NONE
    color_mask: bool = False
    outline_style: OutlineStyle = OutlineStyle.NONE

    def __init__(self) -> None:
        self.input_files = {}
        self.output_dir = OUTPUT_PATH

    def __setattr__(self, key: str, value: Any) -> None:
        expected_type = self.__annotations__.get(key)

        if expected_type is None:
            raise AttributeError

        super().__setattr__(key, expected_type(value))

    def load(self, path: str | Path) -> None:
        if not Path(path).is_file():
            return

        with open(path, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        if not isinstance(data, dict):
            raise Exception

        for key, value in data.items():
            expected_type = self.__annotations__.get(key)

            if expected_type is None:
                continue

            if key == "input_files":
                if not isinstance(value, list):
                    continue
                value = {p.name: p for p in (Path(v) for v in value)}

            elif issubclass(expected_type, Enum):
                try:
                    value = expected_type.__members__[value]
                except KeyError:
                    continue

            self.__setattr__(key, value)

    def save(self, path: str | Path) -> None:
        data = {**vars(self)}

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = [str(x) for x in value.values()]
            elif isinstance(value, Path):
                data[key] = str(value)
            elif isinstance(value, Enum):
                data[key] = value.name

        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)
