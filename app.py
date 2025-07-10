# nuitka-project: --onefile
# nuitka-project: --output-filename=WirthMage.exe
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --include-onefile-external-data=lib=lib
# nuitka-project: --include-package=customtkinter
# nuitka-project: --include-package=CTkListbox
# nuitka-project: --msvc=latest

import ast
import os
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import cast

import customtkinter as ctk

from common import (
    CONFIG_JSON,
    FILE_DIALOG_TITLE,
    FOLDER_FIALOG_TITLE,
    IMAGE_TYPES,
    WINDOW_TITLE,
    ImageSize,
    ImageType,
)
from converter import convert
from progress import ProgressModel, ProgressView
from ui_model import UIModel
from ui_view import UIView


class App:
    model: UIModel
    view: UIView

    input_dir = Path.home() / "Pictures"

    def __init__(self) -> None:
        ctk.set_default_color_theme("green")

        view = self.view = UIView()
        model = self.model = UIModel()

        view.title(WINDOW_TITLE)

        if CONFIG_JSON.is_file():
            model.load(CONFIG_JSON)
            self.get_input_files()

        if not model.output_dir.get().exists():
            model.output_dir.set(model.output_dir.default_value)

        view.input_files.configure(listvariable=model.input_files)
        view.output_dir.configure(textvariable=model.output_dir)

        view.image_size.configure(
            variable=model.image_size,
            command=self.image_size_changed,
        )
        self.image_size_changed(cast(ImageSize, model.image_size.get()))
        view.image_size_2x.configure(variable=model.image_size_2x)
        view.image_size_4x.configure(variable=model.image_size_4x)

        view.image_type.configure(
            variable=model.image_type,
            command=self.image_type_changed,
        )
        self.image_type_changed(cast(ImageType, model.image_type.get()))
        view.indexed_color.configure(variable=model.indexed_color)
        view.color_mask.configure(
            variable=model.color_mask,
            command=self.color_mask_changed,
        )
        view.outline_style.configure(variable=model.outline_style)

        view.input_files_add_button.configure(command=self.add_input_files)
        view.input_files_remove_button.configure(
            command=self.remove_input_files,
        )
        view.input_files_clear_button.configure(command=self.clear_input_files)

        view.output_dir_change_button.configure(command=self.change_output_dir)
        view.output_dir_show_button.configure(command=self.show_output_dir)

        view.execute_button.configure(command=self.execute)
        view.quit_button.configure(command=self.quit)
        view.protocol("WM_DELETE_WINDOW", self.quit)

    def get_input_files(self):
        data = ast.literal_eval(self.model.input_files.get())
        ast.literal_eval
        if not isinstance(data, dict):
            return dict()
        not_exists = [k for k, v in data.items() if not Path(v).exists()]
        if not_exists:
            for key in not_exists:
                del data[key]
            self.model.input_files.set(data)
        return data

    def add_input_files(self):
        paths = ctk.filedialog.askopenfilenames(
            title=FILE_DIALOG_TITLE,
            filetypes=IMAGE_TYPES,
            initialdir=self.input_dir,
        )
        if not paths:
            return
        data = self.get_input_files()
        for path in paths:
            path = Path(path)
            data[path.name] = str(path.absolute())
        self.input_dir = path.parent
        self.model.input_files.set(dict(sorted(data.items())))

    def remove_input_files(self):
        data = self.get_input_files()
        keys = tuple(data.keys())
        selection = self.view.input_files.curselection()
        if not selection and selection != 0:
            return
        if isinstance(selection, Iterable):
            for i in selection:
                del data[keys[i]]
        elif selection is not None:
            del data[selection]
        self.model.input_files.set(data)

    def clear_input_files(self):
        self.model.input_files.set({})

    def change_output_dir(self):
        selection = ctk.filedialog.askdirectory(
            title=FOLDER_FIALOG_TITLE,
            initialdir=self.model.output_dir.get(),
        )
        if selection:
            self.model.output_dir.set(selection)

    def show_output_dir(self):
        os.startfile(self.model.output_dir.get())

    def image_size_changed(self, value: ImageSize):
        state = ctk.NORMAL if value != ImageSize.ASIS else ctk.DISABLED

        for widget in (
            self.view.image_size_2x,
            self.view.image_size_4x,
        ):
            widget.configure(state=state)

    def image_type_changed(self, value: ImageType):
        state = ctk.NORMAL if value != ImageType.JPEG else ctk.DISABLED

        for widget in (
            self.view.indexed_color,
            self.view.color_mask,
            self.view.outline_style,
        ):
            widget.configure(state=state)

        if state == ctk.NORMAL:
            self.color_mask_changed()

    def color_mask_changed(self):
        state = ctk.NORMAL if self.model.color_mask.get() else ctk.DISABLED
        self.view.outline_style.configure(state=state)

    def execute(self):
        input_files = self.get_input_files()
        total_files = len(input_files)
        self.show_progress(total_files)

    def show_progress(self, total_files):
        progress_model = ProgressModel(total_files)
        progress_view = ProgressView(self.view, progress_model)
        threading.Thread(
            target=lambda: self.progress_worker(progress_view),
            daemon=True,
        ).start()

    def progress_worker(self, progress_view: ProgressView):
        params = {
            key: value.get()
            for key, value in self.model.__dict__.items()
            if key != "input_files"
        }
        input_files = self.get_input_files()

        for path in input_files.values():
            if progress_view.model.cancelled:
                break

            if (path := Path(path)).is_file():
                try:
                    convert(path, **params)
                except FileNotFoundError:
                    del input_files[path.name]
                    self.model.input_files.set(input_files)
                finally:
                    progress_view.advance()

    def quit(self):
        self.model.save(CONFIG_JSON)
        self.view.quit()

    def mainloop(self) -> None:
        self.watch_input_files()
        self.view.mainloop()

    def watch_input_files(self) -> None:
        input_files = self.get_input_files()
        deleted = False

        for path in input_files.values():
            path = Path(path)
            if not path.is_file():
                del input_files[path.name]
                deleted = True

        if deleted:
            self.model.input_files.set(input_files)

        self.view.after(100, self.watch_input_files)


if __name__ == "__main__":
    App().mainloop()
