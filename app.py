# nuitka-project: --onefile
# nuitka-project: --output-filename=WirthMage.exe
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --windows-icon-from-ico=assets/icon.ico
# nuitka-project: --include-data-dir=assets=assets
# nuitka-project: --include-raw-dir=lib=lib
# nuitka-project: --follow-imports
# nuitka-project: --msvc=latest
# nuitka-project: --product-name=WirthMage
# nuitka-project: --file-description=CardWirth用画像コンバータ
# nuitka-project: --file-version=0.0.2
# nuitka-project: --copyright=(C) 2025 AzamiHaruCat https://github.com/AzamiHaruCat/WirthMage

from __future__ import annotations

import os
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import List

import wx

import constants as cs
from converter import convert
from converter_params import ConverterParams


class App(wx.App):
    input_dir = cs.INPUT_PATH

    def __init__(self) -> None:
        super().__init__(False)

        import ui  # The wx.App object must be created first!

        view = self.view = ui.MainFrame()
        model = self.model = ConverterParams()

        if cs.CONFIG_JSON.is_file():
            model.load(cs.CONFIG_JSON)

        view.panel.SetDropTarget(self.FileDropTarget(self))

        block = view.input_files
        block.listbox.SetItems(sorted(model.input_files.keys()))
        block.add_button.Bind(ui.EVT_CLICKED, self.add_input_files)
        block.remove_button.Bind(ui.EVT_CLICKED, self.remove_input_files)
        block.clear_button.Bind(ui.EVT_CLICKED, self.clear_input_files)

        block = view.output_dir
        block.text.SetLabel(str(model.output_dir))
        block.change_button.Bind(ui.EVT_CLICKED, self.change_output_dir)
        block.open_button.Bind(ui.EVT_CLICKED, self.show_output_dir)

        block = view.output_size
        block.switch.SetValue(model.image_size)
        block.x2_checkbox.SetValue(model.output_x2)
        block.x4_checkbox.SetValue(model.output_x4)
        for control in block.controls:
            control.Bind(ui.EVT_CLICKED, self.on_change_output_size)
        self.on_change_output_size()

        block = view.output_format
        block.switch.SetValue(model.image_type)
        block.color_mask_checkbox.SetValue(model.color_mask)
        block.indexed_color_choice.SetSelection(
            tuple(cs.IndexedColor).index(model.indexed_color)
        )
        block.outline_style_choice.SetSelection(
            tuple(cs.OutlineStyle).index(model.outline_style)
        )
        for control in block.controls:
            control.Bind(ui.EVT_CLICKED, self.on_change_output_format)
        self.on_change_output_format()

        self.view.execute_button.Bind(ui.EVT_CLICKED, self.execute)
        self.view.quit_button.Bind(ui.EVT_CLICKED, self.quit)
        self.view.Bind(wx.EVT_CLOSE, self.quit)

        self.view.Bind(wx.EVT_ACTIVATE, self.refresh)

    def refresh(self, *_) -> None:
        for control in (
            *self.view.input_files.controls,
            *self.view.output_dir.controls,
            *self.view.output_size.controls,
            *self.view.output_format.controls,
            self.view.execute_button,
            self.view.quit_button,
        ):
            control.Refresh()

    def on_change_output_size(self, *_) -> None:
        block = self.view.output_size
        self.model.image_size = cs.ImageSize(block.switch.GetValue())
        self.model.output_x2 = block.x2_checkbox.GetValue()
        self.model.output_x4 = block.x4_checkbox.GetValue()
        flag = block.switch.GetSelection() != 0
        block.x2_checkbox.Enable(flag)
        block.x4_checkbox.Enable(flag)
        self.refresh()

    def on_change_output_format(self, *_) -> None:
        block = self.view.output_format
        self.model.image_type = cs.ImageType(block.switch.GetValue())
        self.model.color_mask = block.color_mask_checkbox.GetValue()
        self.model.indexed_color = tuple(cs.IndexedColor)[
            block.indexed_color_choice.GetSelection()
        ]
        self.model.outline_style = tuple(cs.OutlineStyle)[
            block.outline_style_choice.GetSelection()
        ]
        flag = self.model.image_type != cs.ImageType.JPEG
        block.color_mask_checkbox.Enable(flag)
        block.indexed_color_choice.Enable(flag)
        flag = flag and self.model.color_mask
        block.outline_style_choice.Enable(flag)
        self.refresh()

    def add_input_files(self, *_) -> None:
        with wx.FileDialog(
            self.view,
            message=cs.FILE_DIALOG_TITLE,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST,
            wildcard="|".join("|".join(x) for x in cs.IMAGE_TYPES),
            defaultDir=str(self.input_dir),
        ) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                paths = dialog.GetPaths()
                self._add_input_files(paths)
        self.refresh()

    def _add_input_files(self, paths: Iterable[str | Path]) -> None:
        data = self.model.input_files
        listbox = self.view.input_files.listbox
        for path in paths:
            path = Path(path).absolute()
            data[path.name] = path
        listbox.SetItems(sorted(data.keys()))
        self.input_dir = path.parent
        self.refresh()

    def remove_input_files(self, *_) -> None:
        data = self.model.input_files
        listbox = self.view.input_files.listbox
        for i, item in enumerate(listbox.GetItems()):
            if listbox.IsSelected(i):
                del data[item]
        listbox.SetItems(sorted(data.keys()))
        self.refresh()

    def clear_input_files(self, *_) -> None:
        self.model.input_files = {}
        self.view.input_files.listbox.SetItems(())
        self.refresh()

    def change_output_dir(self, *_) -> None:
        with wx.DirDialog(
            self.view,
            message=cs.FOLDER_DIALOG_TITLE,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
            defaultPath=str(self.model.output_dir),
        ) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                self.model.output_dir = path
                self.view.output_dir.text.SetLabel(path)
        self.refresh()

    def show_output_dir(self, *_) -> None:
        os.startfile(self.model.output_dir)
        self.refresh()

    def execute(self, *_) -> None:
        self.model.save(cs.CONFIG_JSON)
        if total_files := len(self.model.input_files):
            self.show_progress(total_files)

    def show_progress(self, total_files: int) -> None:
        import ui

        progress_model = ui.ProgressModel(total_files)
        progress_view = ui.ProgressDialog(self.view, progress_model)

        def worker() -> None:
            listbox = self.view.input_files.listbox
            data = self.model.input_files
            paths = tuple(data.values())
            params = {**vars(self.model)}
            del params["input_files"]

            for path in paths:
                if progress_view.model.is_cancelled:
                    break

                if (path := Path(path)).is_file():
                    try:
                        convert(path, **params)
                    except FileNotFoundError:
                        del data[path.name]
                        wx.CallAfter(listbox.SetItems, sorted(data.keys()))
                    finally:
                        wx.CallAfter(progress_view.advance)

            wx.CallAfter(self.refresh)

        threading.Thread(target=worker, daemon=True).start()
        progress_view.ShowModal()

    def quit(self, *_) -> None:
        self.model.save(cs.CONFIG_JSON)
        self.view.Destroy()

    def Mainloop(self) -> None:
        self.watch_input_files()
        self.view.Show()
        super().MainLoop()

    def watch_input_files(self) -> None:
        data = self.model.input_files
        deleted = False

        for key, path in data.items():
            if not path.is_file():
                del data[key]
                deleted = True

        if deleted:
            self.view.input_files.listbox.SetItems(sorted(data.keys()))

        wx.CallLater(100, self.watch_input_files)

    class FileDropTarget(wx.FileDropTarget):

        def __init__(self, app: App) -> None:
            super().__init__()
            self.app = app

        def OnDropFiles(self, x: int, y: int, filenames: List[str]) -> bool:
            filenames = [
                filename
                for filename in filenames
                if Path(filename).suffix.lower()
                in (".bmp", ".png", ".jpg", ".jpeg", ".gif")
            ]
            if filenames:
                self.app._add_input_files(filenames)
                return True
            else:
                return False


if __name__ == "__main__":
    App().Mainloop()
