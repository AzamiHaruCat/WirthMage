import inspect
from typing import Type, TypeVar

from CTkListbox import CTkListbox as _CTkListbox
from customtkinter import (
    CTk,
    CTkButton,
    CTkCheckBox,
    CTkEntry,
    CTkFont,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkRadioButton,
    CTkSegmentedButton,
    Variable,
)
from tkinterdnd2 import DND_FILES, TkinterDnD

from constants import (
    ADD_LABEL,
    ASSETS_PATH,
    CHANGE_LABEL,
    CLEAR_LABEL,
    COLOR_MASK_LABEL,
    EXECUTE_LABEL,
    INDEXED_COLOR_LABEL,
    NOTICE_MESSAGES,
    OPEN_LABEL,
    OUTLINE_STYLE_LABEL,
    OUTPUT_2X_LABEL,
    OUTPUT_4X_LABEL,
    OUTPUT_FORMAT_LABEL,
    OUTPUT_SIZE_LABEL,
    QUIT_LABEL,
    REMOVE_LABEL,
    ImageSize,
    ImageType,
    IndexedColor,
    OutlineStyle,
)


class CTkListbox(_CTkListbox):  # 暫定的な修正
    def configure(self, listvariable: Variable | None = None, **kwargs):
        if listvariable and not hasattr(self, "listvariable"):
            self.listvariable = listvariable
            self.listvariable.trace_add(
                "write", lambda a, b, c: self.update_listvar()
            )
            self.update_listvar()
        return super().configure(**kwargs)


T = TypeVar(
    "T",
    CTkButton,
    CTkCheckBox,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkRadioButton,
    CTkSegmentedButton,
    CTkListbox,
)


class UIView(CTk, TkinterDnD.Tk):
    def __init__(self) -> None:
        CTk.__init__(self)
        TkinterDnD.Tk.__init__(self)
        self.drop_target_register(DND_FILES)

        # アイコン
        icon_path = ASSETS_PATH / "icon.ico"
        self.iconbitmap(icon_path)
        self.iconbitmap(default=icon_path)

        # フォント
        s_width = self.winfo_screenwidth()
        s_height = self.winfo_screenheight()
        font_family = "BIZ UDPGothic"
        font_size = int(min(s_width, s_height) * 0.02)
        self.font = CTkFont(font_family, font_size)
        self.bold_font = CTkFont(font_family, font_size, "bold")
        self.small_font = CTkFont(font_family, font_size * 80 // 100)

        # 画面サイズ
        w_width = font_size * 40
        w_height = font_size * 28
        self.center_geometry(w_width, w_height)
        self.configure(padx=font_size // 2, pady=font_size // 2)

        # ルートフレーム
        root_frame = CTkFrame(self, fg_color="transparent")
        root_frame.place(
            anchor="center",
            relx=0.5,
            rely=0.5,
            relwidth=1.0,
            relheight=1.0,
        )

        # 左右フレーム
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        left_frame, right_frame = (
            self.create_widget(
                CTkFrame,
                column=column,
                row=0,
                padx=font_size // 2,
                pady=font_size // 2,
            )
            for column in range(2)
        )
        left_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 入力ファイル
        self.create_widget(
            CTkLabel,
            master=left_frame,
            text="入力ファイル",
        )
        block = self.create_widget(
            CTkListbox,
            master=left_frame,
            multiple_selection=True,
            listvariable=None,
        )
        left_frame.grid_rowconfigure(block.grid_info()["row"], weight=1)
        self.input_files = block
        block = self.create_widget(CTkFrame, master=left_frame)
        block.grid_columnconfigure(tuple(range(3)), weight=1)
        (
            self.input_files_add_button,
            self.input_files_remove_button,
            self.input_files_clear_button,
        ) = (
            self.create_widget(
                CTkButton,
                master=block,
                text=text,
                column=column,
                row=0,
                width=font_size * 3,
                padx=font_size // 10,
                pady=(font_size // 2, 0),
            )
            for column, text in enumerate(
                (ADD_LABEL, REMOVE_LABEL, CLEAR_LABEL),
            )
        )

        # 出力フォルダ
        self.create_widget(CTkLabel, master=right_frame, text="出力フォルダ")
        block = self.create_widget(
            CTkFrame, master=right_frame, pady=(0, font_size // 2)
        )
        block.grid_columnconfigure(0, weight=1)
        self.output_dir = self.create_widget(
            CTkEntry,
            master=block,
            font=self.small_font,
            state="readonly",
            width=0,
            column=0,
            row=0,
            padx=0,
        )
        (
            self.output_dir_change_button,
            self.output_dir_show_button,
        ) = (
            self.create_widget(
                CTkButton,
                master=block,
                text=text,
                width=font_size * 3,
                column=column,
                row=0,
                padx=(font_size // 5, 0),
            )
            for column, text in enumerate((CHANGE_LABEL, OPEN_LABEL), 1)
        )

        # 出力サイズ
        self.create_widget(
            CTkLabel,
            master=right_frame,
            pady=(font_size // 2, 0),
            text=OUTPUT_SIZE_LABEL,
        )
        self.image_size = self.create_widget(
            CTkSegmentedButton,
            master=right_frame,
            values=tuple(ImageSize.__members__.values()),
            pady=(0, font_size // 2),
        )
        self.image_size_2x = self.create_widget(
            CTkCheckBox,
            master=right_frame,
            text=OUTPUT_2X_LABEL,
            pady=(0, font_size // 2),
        )
        self.image_size_4x = self.create_widget(
            CTkCheckBox,
            master=right_frame,
            text=OUTPUT_4X_LABEL,
            pady=(0, font_size // 2),
        )

        # 出力形式
        self.create_widget(
            CTkLabel,
            master=right_frame,
            pady=(font_size // 2, 0),
            text=OUTPUT_FORMAT_LABEL,
        )
        self.image_type = self.create_widget(
            CTkSegmentedButton,
            master=right_frame,
            values=tuple(ImageType.__members__.values()),
            pady=(0, font_size // 2),
        )
        block = self.create_widget(
            CTkFrame,
            master=right_frame,
            pady=(0, font_size // 2),
        )
        self.create_widget(
            CTkLabel,
            master=block,
            text=INDEXED_COLOR_LABEL,
            font=self.font,
            text_color=None,
            padx=(0, font_size // 4),
        )
        self.indexed_color = self.create_widget(
            CTkOptionMenu,
            master=block,
            values=tuple(IndexedColor.__members__.values()),
            width=font_size * 6,
            column=1,
            row=0,
        )
        self.color_mask = self.create_widget(
            CTkCheckBox,
            master=right_frame,
            text=COLOR_MASK_LABEL,
            pady=(0, font_size // 2),
        )
        block = self.create_widget(
            CTkFrame,
            master=right_frame,
            pady=(0, font_size // 2),
        )
        self.create_widget(
            CTkLabel,
            master=block,
            text=OUTLINE_STYLE_LABEL,
            font=self.font,
            text_color=None,
            padx=(0, font_size // 4),
        )
        self.outline_style = self.create_widget(
            CTkOptionMenu,
            master=block,
            values=tuple(OutlineStyle.__members__.values()),
            width=font_size * 6,
            column=1,
            row=0,
        )

        # スペース調整
        block = self.create_widget(CTkFrame, master=right_frame)
        right_frame.grid_rowconfigure(block.grid_info()["row"], weight=1)

        # 注意事項
        block = self.create_widget(
            CTkFrame,
            master=right_frame,
            pady=(0, font_size // 2),
        )
        for text in NOTICE_MESSAGES:
            self.create_widget(
                CTkLabel,
                master=block,
                font=self.small_font,
                text=text,
                text_color=None,
            )

        # 実行・終了ボタン
        block = self.create_widget(CTkFrame, master=right_frame)
        block.grid_columnconfigure(tuple(range(2)), weight=1)
        block.grid_rowconfigure(0, minsize=font_size * 2)
        self.execute_button = self.create_widget(
            CTkButton,
            master=block,
            text=EXECUTE_LABEL,
            fg_color="royalblue",
            hover_color="cornflowerblue",
            padx=(0, font_size // 5),
        )
        self.quit_button = self.create_widget(
            CTkButton,
            master=block,
            text=QUIT_LABEL,
            fg_color="tomato",
            hover_color="lightsalmon",
            column=1,
            row=0,
            padx=(font_size // 5, 0),
        )

    def center_geometry(self, width: int, height: int):
        self.geometry(f"{width}x{height}")
        self.update()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        shift_x = self.winfo_rootx() - self.winfo_x()
        shift_y = self.winfo_rooty() - self.winfo_y()
        x = (screen_width - width) // 2 - shift_x
        y = (screen_height - height) // 2 - shift_y
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widget(self, cls: Type[T], **kwargs) -> T:
        keys = set(inspect.signature(cls.__init__).parameters.keys())
        params1, params2 = (
            {k: v for k, v in kwargs.items() if k in keys},
            {k: v for k, v in kwargs.items() if k not in keys},
        )
        size_unit = self.font.actual("size")

        if "font" in keys and "font" not in params1:
            params1["font"] = self.bold_font if cls is CTkLabel else self.font

        if cls is CTkFrame:
            params1 = {"fg_color": "transparent", **params1}
        elif cls is CTkLabel:
            params1 = {"anchor": "w", "text_color": "#408060", **params1}
        elif cls in (CTkButton, CTkSegmentedButton):
            params2 = {"ipady": size_unit // 5, **params2}

        widget = cls(
            **{
                "master": self,
                "width": size_unit * 3,
                **params1,
            }
        )
        widget.grid(
            **{
                "padx": 0,
                "pady": 0,
                "sticky": "nswe",
                **params2,
            }
        )
        return widget
