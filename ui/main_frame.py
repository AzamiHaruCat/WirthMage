from __future__ import annotations


import wx

import constants as cs

from .constants import (
    BASE_FONT,
    BUTTON_SIZE,
    MONO_FONT,
    SIZE_UNIT,
)
from .controls import (
    Button,
    CheckBox,
    InlineLabel,
    Label,
    ListBox,
    Note,
    SwitchButtons,
)


class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(
            None,
            title=cs.WINDOW_TITLE,
            size=wx.Size(SIZE_UNIT * 40, SIZE_UNIT * 28),
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX,
        )

        self.SetIcon(wx.Icon(str(cs.ASSETS_PATH / "icon.ico")))
        self.SetFont(BASE_FONT)
        self.SetBackgroundColour(wx.Colour(0xF8, 0xF8, 0xF8))
        self.SetForegroundColour(wx.Colour(0x08, 0x08, 0x08))

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(self.GetBackgroundColour())
        self.panel.SetForegroundColour(self.GetForegroundColour())

        columns = wx.GridSizer(1, 2, 0, SIZE_UNIT)
        columns.Add(self._create_left_column(), 0, wx.EXPAND)
        columns.Add(self._create_right_column(), 0, wx.EXPAND)

        root_sizer = wx.BoxSizer()
        root_sizer.Add(columns, 1, wx.EXPAND | wx.ALL, SIZE_UNIT)

        self.panel.SetSizer(root_sizer)
        self.Layout()
        self.Center()

    def _create_left_column(self) -> wx.Sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.input_files = InputFilesBlock(self.panel)
        sizer.Add(self.input_files, 1, wx.EXPAND)

        return sizer

    def _create_right_column(self) -> wx.Sizer:
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.output_dir = OutputDirBlock(self.panel)
        sizer.Add(self.output_dir, 0, wx.EXPAND)

        self.output_size = OutputSizeBlock(self.panel)
        sizer.Add(self.output_size, 0, wx.EXPAND | wx.TOP, SIZE_UNIT // 2)

        self.output_format = OutputFormatBlock(self.panel)
        sizer.Add(self.output_format, 0, wx.EXPAND | wx.TOP, SIZE_UNIT // 2)

        sizer.AddStretchSpacer(1)

        for text in cs.NOTICE_MESSAGES:
            sizer.Add(Note(self.panel, text), 1, wx.EXPAND)

        self.execute_button = Button(
            self.panel,
            cs.EXECUTE_LABEL,
            size=wx.Size(*BUTTON_SIZE).Scale(1, 1.3),
            bg_colour=wx.Colour(0x20, 0x40, 0xF0),
            hover_colour=wx.Colour(0x40, 0x80, 0xF0),
        )

        self.quit_button = Button(
            self.panel,
            cs.QUIT_LABEL,
            size=wx.Size(*BUTTON_SIZE).Scale(1, 1.3),
            bg_colour=wx.Colour(0xF0, 0x40, 0x20),
            hover_colour=wx.Colour(0xF0, 0x80, 0x40),
        )
        buttons = wx.GridSizer(0, 2, 0, SIZE_UNIT // 2)
        buttons.Add(self.execute_button, 0, wx.EXPAND)
        buttons.Add(self.quit_button, 0, wx.EXPAND)
        sizer.Add(buttons, 0, wx.EXPAND | wx.TOP, SIZE_UNIT // 2)

        return sizer


class BlockSizer(wx.BoxSizer):
    controls: tuple[wx.Control, ...]

    def __init__(self, parent: wx.Window, label: str) -> None:
        super().__init__(wx.VERTICAL)
        self.label = Label(parent, label)
        self.Add(self.label, 0, wx.EXPAND)

    def Refresh(self):
        for control in self.controls:
            control.Refresh()


class InputFilesBlock(BlockSizer):
    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, cs.INPUT_FILES_LABEL)

        self.listbox = ListBox(parent, style=wx.LB_MULTIPLE)
        self.listbox.SetFont(MONO_FONT)
        self.Add(self.listbox, 1, wx.EXPAND)

        buttons = [
            self.add_button,
            self.remove_button,
            self.clear_button,
        ] = [
            Button(parent, label=label)
            for label in (cs.ADD_LABEL, cs.REMOVE_LABEL, cs.CLEAR_LABEL)
        ]
        buttons_sizer = wx.GridSizer(1, 0, 0, SIZE_UNIT // 2)
        for button in buttons:
            buttons_sizer.Add(button, flag=wx.EXPAND)
        self.Add(buttons_sizer, 0, wx.EXPAND | wx.TOP, SIZE_UNIT // 2)

        self.controls = (self.listbox, *buttons)


class OutputDirBlock(BlockSizer):
    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, cs.OUTPUT_DIR_LABEL)

        sizer = wx.FlexGridSizer(1, 0, 0, SIZE_UNIT // 8)
        sizer.AddGrowableCol(0)

        mid_sizer = wx.BoxSizer(wx.VERTICAL)
        mid_panel = wx.Panel(parent, style=wx.BORDER_THEME)
        mid_panel.SetBackgroundColour(wx.WHITE)
        mid_panel.SetSizer(mid_sizer)

        self.text = InlineLabel(
            mid_panel,
            label=str(cs.OUTPUT_PATH),
            style=wx.ST_ELLIPSIZE_START,
            size=wx.Size(1, -1),
        )
        self.text.SetFont(MONO_FONT)

        mid_sizer.AddStretchSpacer()
        mid_sizer.Add(self.text, 0, wx.EXPAND)
        mid_sizer.AddStretchSpacer()
        sizer.Add(mid_panel, 0, wx.EXPAND)

        buttons = [
            self.change_button,
            self.open_button,
        ] = [
            Button(
                parent,
                label=label,
                size=wx.Size(int(SIZE_UNIT * 2.5), BUTTON_SIZE.Height),
            )
            for label in (cs.CHANGE_LABEL, cs.OPEN_LABEL)
        ]
        for button in buttons:
            sizer.Add(button, 0, wx.EXPAND)

        self.Add(sizer, 0, wx.EXPAND)

        self.controls = (*buttons,)


class OutputSizeBlock(BlockSizer):
    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, cs.OUTPUT_SIZE_LABEL)

        self.switch = SwitchButtons(
            parent, cs.ImageSize, rows=1, hgap=SIZE_UNIT // 8
        )
        self.Add(self.switch, 0, wx.EXPAND)

        self.x2_checkbox = CheckBox(parent, cs.OUTPUT_X2_LABEL)
        self.Add(self.x2_checkbox, 0, wx.TOP, SIZE_UNIT // 5)

        self.x4_checkbox = CheckBox(parent, cs.OUTPUT_X4_LABEL)
        self.Add(self.x4_checkbox, 0, wx.TOP, SIZE_UNIT // 5)

        self.controls = (
            self.switch,
            self.x2_checkbox,
            self.x4_checkbox,
        )


class OutputFormatBlock(BlockSizer):
    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, cs.OUTPUT_FORMAT_LABEL)

        self.switch = SwitchButtons(
            parent, cs.ImageType, rows=1, hgap=SIZE_UNIT // 8
        )
        self.Add(self.switch, 0, wx.EXPAND)

        self.color_mask_checkbox = CheckBox(parent, cs.COLOR_MASK_LABEL)
        self.Add(self.color_mask_checkbox, 0, wx.TOP, SIZE_UNIT // 5)

        self.indexed_color_choice = wx.Choice(
            parent, choices=list[str](cs.IndexedColor)
        )
        self.outline_style_choice = wx.Choice(
            parent, choices=list[str](cs.OutlineStyle)
        )

        for label, control in (
            (cs.INDEXED_COLOR_LABEL, self.indexed_color_choice),
            (cs.OUTLINE_STYLE_LABEL, self.outline_style_choice),
        ):
            sizer = wx.BoxSizer()
            control.SetSelection(0)

            for control in (
                InlineLabel(parent, label, size=wx.Size(SIZE_UNIT * 3, -1)),
                control,
            ):
                sizer.Add(control, 0, wx.ALIGN_CENTER_VERTICAL)

            self.Add(sizer, 0, wx.TOP, SIZE_UNIT // 4)

        self.controls = (
            self.switch,
            self.color_mask_checkbox,
            self.indexed_color_choice,
            self.outline_style_choice,
        )
