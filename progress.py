from customtkinter import (
    CENTER,
    CTkButton,
    CTkFrame,
    CTkLabel,
    CTkProgressBar,
)

from constants import CANCEL_LABEL, PROGRESS_LABEL
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
        return self.current / self.total if self.total else 1

    def advance(self) -> None:
        self.current += 1

    def cancel(self) -> None:
        self.cancelled = True


class ProgressView(CTkFrame):
    master: UIView

    def __init__(
        self,
        master: UIView,
        model: ProgressModel,
        label_template: str = PROGRESS_LABEL,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(master, fg_color="transparent", *args, **kwargs)
        self.model = model
        self.template = label_template

        self.label = CTkLabel(self, font=master.font)
        self.label.place(anchor=CENTER, relx=0.5, rely=0.4)

        self.bar = CTkProgressBar(self)
        self.bar.place(anchor=CENTER, relx=0.5, rely=0.5, relwidth=0.5)

        self.cancel_button = CTkButton(
            self,
            text=CANCEL_LABEL,
            font=master.font,
            command=self.cancel,
        )
        self.cancel_button.place(anchor=CENTER, relx=0.5, rely=0.6)

        self.tick()
        self.place(
            anchor="center",
            relx=0.5,
            rely=0.5,
            relwidth=1.0,
            relheight=1.0,
        )

    def advance(self) -> None:
        self.model.advance()
        self.tick()

    def cancel(self) -> None:
        self.model.cancel()

    def tick(self) -> None:
        self.bar.set(self.model.progress_ratio)
        self.label.configure(
            text=self.template.format(
                current=self.model.current,
                total=self.model.total,
            )
        )
        if self.model.completed or self.model.cancelled:
            try:
                self.place_forget()
            finally:
                self.after_idle(self.destroy)
