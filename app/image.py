import os
from glob import glob
from shutil import copyfile

from tf.advanced.helpers import dh
from tf.advanced.repo import checkoutRepo
from tf.core.timestamp import AUTO, TERSE, VERBOSE

LOCAL_IMAGE_DIR = "illustrations"

ILLUSTRATION_TO = "{}"
ILLUSTRATION_EXT = "gif"
SYMBOL_TO = "{}"
SYMBOL_EXT = "png"

ITEM_STYLE = "padding: 0.5rem;"

FLEX_STYLE = (
    "display: flex;"
    "flex-flow: row nowrap;"
    "justify-content: flex-start;"
    "align-items: center;"
    "align-content: flex-start;"
)

CAPTION_STYLE = dict(
    top=(
        "display: flex;"
        "flex-flow: column-reverse nowrap;"
        "justify-content: space-between;"
        "align-items: center;"
        "align-content: space-between;"
    ),
    bottom=(
        "display: flex;"
        "flex-flow: column nowrap;"
        "justify-content: space-between;"
        "align-items: center;"
        "align-content: space-between;"
    ),
    left=(
        "display: flex;"
        "flex-flow: row-reverse nowrap;"
        "justify-content: space-between;"
        "align-items: center;"
        "align-content: space-between;"
    ),
    right=(
        "display: flex;"
        "flex-flow: row nowrap;"
        "justify-content: space-between;"
        "align-items: center;"
        "align-content: space-between;"
    ),
)


def imageCls(app, n):
    api = app.api
    F = api.F
    nType = F.otype.v(n)

    if nType != "figure":
        return (nType, None, None)

    return (nType, F.typ.v(n), F.url.v(n))


def getImages(
    app,
    ns,
    kind=None,
    warning=True,
    _asString=False,
):
    if type(ns) is int or type(ns) is str:
        ns = [ns]
    result = []
    for n in ns:
        (nType, kind, identifier) = imageCls(app, n)
        if kind:
            imageBase = app._imagery.get(kind, {})
            image = imageBase.get(identifier, None)
            if image is None:
                thisImage = (
                    (
                        f"<span><b>no {kind}</b>"
                        f" <code>{identifier}</code></span>"
                    )
                    if warning
                    else ""
                )
            else:
                theImage = _useImage(app, image, kind, n)
                thisImage = (
                    f'<img src="{theImage}" style="display: inline;" />'
                )
            thisResult = thisImage if thisImage else None
        else:
            thisResult = (
                (f"<span><b>no {kind}</b> for <code>{nType}</code>s</span>")
                if warning
                else ""
            )
        result.append(thisResult)
    if not warning:
        result = [image for image in result if image]
    if not result:
        return ""
    if _asString:
        return "".join(result)
    resultStr = f'</div><div style="{ITEM_STYLE}">'.join(result)
    html = (
        f'<div style="{FLEX_STYLE}">'
        f'<div style="{ITEM_STYLE}">'
        f"{resultStr}</div></div>"
    ).replace("\n", "")
    dh(html)
    if not warning:
        return True


def _useImage(app, image, kind, node):
    _browse = app._browse
    aContext = app.context

    (imageDir, imageName) = os.path.split(image)
    (base, ext) = os.path.splitext(imageName)
    localBase = aContext.localDir if _browse else app.curDir
    localDir = f"{localBase}/{LOCAL_IMAGE_DIR}"

    if not os.path.exists(localDir):
        os.makedirs(localDir, exist_ok=True)

    localImageName = f"{kind}-{node}{ext}"
    localImagePath = f"{localDir}/{localImageName}"
    if not os.path.exists(localImagePath) or os.path.getmtime(image) > os.path.getmtime(
        localImagePath
    ):
        copyfile(image, localImagePath)
    base = "/local/" if _browse else ""
    return f"{base}{LOCAL_IMAGE_DIR}/{localImageName}"


def getImagery(app, silent, checkout=""):
    aContext = app.context
    org = aContext.org
    repo = aContext.repo
    graphicsRelative = aContext.graphicsRelative

    (imageRelease, imageCommit, imageLocal, imageBase, imageDir) = checkoutRepo(
        app._browse,
        org=org,
        repo=repo,
        folder=graphicsRelative,
        version="",
        checkout=checkout,
        withPaths=True,
        keep=True,
        silent=silent,
    )
    if not imageBase:
        app.api = None
        return

    app.imageDir = f"{imageBase}/{org}/{repo}/{graphicsRelative}"

    app._imagery = {}
    for (dirFmt, ext, kind) in (
        (SYMBOL_TO, SYMBOL_EXT, "symbol"),
        (ILLUSTRATION_TO, ILLUSTRATION_EXT, "illustration"),
    ):
        srcDir = dirFmt.format(app.imageDir)
        filePaths = glob(f"{srcDir}/*.{ext}")
        images = {}

        for filePath in filePaths:
            fileName = os.path.split(filePath)[1]
            images[fileName] = filePath

        app._imagery[kind] = images

        if silent in {VERBOSE, AUTO, TERSE}:
            dh(f"Found {len(images)} {kind}s<br>")
