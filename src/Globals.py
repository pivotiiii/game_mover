from tkinter import font as fontImportAlias

debug = False
root = None
config = None
font = None

def init_font():
    global font
    font = fontImportAlias.Font(family="Segoe UI Variable", size = 14)

def measure_in_pixels(text: str) -> int:
    return font.measure(text)

def measure_in_text_units(text: str) -> int:
    pixels = measure_in_pixels(text)
    text_units = 0
    while text_units < pixels:
        text_units = text_units + 1
        pixels_conv = measure_in_pixels("0" * text_units)
        if pixels_conv > pixels:
            #if abs(measure_in_pixels("0" * (text_units - 1)) - pixels) < abs(pixels_conv - pixels):
            #    return text_units - 1
            return text_units

def widget_size_bind(event):
    if debug: print(f"{event.widget} width: {event.width} height: {event.height}")
        