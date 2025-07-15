import wx

import constants as cs

from .constants import BUTTON_SIZE, SIZE_UNIT
from .controls import EVT_CLICKED, Button


class ProgressModel:

    def __init__(self, total_steps: int) -> None:
        self.total = total_steps
        self.current = 0
        self.is_cancelled = False

    @property
    def is_completed(self) -> bool:
        return self.current >= self.total

    @property
    def progress_ratio(self) -> float:
        return self.current / self.total if self.total else 1

    def advance(self) -> None:
        self.current += 1

    def cancel(self) -> None:
        self.is_cancelled = True


class ProgressView(wx.Panel):

    def __init__(
        self,
        parent: wx.Window,
        model: ProgressModel,
        label_template: str = cs.PROGRESS_LABEL,
    ) -> None:

        super().__init__(parent)

        self.model = model
        self.template = label_template

        main_frame = parent.GetTopLevelParent().GetParent()
        self.SetFont(main_frame.GetFont())
        self.SetBackgroundColour(main_frame.GetBackgroundColour())
        self.SetForegroundColour(main_frame.GetForegroundColour())

        self.label = wx.StaticText(self, style=wx.ALIGN_CENTER_HORIZONTAL)
        self.bar = wx.Gauge(
            self,
            range=100,
            style=wx.GA_HORIZONTAL,
            size=wx.Size(int(parent.GetSize().Width * 0.8), SIZE_UNIT),
        )
        self.cancel_button = Button(
            self,
            label=cs.CANCEL_LABEL,
            size=wx.Size(*BUTTON_SIZE).Scale(1, 1.3),
        )
        self.cancel_button.Bind(EVT_CLICKED, self._on_cancel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        sizer.Add(self.label, 1, wx.ALIGN_CENTER | wx.ALL, SIZE_UNIT // 2)
        sizer.Add(self.bar, 1, wx.ALIGN_CENTER | wx.ALL, SIZE_UNIT // 2)
        sizer.Add(
            self.cancel_button, 1, wx.ALIGN_CENTER | wx.ALL, SIZE_UNIT // 2
        )
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

        self.tick()

    def _on_cancel(self, event: wx.CommandEvent) -> None:
        self.cancel()

    def advance(self) -> None:
        self.model.advance()
        self.tick()

    def cancel(self) -> None:
        self.model.cancel()
        self._check_cleanup()

    def tick(self) -> None:
        ratio = self.model.progress_ratio
        label = self.template.format(
            current=self.model.current,
            total=self.model.total,
        )
        self.bar.SetValue(int(ratio * 100))
        self.label.SetLabel(label)
        self._check_cleanup()

    def _check_cleanup(self) -> None:
        if self.model.is_completed or self.model.is_cancelled:
            self.Hide()
            wx.CallAfter(self.Destroy)


class ProgressDialog(wx.Dialog):

    def __init__(
        self,
        parent: wx.Window,
        model: ProgressModel,
        title: str = cs.PROGRESS_TITLE,
        label_template: str = cs.PROGRESS_LABEL,
    ) -> None:

        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSize(wx.Size(SIZE_UNIT * 24, SIZE_UNIT * 12))

        self.view = ProgressView(self, model, label_template)
        sizer = wx.BoxSizer()
        sizer.Add(self.view, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        self.CenterOnParent()

        self._monitor_progress()

    @property
    def model(self) -> ProgressModel:
        return self.view.model

    def advance(self) -> None:
        return self.view.advance()

    def cancel(self) -> None:
        return self.view.cancel()

    def _monitor_progress(self) -> None:
        def check():
            if self.view.model.is_completed or self.view.model.is_cancelled:
                self.EndModal(wx.ID_OK)
            else:
                self.view.tick()
                wx.CallLater(100, check)

        wx.CallLater(100, check)
