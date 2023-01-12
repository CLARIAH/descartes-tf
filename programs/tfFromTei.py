import sys
import os
import re
import collections
import yaml
import xml.etree.ElementTree as ET
from tf.fabric import Fabric
from tf.convert.walker import CV
from tf.core.helpers import initTree, unexpanduser

HELP = """

Convert TEI to TF and optionally loads the TF.

python3 tfFromTrim.py [task] [--help]

--help: print this text and exit

task:
    if not passed, generates tf;
    otherwise it should have one of the following values:

checkonly:
    just reports on the elements in the source;
    does not generate TF;
    if not passed, no checking takes place.
load:
    loads the generated TF;
    if missing, no loading is performed.
loadonly:
    does not generate TF;
    loads previously generated TF.

N.B. This program must be run in the programs directory of the clone
of the CLARIAH/descartes-tf repository on github.
"""

TASKS = set(
    """
    checkonly
    loadonly
    load
""".strip().split()
)


BACKEND = "github"
BASE = os.path.expanduser(f"~/{BACKEND}")
ORG = "CLARIAH"
REPO = "descartes-tf"
SOURCE_FILE = "JapAM-EJB-DR.xml"

REPO_DIR = f"{BASE}/{ORG}/{REPO}"
SOURCE_DIR = f"{REPO_DIR}/source"
GRAPHICS_DIR = f"{SOURCE_DIR}/illustrations"
YAML_DIR = f"{REPO_DIR}/yaml"
LOCAL_DIR = f"{REPO_DIR}/_local"
TF_DIR = f"{REPO_DIR}/tf"
REPORT_DIR = f"{REPO_DIR}/report"


def readYaml(baseName):
    filePath = f"{YAML_DIR}/{baseName}.yml"
    if os.path.exists(filePath):
        with open(f"{YAML_DIR}/{baseName}.yml") as fh:
            return yaml.load(fh, Loader=yaml.FullLoader)
    return {}


SETTINGS = readYaml("settings")
SOURCE_PATH = f"{SOURCE_DIR}/{SETTINGS['sourceFile']}"

VERSION_TF = SETTINGS["versionTf"]
OUT_DIR = f"{TF_DIR}/{VERSION_TF}"
INT_FEATURES = set(SETTINGS["intFeatures"])
FEATURE_META = SETTINGS["featureMeta"]

NUM_RE = re.compile(r"""[0-9]""", re.S)


# ERROR HANDLING

warnings = collections.defaultdict(set)
errors = collections.defaultdict(set)


def docSummary(docs):
    nDocs = len(docs)
    rep = "   0x" if not nDocs else f"   1x {docs[0]}" if nDocs == 1 else ""
    if not rep:
        examples = " ".join(docs[0:2])
        rest = " ..." if nDocs > 2 else ""
        rep = f"{nDocs:>4}x {examples}{rest}"
    return f"{rep:<30}"


def showDiags(diags, kind, batch=20):
    if not diags:
        print("No diags")
    else:
        for (diag, docs) in sorted(diags.items()):
            docRep = docSummary(
                sorted(docs, key=lambda d: tuple(int(x) for x in d.split(":")))
            )
            print(f"{kind} {diag} {len(docs):>4}x {docRep}")


# SOURCE CORRECTION

CORRECTIONS = (
    (40245, "Vir clarissime,", """<div type="opener"><p>∞</p></div>"""),
    (24488, """<figure rend="inline">""", """<figure>"""),
    (24518, """<figure rend="inline">""", """<figure>"""),
)


def correctText(lines):
    for (lineNum, was, becomes) in CORRECTIONS:
        lineIndex = lineNum - 1
        origLine = lines[lineIndex]
        nOccs = origLine.count(was)

        if nOccs == 1:
            newLine = origLine.replace(was, becomes.replace("∞", was))
            lines[lineIndex] = newLine
            print(f"CORRECTION on {lineNum} applied:\n---{origLine.strip()}-->")
            print(f"---{newLine.strip()}---")
        else:
            print(f"CORRECTION on {lineNum} not applied:\n---{origLine.strip()}---")
            if nOccs == 0:
                print(f"{was} not found")
            elif nOccs > 1:
                print(f"{was} {nOccs} x found")
    return "".join(lines)


# SOURCE READING

P = "p"
S = "sentence"
VOLUME = "volume"
LETTER = "letter"
PAGE = "page"
WORD = "word"
TEI = "tei"
TEI_HEADER = "teiheader"
META = "meta"
HEAD = "head"
TEXT = "text"
N = "n"
FORMULA = "formula"
PB = "pb"
LB = "lb"
GRAPHIC = "graphic"
FIGURE = "figure"
HI = "hi"
ADD = "add"
DIV = "div"
OPENER = "opener"
CLOSER = "closer"
ADDRESS = "address"
POSTSCRIPTUM = "postscriptum"

TEXT_ATTRIBUTES = """
    italic
    sub
    sup
    margin
""".strip().split()

TRANSPARENT_ELEMENTS = set(
    """
    text
    body
    teiset
""".strip().split()
)

SKIP_ELEMENTS = set(
    """
""".strip().split()
)

NODE_ELEMENTS = set(
    """
    head
    p
    hi
    formula
    figure
""".strip().split()
)

BREAKS = set(
    """
    lb
    pb
""".strip().split()
)

DO_TEXT_ELEMENTS = set(
    """
    head
    p
    hi
    formula
    add
""".strip().split()
)

DO_TAIL_ELEMENTS = set(
    """
    pb
    lb
    hi
    formula
    figure
    add
""".strip().split()
)

WORD_PARTS_RE = re.compile(
    r"""
    ^
    (.*?)
        (
            \W
            .*
        )
    (\w*)
    (.*)
    $
    """,
    re.S | re.I | re.X,
)

WHITE_RE = re.compile(r"""\s\s+""", re.S)
NON_WORD_CHAR = r",./\\<>;:'\"\[\]{}()!@#$%^&*+=_«» \t\n-"
WORD_CHAR = f"^{NON_WORD_CHAR}"
WORD_RE = re.compile(
    rf"""
        ([{WORD_CHAR}]+)
        ([{NON_WORD_CHAR}]*)
    """,
    re.S | re.X,
)
NON_WORD_RE = re.compile(
    rf"""
        ^
        ([{NON_WORD_CHAR}]+)
        (.*)
    """,
    re.S | re.X,
)
PUNC_RE = re.compile(
    rf"""
        ^
        ([{NON_WORD_CHAR}]+)
        $
    """,
    re.S | re.X,
)

CLEAN_GRAPHIC_RE = re.compile(
    r"""
    <figure\ rend="inline">
    <graphic[^>]*/>
    </figure>
    (
        <formula
        [^>]*
        >
    )
    """,
    re.S | re.I | re.X,
)


# CHECKING


def nodeInfo(node, analysis, inText):
    tag = node.tag.lower()
    atts = node.attrib

    if inText:
        if not atts:
            analysis[f"{tag}.."] += 1
        else:
            for (k, v) in atts.items():
                vTrim = NUM_RE.sub(N, v)
                if k == "value":
                    vTrim = "x"
                isLayout = k == "rend"
                if isLayout:
                    analysis[f" {tag}.{k}={v}"] += 1
                else:
                    analysis[f"{tag}.{k}={vTrim}"] += 1

    if not inText:
        inText = tag == TEXT
    for child in node:
        nodeInfo(child, analysis, inText)


def analyse(text):
    analysis = collections.Counter()
    root = ET.fromstring(text)
    nodeInfo(root, analysis, False)
    return analysis


def check():
    def writeReport():
        reportFile = f"{REPORT_DIR}/elements.tsv"
        initTree(REPORT_DIR)
        with open(reportFile, "w") as fh:
            for (path, amount) in sorted(analysis.items()):
                fh.write(f"{path}\t{amount}\n")
        print(f"Analysis written to {reportFile}")

    analysis = collections.Counter()

    with open(SOURCE_PATH) as fh:
        text = fh.read()
        analysis = analyse(text)

    writeReport()

    return True


# SET UP CONVERSION


def getConverter():
    TF = Fabric(locations=OUT_DIR)
    return CV(TF)


def convert():
    initTree(OUT_DIR, fresh=True, gentle=True)

    cv = getConverter()

    return cv.walk(
        director,
        SETTINGS["slotType"],
        otext=SETTINGS["otext"],
        generic=SETTINGS["generic"],
        intFeatures=INT_FEATURES,
        featureMeta=FEATURE_META,
        generateTf=True,
    )


# DIRECTOR


def director(cv):
    cur = {}

    with open(SOURCE_PATH) as fh:
        text = list(fh)
        text = correctText(text)
        text = CLEAN_GRAPHIC_RE.sub(r"\1", text)
        root = ET.fromstring(text)

    cur["stop"] = False
    volumeNode = cv.node(VOLUME)
    volNum = 1
    print(f"volume {volNum:>2}")
    cv.feature(volumeNode, n=volNum)
    cur[VOLUME] = volumeNode
    cur["volNum"] = volNum
    cur["newVolume"] = None
    walkNode(cv, cur, root)

    print("done")

    # delete meta data of unused features

    for nodeType in (PAGE, VOLUME):
        if nodeType in cur:
            cv.terminate(cur[nodeType])

    for feat in FEATURE_META:
        if not cv.occurs(feat):
            print(f"WARNING: feature {feat} does not occur")
            cv.meta(feat)

    if warnings:
        showDiags(warnings, "WARNING")
    if errors:
        showDiags(errors, "ERROR")
        cv.stop("because of irregularities")


# WALKERS


def walkNode(cv, cur, node):
    """Handle all elements in the XML file."""
    if cur["stop"]:
        return

    tag = node.tag.lower()

    atts = node.attrib
    if tag == ADD:
        textAttribute = atts.get("place", None)
        if textAttribute:
            if textAttribute not in TEXT_ATTRIBUTES:
                addError(f"unrecognized place = `{textAttribute}`", cur)
        if textAttribute is not None:
            del atts["place"]
    else:
        textAttribute = atts.get("rend", None)
        if textAttribute:
            if tag == HEAD and textAttribute == "h3":
                textAttribute = None
                del atts["rend"]
        if textAttribute:
            if textAttribute in {"h4", "h5"}:
                if P in cur and len(cur[P]) > 0:
                    cv.feature(cur[P][-1], level=2 if textAttribute == "h4" else 3)
                    textAttribute = None
                    del atts["rend"]
        textAttribute = "italic" if textAttribute == "i" else textAttribute
        if textAttribute:
            if textAttribute == "inline":
                cur["figureType"] = "inline"
                textAttribute = None
                del atts["rend"]
        if textAttribute:
            if textAttribute not in TEXT_ATTRIBUTES:
                addError(f"unrecognized rend = `{textAttribute}`", cur)
        if textAttribute is not None:
            del atts["rend"]

    featAtts = featsFromAtts(atts)

    if tag in SKIP_ELEMENTS:
        return

    elif tag in BREAKS:
        if tag == PB:
            curPage = cur.get(PAGE, None)
            if curPage:
                linkIfEmpty(cv, cur, curPage, "page", dontwarn=True, wrap=True)
                cv.terminate(curPage)
            if N in atts:
                (volNum, pageNum) = atts[N].split("-", 1)
                volNum = int(volNum)
                pageNum = int(pageNum)
                if cur.get("volNum", None) != volNum:
                    cur["newVolume"] = volNum
                if PAGE in cur:
                    cv.terminate(cur[PAGE])
                cur[PAGE] = cv.node(PAGE)
                cv.feature(cur[PAGE], n=pageNum)
                cur["pageNum"] = pageNum
            else:
                addError("pb without n attribute", cur)
        elif tag == LB:
            inHead = HEAD in cur and len(cur[HEAD])
            if inHead:
                addText(cv, cur, " -", False, False)
            else:
                addWarning("lb outside head", cur)

    elif tag == TEI:
        cur[LETTER] = cv.node(LETTER)
        cur["pNum"] = 0

    elif tag == TEI_HEADER:
        cur["inMeta"] = True
        cur[META] = {}

    elif tag == META:
        if cur.get("inMeta", False):
            key = featAtts["type"]
            value = featAtts["value"]
            cert = featAtts.get("cert", None)
            resp = featAtts.get("resp", None)

            if key == "alt_id":
                cur[META].setdefault("alt_id", []).append(value)
            else:
                cur[META][key] = value

            if cert is not None:
                cur[META].setdefault("cert", []).append(f"{key}:cert={cert}")
            if resp is not None:
                cur[META].setdefault("resp", []).append(f"{key}:resp={resp}")
        else:
            addWarning(f"{tag} outside {TEI_HEADER}", cur)

    elif tag == GRAPHIC:
        if FIGURE in cur and len(cur[FIGURE]) > 0:
            figureNode = cur[FIGURE][-1]
            isInline = cur.get("figureType", None) == "inline"
            url = featAtts["url"]
            isPng = url.endswith(".png")

            if isInline and not isPng:
                addWarning(f"Graphic {url} is inline but not png", cur)
            elif not isInline and isPng:
                addWarning(f"Graphic {url} is not inline but png", cur)
            if not os.path.isfile(f"{GRAPHICS_DIR}/{url}"):
                addWarning(f"No graphic {url}", cur)
            kind = "symbol" if isInline else "illustration"
            cv.feature(figureNode, typ=kind, **featAtts)
            slot = cv.slot()
            cv.feature(slot, typ="empty", trans="", punc=" ")
            cur[WORD] = slot
        else:
            addWarning("graphic outside figure", cur)
        cur["figureType"] = None

    elif tag == ADD:
        pass

    elif tag == DIV:
        tp = atts.get("type", None)
        if tp is None or tp == "para":
            pass
        elif tp in {OPENER, CLOSER, ADDRESS, POSTSCRIPTUM}:
            cur[tp] = cv.node(tp)
        else:
            pass

    elif tag in NODE_ELEMENTS:
        curNode = cv.node(tag)
        (tp, seq) = curNode
        if tag in cur:
            cur[tag].append(curNode)
            if tag != HI and len(cur[tag]) > 1:
                addWarning(f"{tag} nesting level {len(cur[tag])}", cur)
        else:
            cur[tag] = [curNode]

        if atts:
            if tag != HEAD:
                cv.feature(curNode, **featAtts)

        if tag == HEAD:
            newP = cv.node(P)
            cur["pNum"] += 1
            cv.feature(newP, typ="head", n=cur["pNum"])
            cur.setdefault(P, []).append(newP)
        elif tag == P:
            cur["pNum"] += 1
            cv.feature(cur[P][-1], n=cur["pNum"])
            if sentenceFormation(cur):
                newS = cv.node(S)
                cur["sNum"] = 1
                cv.feature(newS, n=cur["sNum"])
                cur[S] = newS

    elif tag in TRANSPARENT_ELEMENTS:
        pass

    else:
        addError(f"unrecognized tag = {tag}", cur)

    if textAttribute is not None:
        cur[textAttribute] = 1

    if tag in DO_TEXT_ELEMENTS:
        inFormula = FORMULA in cur and len(cur[FORMULA])
        inSentence = cur.get(S, None) is not None
        addText(cv, cur, node.text, inFormula, inSentence)

    # ------ begin walk through the children nodes ------
    for child in node:
        walkNode(cv, cur, child)
    # ------ end   walk through the children nodes ------

    if tag == TEI:
        curNode = cur[LETTER]
        if curNode:
            cv.terminate(curNode)
            del cur[LETTER]
        volNum = cur.get("newVolume", None)
        if volNum is not None:
            cv.terminate(cur[VOLUME])
            cur[VOLUME] = cv.node(VOLUME)
            cur["volNum"] = volNum
            cv.feature(cur[VOLUME], n=volNum)
            cur["newVolume"] = None
            print(f"volume {volNum:>2}")

    elif tag == TEI_HEADER:
        meta = {}

        for (key, value) in cur[META].items():
            meta[key] = ",".join(value) if type(value) is list else value

        cv.feature(cur[LETTER], **meta)

        cur["inMeta"] = False
        cur[META] = {}

    elif tag == ADD:
        pass

    elif tag == DIV:
        tp = atts.get("type", None)
        if tp is None or tp == "para":
            pass
        elif tp in {OPENER, CLOSER, ADDRESS, POSTSCRIPTUM}:
            cv.terminate(cur[tp])
            cur[tp] = None
        else:
            pass

    if textAttribute is not None:
        cur[textAttribute] = 0

    if tag in NODE_ELEMENTS:
        curNode = cur[tag][-1]
        if tag == P:
            if sentenceFormation(cur):
                curS = cur[S]
                cv.terminate(curS)
                cur[S] = None
        if curNode:
            cv.terminate(curNode)
            cur[tag].pop()

        if tag == HEAD:
            curP = cur[P][-1]
            cv.terminate(curP)
            cur[P].pop()

    if tag in DO_TAIL_ELEMENTS:
        if tag == PB and not (P in cur and len(cur[P])) and not node.tail.strip():
            return
        inFormula = FORMULA in cur and len(cur[FORMULA])
        inSentence = cur.get(S, None) is not None
        addText(cv, cur, node.tail, inFormula, inSentence)


# AUXILIARY


def addWarning(msg, cur):
    warnings[msg].add(getPos(cur))


def addError(msg, cur):
    errors[msg].add(getPos(cur))


def getPos(cur):
    volNum = cur.get("volNum", "?")
    pageNum = cur.get("pageNum", "?")
    return f"{volNum}:{pageNum}"


def featsFromAtts(atts):
    return dict(
        getInt(feat, value) if feat in INT_FEATURES else (feat, value)
        for (feat, value) in atts.items()
        if value is not None
    )


def getInt(feat, val):
    stripVal = val.lstrip("0")
    return (feat, int(stripVal)) if val.isdigit() else (f"{feat}str", val)


def sentenceFormation(cur):
    return not any(cur.get(tag, None) for tag in (OPENER, CLOSER, ADDRESS))


def doSentence(cv, cur, trans, punc):
    lastChar = trans[-1]
    if lastChar.lower() == lastChar:
        if len(punc) > 1 and punc[0] == "." and punc[1] in {" ", ")", "»"}:
            cv.terminate(cur[S])
            cur["sNum"] += 1
            newS = cv.node(S)
            cv.feature(newS, n=cur["sNum"])
            cur[S] = newS


def addText(cv, cur, text, inFormula, inSentence):
    if not text:
        return

    if inFormula:
        formulaNode = cur[FORMULA][-1]
        isTeX = cv.get("notation", formulaNode) == "TeX"
        if isTeX:
            cv.feature(formulaNode, tex=text.strip("$"))
        makeSlot(cv, cur, typ="formula", trans=text, punc=" ")
        curWord = cur[WORD]
        for tg in TEXT_ATTRIBUTES:
            if cur.get(tg, None):
                cv.feature(curWord, **{f"is{tg}": 1})
        return

    match = PUNC_RE.match(text)

    # \.[^ <)»0-9.[a-zA-Z;,*\]:(&'-]

    if match:
        punc = match.group(1)
        punc = WHITE_RE.sub(" ", punc)
        punc = punc.replace("\n", " ")
        if punc:
            trans = ""
            makeSlot(cv, cur, trans=trans, punc=punc)

    else:

        # if the text starts with white space: put it in a separate slot

        bareText = text.lstrip()
        if bareText != text:
            trans = ""
            punc = " "
            makeSlot(cv, cur, trans=trans, punc=punc)
            text = bareText

        # if there is a mixture between word characters and the rest
        # group them in pieces consisting of word characters with trailing
        # punctuation and white space
        # Beware of the fact that text can start with non-word material

        match = NON_WORD_RE.match(text)
        if match:
            (punc, text) = match.group(1, 2)
            makeSlot(cv, cur, trans="", punc=punc)
            curWord = cur[WORD]

        for match in WORD_RE.finditer(text):
            (trans, punc) = match.group(1, 2)
            if punc:
                punc = WHITE_RE.sub(" ", punc)
                punc = punc.replace("\n", " ")
            makeSlot(cv, cur, trans=trans, punc=punc)
            curWord = cur[WORD]
            if inSentence:
                doSentence(cv, cur, trans, punc)

            for tg in TEXT_ATTRIBUTES:
                if cur.get(tg, None):
                    cv.feature(curWord, **{f"is{tg}": 1})


def makeSlot(cv, cur, typ=None, trans=None, punc=None):
    typVal = {} if typ is None else dict(typ=typ)
    inP = P in cur and len(cur[P])
    if trans is None:
        trans = ""
    if punc is None:
        punc = ""

    if not inP:
        addWarning(f"slot {typ=} {trans=} {punc=} outside p", cur)

    textVal = dict(trans=trans, punc=punc)

    slot = cv.slot()
    cv.feature(slot, **typVal, **textVal)
    cur[WORD] = slot


def linkIfEmpty(cv, cur, node, spec, dontwarn=False, wrap=False):
    if not cv.linked(node):
        if not dontwarn:
            addWarning(f"empty {spec}", cur)
        doWrap = wrap and not (P in cur and len(cur[P]))
        if doWrap:
            newP = cv.node(P)
            cur.setdefault(P, []).append(newP)
            cur["pNum"] += 1
            cv.feature(newP, n=cur["pNum"])
        makeSlot(cv, cur, typ="empty")
        if doWrap:
            cv.terminate(newP)
            cur[P].pop()


# TF LOADING (to test the generated TF)


def loadTf():
    if not os.path.exists(OUT_DIR):
        print(f"Directory {unexpanduser(OUT_DIR)} does not exist.")
        print("No tf found, nothing to load")
        return False

    TF = Fabric(locations=[OUT_DIR])
    allFeatures = TF.explore(silent=True, show=True)
    loadableFeatures = allFeatures["nodes"] + allFeatures["edges"]
    api = TF.load(loadableFeatures, silent=False)
    if api:
        print(f"max node = {api.F.otype.maxNode}")

    return True


# MAIN


def main():
    args = () if len(sys.argv) == 1 else tuple(sys.argv[1:])

    if "--help" in args:
        print(HELP)
        return True

    onlies = set()

    good = True

    for task in args:
        if task not in TASKS:
            print(f"Unknown task: `{task}`")
            good = False
        elif task.endswith("only"):
            onlies.add(task)

    if len(onlies) > 1:
        print(f"You cannot specify these tasks together: {', '.join(onlies)}")
        good = False

    if not good:
        print(HELP)
        return False

    doCheck = "checkonly" in args
    doConvert = "loadonly" not in args and "checkonly" not in args
    doLoad = "load" in args or "loadonly" in args

    print(f"TEI to TF converter: for {ORG}")

    if doCheck:
        print("Just perform checks")
        return check()

    print(f"TF  target version = {VERSION_TF}")

    if doConvert:
        if not convert():
            return False

    if doLoad:
        loadTf()

    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
