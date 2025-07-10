import json
import tkinter as tk
from enum import StrEnum
from pathlib import Path
from typing import Any

from constants import (
    OUTPUT_PATH,
    ImageSize,
    ImageType,
    IndexedColor,
    OutlineStyle,
)


class PathVar(tk.Variable):
    default_value: Path = OUTPUT_PATH

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.set(self.default_value)

    def get(self) -> Path:
        path = Path(super().get())
        return path if path.is_absolute() else Path.home() / path

    def set(self, value: str | Path) -> None:
        path = Path(value)
        if not path.exists():
            path = self.default_value
        if path.is_relative_to(Path.home()):
            path = path.relative_to(Path.home())
        return super().set(path)


class StrEnumVar(tk.Variable):
    enum: type[StrEnum]

    def __init__(self, *args, **kwargs) -> None:
        value = next(iter(self.enum.__members__.values()))
        super().__init__(value=value, *args, **kwargs)

    def get(self):
        return self.enum(super().get())

    def set(self, value: Any) -> None:
        return super().set(self.enum(value))


(
    ImageSizeVar,
    ImageTypeVar,
    IndexedColorVar,
    OutlineStyleVar,
) = (
    type(f"{enum.__name__}Var", (StrEnumVar,), {"enum": enum})
    for enum in (
        ImageSize,
        ImageType,
        IndexedColor,
        OutlineStyle,
    )
)


class UIModel:
    def __init__(self) -> None:
        self.input_files = tk.Variable(value={})
        self.output_dir = PathVar()
        self.image_size = ImageSizeVar()
        self.image_size_2x = tk.BooleanVar()
        self.image_size_4x = tk.BooleanVar()
        self.image_type = ImageTypeVar()
        self.indexed_color = IndexedColorVar()
        self.color_mask = tk.BooleanVar()
        self.outline_style = OutlineStyleVar()

    def __setattr__(self, key: str, value: Any) -> None:
        if isinstance(value, tk.Variable):
            object.__setattr__(self, key, value)
        else:
            prop = object.__getattribute__(self, key)
            if isinstance(prop, StrEnumVar):
                value = prop.enum(value)
            prop.set(value)

    def load(self, path: str | Path) -> None:
        try:
            with open(path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except IOError:
            return

        if not isinstance(data, dict):
            raise TypeError

        for key, value in data.items():
            prop = getattr(self, key)
            prop.set(
                prop.enum.__members__[value]
                if isinstance(prop, StrEnumVar)
                else value
            )

    def save(self, path: str | Path) -> None:
        data = {
            key: (
                str(prop.get())
                if isinstance(prop, PathVar)
                else (
                    prop.get().name
                    if isinstance(prop, StrEnumVar)
                    else prop.get()
                )
            )
            for key, prop in vars(self).items()
        }

        with open(path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)
