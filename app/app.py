import types
from tf.advanced.find import loadModule
from tf.advanced.app import App


MODIFIERS = "italic margin sub sup".strip().split()


def fmt_layoutOrig(app, n, **kwargs):
    return app._wrapHtml(n, None)


class TfApp(App):
    def __init__(app, *args, silent=False, **kwargs):
        app.fmt_layoutOrig = types.MethodType(fmt_layoutOrig, app)

        super().__init__(*args, silent=silent, **kwargs)

        app.image = loadModule("image", *args)

        app.image.getImagery(app, silent, checkout=kwargs.get("checkout", ""))

        app.reinit()

    # FORMAT suppport

    def _wrapHtml(app, n, kind):
        api = app.api
        F = api.F
        Fs = api.Fs
        trans = F.trans.v(n) or ""
        punc = F.punc.v(n) or ""
        material = f"{trans}{punc}"
        clses = " ".join(cf for cf in MODIFIERS if Fs(f"is{cf}").v(n))
        return f'<span class="{clses}">{material}</span>' if clses else f"{material}"

    # GRAPHICS Support

    def getGraphics(app, isPretty, n, nType, outer):
        result = ""

        if True:
            theGraphics = app.image.getImages(
                app,
                n,
                kind=nType,
                _asString=True,
                warning=False,
            )
            if theGraphics:
                result = f"<div>{theGraphics}</div>" if isPretty else f" {theGraphics}"

        return result

    def imagery(app, objectType, kind):
        return set(app._imagery.get(objectType, {}).get(kind, {}))
