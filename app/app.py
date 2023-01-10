from tf.advanced.find import loadModule
from tf.advanced.app import App


class TfApp(App):
    def __init__(app, *args, silent=False, **kwargs):
        super().__init__(*args, silent=silent, **kwargs)
        app.image = loadModule("image", *args)

        app.image.getImagery(app, silent, checkout=kwargs.get("checkout", ""))

        app.reinit()

    # PRETTY HELPERS

    def getGraphics(app, isPretty, n, nType, outer):
        result = ""

        if outer:
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
