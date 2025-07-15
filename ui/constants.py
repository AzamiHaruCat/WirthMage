import wx

SIZE_UNIT = int(min(*wx.GetDisplaySize()) * 0.02)

BASE_FONT = wx.Font(
    wx.Size(0, SIZE_UNIT),
    wx.FONTFAMILY_DEFAULT,
    wx.FONTSTYLE_NORMAL,
    wx.FONTWEIGHT_NORMAL,
    faceName="BIZ UDPGothic",
)
MONO_FONT = wx.Font(
    wx.Size(0, SIZE_UNIT),
    wx.FONTFAMILY_MODERN,
    wx.FONTSTYLE_NORMAL,
    wx.FONTWEIGHT_NORMAL,
    faceName="BIZ UDGothic",
)

BUTTON_SIZE = wx.Size(SIZE_UNIT * 7, int(SIZE_UNIT * 1.5))
BG_COLOUR = wx.Colour(0x40, 0xC0, 0x80)
HOVER_COLOUR = wx.Colour(0x20, 0x60, 0x40)
ACTIVE_COLOUR = wx.Colour(0x80, 0xF0, 0xF0)
TOGGLE_COLOUR = wx.Colour(0xF0, 0xC0, 0x20)
