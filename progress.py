from customtkinter import CTkButton, CTkLabel, CTkProgressBar, CTkToplevel

from constants import CANCEL_LABEL, PROGRESS_LABEL, PROGRESS_TITLE
from ui_view import UIView


class ProgressModel:
    def __init__(self, total_steps: int) -> None:
        self.total = total_steps
        self.current = 0
        self.cancelled = False

    @property
    def completed(self) -> bool:
        return self.current >= self.total

    @property
    def progress_ratio(self) -> float:
        return self.current / self.total

    def advance(self) -> None:
        self.current += 1

    def cancel(self) -> None:
        self.cancelled = True


class ProgressView(CTkToplevel):
    master: UIView

    def __init__(
        self,
        master: UIView,
        model: ProgressModel,
        window_title: str = PROGRESS_TITLE,
        label_template: str = PROGRESS_LABEL,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(master, *args, **kwargs)
        self.master.attributes("-disabled", True)
        self.model = model
        self.template = label_template
        self.title(window_title)
        size_unit = master.font.actual("size")
        self.label = CTkLabel(self, text="", font=master.font)
        self.bar = CTkProgressBar(self)
        self.label.pack(pady=(size_unit // 2, 0))
        self.bar.pack(padx=size_unit // 2, pady=size_unit // 2)
        self.cancel_button = CTkButton(
            self,
            text=CANCEL_LABEL,
            font=master.font,
            command=self.cancel,
        )
        self.cancel_button.pack(pady=size_unit // 2)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.center_geometry(size_unit * 20, size_unit * 7)
        self.tick()

    def advance(self) -> None:
        self.model.advance()
        self.tick()

    def cancel(self) -> None:
        self.model.cancel()
        self.attributes("-disabled", True)

    def tick(self) -> None:
        self.bar.set(self.model.progress_ratio)
        self.label.configure(
            text=self.template.format(
                current=self.model.current,
                total=self.model.total,
            )
        )
        if self.model.completed or self.model.cancelled:
            self.destroy()

    def destroy(self):
        self.master.attributes("-disabled", False)
        self.master.focus_set()
        self.withdraw()
        self.after(100, super().destroy)

    def center_geometry(self, width: int, height: int):
        master = self.master
        shift_x = master.winfo_rootx() - master.winfo_x()
        shift_y = master.winfo_rooty() - master.winfo_y()
        x = master.winfo_x() + (master.winfo_width() - width) // 2 - shift_x
        y = master.winfo_y() + (master.winfo_height() - height) // 2 - shift_y
        self.geometry(f"{width}x{height}+{x}+{y}")
