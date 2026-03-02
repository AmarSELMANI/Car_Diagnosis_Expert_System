# gui/animations.py
def fade_in(widget, alpha=0.0):
    if alpha < 1:
        widget.attributes("-alpha", alpha)
        widget.after(30, fade_in, widget, alpha + 0.05)

def fade_out(widget, callback=None, alpha=1.0):
    if alpha > 0:
        widget.attributes("-alpha", alpha)
        widget.after(30, fade_out, widget, callback, alpha - 0.05)
    else:
        if callback:
            callback()
