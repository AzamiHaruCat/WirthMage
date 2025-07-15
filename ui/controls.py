from __future__ import annotations

from typing import Iterable

import wx
import wx.lib.newevent

from .constants import (
    ACTIVE_COLOUR,
    BG_COLOUR,
    BUTTON_SIZE,
    HOVER_COLOUR,
    SIZE_UNIT,
    TOGGLE_COLOUR,
)

ClickEvent, EVT_CLICKED = wx.lib.newevent.NewCommandEvent()


class Label(wx.StaticText):

    def __init__(
        self,
        parent: wx.Window,
        label: str = "",
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, label=label, *args, **kwargs)
        font = wx.Font(parent.GetFont())
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.SetFont(font)
        self.SetForegroundColour(wx.Colour(0x40, 0x80, 0x60))
        self.Wrap(-1)


class InlineLabel(wx.StaticText):

    def __init__(
        self,
        parent: wx.Window,
        label: str = "",
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, label=label, *args, **kwargs)
        self.Wrap(-1)


class Note(wx.StaticText):

    def __init__(
        self,
        parent: wx.Window,
        label: str = "",
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, label=label, *args, **kwargs)
        font = wx.Font(parent.GetFont())
        font.SetPixelSize(font.GetPixelSize().Scale(0.85, 0.85))
        self.SetFont(font)
        self.Wrap(0)


class Button(wx.Control):
    is_active = False
    is_pressed = False

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        size: wx.Size = BUTTON_SIZE,
        style: int = wx.BORDER_NONE,
        radius: float = SIZE_UNIT / 4,
        bg_colour: wx.Colour = BG_COLOUR,
        hover_colour: wx.Colour = HOVER_COLOUR,
        active_colour: wx.Colour = ACTIVE_COLOUR,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, size=size, style=style, *args, **kwargs)

        self.label = label
        self.radius = radius
        self.bg_colour = bg_colour
        self.hover_colour = hover_colour
        self.active_colour = active_colour

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour(bg_colour)
        self.SetForegroundColour(wx.WHITE)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_press)
        self.Bind(wx.EVT_LEFT_UP, self._on_release)

        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def Enable(self, enable: bool = True) -> bool:
        value = super().Enable(enable)
        self.Refresh()
        return value

    def Disable(self) -> bool:
        value = super().Disable()
        self.Refresh()
        return value

    def _on_paint(self, event: wx.PaintEvent) -> None:
        self._update_colour()

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        w, h = self.GetSize()

        self._draw_content(dc, gc, w, h)

        if not self.IsEnabled():
            colour = self.GetParent().GetBackgroundColour()
            colour = wx.Colour(*colour.Get(False), alpha=192)
            gc.SetBrush(wx.Brush(colour))
            gc.SetPen(wx.TRANSPARENT_PEN)
            gc.DrawRectangle(0, 0, w, h)

        event.Skip()

    def _update_colour(self) -> None:
        mouse_screen = wx.GetMousePosition()
        mouse_local = self.ScreenToClient(mouse_screen)

        if self.GetClientRect().Contains(mouse_local):
            if self.is_pressed:
                self.SetBackgroundColour(self.active_colour)
            else:
                self.SetBackgroundColour(self.hover_colour)
        else:
            self.SetBackgroundColour(self.bg_colour)

    def _draw_content(
        self,
        dc: wx.BufferedPaintDC,
        gc: wx.GraphicsContext,
        w: int,
        h: int,
    ) -> None:

        r = self.radius

        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        gc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRoundedRectangle(0, 0, w, h, r)

        while True:
            tw, th = dc.GetTextExtent(self.label)

            if tw < w:
                break

            font = self.GetFont()
            fw, fh = font.GetPixelSize()
            fw = (fh if fw <= 0 else fw) - 1
            font = wx.Font(
                wx.Size(fw, fh),
                font.GetFamily(),
                font.GetStyle(),
                font.GetWeight(),
                font.GetUnderlined(),
                font.GetFaceName(),
                font.GetEncoding(),
            )
            self.SetFont(font)
            dc.SetFont(font)

        dc.DrawText(self.label, (w - tw) // 2, (h - th) // 2)

    def _on_enter(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            if self.is_pressed and event.leftIsDown:
                self._on_press(event)
            else:
                self.is_pressed = False
                self.Refresh()

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.Refresh()

    def _on_press(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.is_pressed = True
            self.Refresh()

    def _on_release(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.is_pressed = False
            self._on_enter(event)
            self._fire_click_event()

    def _fire_click_event(self) -> None:
        evt = ClickEvent(self.GetId())
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)


class ToggleButton(Button):
    is_active = False

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        size: wx.Size = BUTTON_SIZE,
        style: int = wx.BORDER_NONE,
        radius: float = SIZE_UNIT / 4,
        bg_colour: wx.Colour = BG_COLOUR,
        hover_colour: wx.Colour = HOVER_COLOUR,
        active_colour: wx.Colour = ACTIVE_COLOUR,
        toggle_colour: wx.Colour = TOGGLE_COLOUR,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(
            parent,
            label,
            size,
            style,
            radius,
            bg_colour,
            hover_colour,
            active_colour,
            *args,
            **kwargs,
        )

        self.toggle_colour = toggle_colour

    def GetValue(self) -> bool:
        return self.is_active

    def SetValue(self, flag: bool) -> None:
        self.is_active = flag
        self.Refresh()

    def _update_colour(self) -> None:
        super()._update_colour()
        if self.is_active:
            self.SetBackgroundColour(self.toggle_colour)

    def _on_enter(self, event: wx.MouseEvent) -> None:
        if not self.is_active:
            super()._on_enter(event)

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if not self.is_active:
            super()._on_leave(event)

    def _on_release(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.is_active = not self.is_active
            super()._on_release(event)


class SwitchButtons(wx.Control):

    def __init__(
        self,
        parent: wx.Window,
        labels: Iterable[str],
        style: int = wx.BORDER_NONE,
        radius: float = SIZE_UNIT / 4,
        bg_colour: wx.Colour = BG_COLOUR,
        hover_colour: wx.Colour = HOVER_COLOUR,
        active_colour: wx.Colour = ACTIVE_COLOUR,
        toggle_colour: wx.Colour = TOGGLE_COLOUR,
        rows: int = 0,
        cols: int = 0,
        gap: wx.Size | None = None,
        vgap: int = 0,
        hgap: int = 0,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, style=style, *args, **kwargs)

        self.buttons = tuple(
            SwitchButtons.Button(
                self,
                label=label,
                style=style,
                radius=radius,
                bg_colour=bg_colour,
                hover_colour=hover_colour,
                active_colour=active_colour,
                toggle_colour=toggle_colour,
                *args,
                **kwargs,
            )
            for label in labels
        )
        self.SetSelection(0)

        if gap:
            hgap, vgap = gap

        sizer = wx.GridSizer(rows, cols, vgap, hgap)

        for item in self.buttons:
            sizer.Add(item, flag=wx.EXPAND)

        self.SetSizer(sizer)

    def Add(self):
        raise AttributeError

    def GetValue(self) -> str | None:
        for item in self.buttons:
            if item.is_active:
                return item.label

    def SetValue(self, value: str) -> None:
        for i, item in enumerate(self.buttons):
            if item.label == value:
                return self.SetSelection(i)
        self.SetSelection(-1)

    def GetSelection(self) -> int:
        for i, item in enumerate(self.buttons):
            if item.is_active:
                return i
        return -1

    def SetSelection(self, index: int) -> None:
        for item in self.buttons:
            item.is_active = False
        item = self.buttons[index]
        item.is_active = True
        self.Refresh()

    def Refresh(self) -> None:
        for item in self.buttons:
            if item.is_active:
                item.SetBackgroundColour(item.toggle_colour)
            elif item.is_pressed:
                item.SetBackgroundColour(item.active_colour)
            else:
                item.SetBackgroundColour(item.bg_colour)
            item.Refresh()

    class Button(ToggleButton):

        def __init__(
            self,
            parent: SwitchButtons,
            *args,
            **kwargs,
        ) -> None:

            super().__init__(parent, *args, **kwargs)

        def _on_press(self, event: wx.MouseEvent) -> None:
            if not self.is_active:
                super()._on_press(event)

        def _on_release(self, event: wx.MouseEvent) -> None:
            if self.IsEnabled():
                for item in self.GetParent().buttons:  # type: ignore
                    if item is not self:
                        item.is_active = False
                        item._on_leave(event)
                self.is_active = False
                super()._on_release(event)


class CheckBox(ToggleButton):

    def __init__(
        self,
        parent: wx.Window,
        label: str,
        size: wx.Size | None = None,
        style: int = wx.BORDER_NONE,
        radius: float = SIZE_UNIT / 8,
        bg_colour: wx.Colour = BG_COLOUR,
        hover_colour: wx.Colour = HOVER_COLOUR,
        active_colour: wx.Colour = ACTIVE_COLOUR,
        toggle_colour: wx.Colour = TOGGLE_COLOUR,
        *args,
        **kwargs,
    ) -> None:

        if size is None:
            fw, fh = parent.GetFont().GetPixelSize()
            size = wx.Size(int(fh * (len(label) + 1.3)), int(fh * 1.2))

        super().__init__(
            parent,
            label,
            size,
            style,
            radius,
            bg_colour,
            hover_colour,
            active_colour,
            toggle_colour,
            *args,
            **kwargs,
        )

        self.SetForegroundColour(parent.GetForegroundColour())

    def _draw_content(
        self,
        dc: wx.BufferedPaintDC,
        gc: wx.GraphicsContext,
        w: int,
        h: int,
    ) -> None:

        fw, fh = self.GetFont().GetPixelSize()
        px = int(fh * 0.2)
        x = fh - px
        r = self.radius

        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        gc.SetBrush(wx.Brush(wx.TRANSPARENT_BRUSH))
        gc.SetPen(wx.Pen(self.GetBackgroundColour(), px))
        gc.DrawRoundedRectangle(px // 2, (h - fh + px // 2) // 2, x, x, r)

        if self.is_active:
            gc.SetPen(wx.Pen(self.GetForegroundColour(), px))
            ox, oy = px * 1.5, (h - fh + px // 2) // 2 + px
            size = fh * 0.8
            points = [
                wx.Point2D(ox, oy),
                wx.Point2D(ox + size / 4, oy + size / 2),
                wx.Point2D(ox + size, oy - size / 4),
            ]
            gc.DrawLines(points)

        tw, th = dc.GetTextExtent(self.label)
        dc.DrawText(self.label, int(fh * 1.3), (h - th) // 2)

    def _on_enter(self, event: wx.MouseEvent) -> None:
        Button._on_enter(self, event)

    def _on_leave(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.SetBackgroundColour(
                self.toggle_colour if self.is_active else self.bg_colour
            )
            self.Refresh()

    def _on_release(self, event: wx.MouseEvent) -> None:
        if self.IsEnabled():
            self.is_active = not self.is_active
            self.is_pressed = False
            self._on_enter(event)
            self._fire_click_event()


class ListBox(wx.VListBox, wx.Control):
    items: tuple[str, ...]

    def __init__(
        self,
        parent: wx.Window,
        items: Iterable[str] = (),
        style: int = 0,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(parent, style=style, *args, **kwargs)

        self.SetItems(items)
        self.SetSelectionBackground(TOGGLE_COLOUR)

    def GetItems(self) -> tuple[str, ...]:
        return self.items

    def SetItems(self, items: Iterable[str]) -> None:
        self.items = tuple(items)
        self.SetSelection(-1)
        self.SetItemCount(len(self.items))

    def Append(self, value: str) -> None:
        self.SetItems((*self.items, value))

    def Delete(self, index: int) -> None:
        self.SetItems((*self.items[0:index], *self.items[index + 1 :]))

    def Clear(self) -> None:
        self.SetItems(())

    def OnMeasureItem(self, index) -> int:
        return int(self.GetFont().GetPixelSize().GetHeight() * 1.2)

    def OnDrawItem(self, dc, rect, index) -> None:
        text = self.items[index]
        fw, fh = self.GetFont().GetPixelSize()
        dc.SetTextForeground(wx.Colour(33, 33, 33))
        dc.DrawText(text, rect.x + fh // 5, rect.y + fh // 10)

    def OnDrawBackground(self, dc, rect, index) -> None:
        if self.IsSelected(index):
            dc.SetBrush(wx.Brush(self.GetSelectionBackground()))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)
