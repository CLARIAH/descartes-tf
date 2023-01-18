<img src="images/logo.png" align="right" width="200"/>
<img src="images/tf.png" align="right" width="200"/>

# Feature documentation

Here you find a description of the text of the letters of Descartes,
the
[Text-Fabric model](https://annotation.github.io/text-fabric/tf/about/datamodel.html)
in general, and the node types, features of the
this in particular.

See also

*   [about](about.md) for the provenance of the data;
*   [TF docs](https://annotation.github.io/text-fabric/tf) for documentation on Text-Fabric.

## Transcription

The corpus consists of letters, which are grouped in volumes.
Letters are divided in paragraphs, some of which act as address, opener, closer, or
postscriptum.

Letters may contain illustrations, symbols, and mathematical formulas.

### Sentences

We have added the concept of sentence.
A sentence is a piece of text within a paragraph that is
terminated by a `.` . 

Not all `.`s act as sentence terminator, though, e.g. in
`Kal. Aprilis` it marks an abbreviation.

We have tried to exclude most of these cases.

The purpose of adding sentences was to have a convenient
division within paragraphs. This division can be used to
display manageable chunks of the corpus.

It can also be used to detect parallel passages, i.e. similar sentences
in the correspondence.

## Text-Fabric model

The Text-Fabric model views the text as a series of atomic units, called
*slots*. In this corpus [*words*](#node-type-word) are the slots.

On top of that, more complex textual objects can be represented as *nodes*. In
this corpus we have node types for:

[*word*](#node-type-word),
[*hi*](#node-type-hi),
[*figure*](#node-type-figure),
[*formula*](#node-type-formula),
[*sentence*](#node-type-sentence),
[*head*](#node-type-head),
[*opener*](#node-type-opener),
[*closer*](#node-type-closer),
[*postscriptum*](#node-type-postscriptum),
[*address*](#node-type-address),
[*p*](#node-type-p),
[*page*](#node-type-page),
[*letter*](#node-type-letter),
[*volume*](#node-type-volume),

Note that *slots* are nodes themselves.

The type of every node is given by the feature
[**otype**](https://annotation.github.io/text-fabric/tf/cheatsheet.html#special-node-feature-otype).
Every node is linked to a subset of slots by
[**oslots**](https://annotation.github.io/text-fabric/tf/cheatsheet.html#special-edge-feature-oslots).

Nodes can be annotated with features.
Relations between nodes can be annotated with edge features.
See the table below.

Text-Fabric supports up to three customizable section levels.
In this corpus we define them as:
[*volume*](#node-type-volume),
[*letter*](#node-type-letter),
and
[*p*](#node-type-p).

# Reference table of features

*(Keep this under your pillow)*

## Node type [*word*](#word)

This is the slot type, i.e. the nodes of type `word` are the *slots*.

Basic unit corresponding to a word plus attached non-word stuff such as punctuation,
brackets, etc.

feature | values | description
------- | ------ | ------
**trans** | `quaestionem` | the string that makes up a word, without punctuation
**punc** | `, ` | non-word characters after a word, including whitespace
**isitalic** | `1` | indicates the word is in italics
**ismargin** | `1` | indicates the word is in the margin
**issub** | `1` | indicates the word is in subscript
**issup** | `1` | indicates the word is in superscript
**typ** | `empty` `formula` | indicates the kind of word

### Remarks

* **typ** = `empty`: deliberately empty word, i.e. **trans** is empty or absent;
  however, **punc** may contain something, typically a space.
* the **is**xxx features have only one possible value: `1`.
  They can also be [absent](#absent).

## Node type [*hi*](#hi)

Stretches of text with special formatting.
This node type has no special features.
All words belonging to **hi** nodes have their special formatting
recorded in the **is...** features, listed under
[*word*](#node-type-word).

Nodes of this type may be nested. They may also overlap without proper
nesting. However, as the data is generated from XML, it is likely
that all overlap occurs in the form of nesting.

## Node type [*figure*](#figure)

Figures come in two kinds: symbols and illustrations.
They are represented by an image.
These nodes have an empty slot, which links them to textual positions.

feature | values | description
------- | ------ | ------
**typ** | `symbol` `illustration` | the kind of image
**url** | `cossic1.png` `AT1-101a.gif` | file name of the image

## Node type [*formula*](#formula)

Mathematical formula in [TeX](https://en.wikipedia.org/wiki/TeX) notation.
They will be typeset by 
[MathJax](https://www.mathjax.org)
when being displayed.
Note that in the Text-Fabric browser MathJax 3 is used, while in notebooks
running Jupyterlab 3.5 MathJax 2 still rules.

The TeX code sits in the **trans** feature of a single slot
with **typ** = `formula` that belongs to the **formula** node.

It also is contained, without the surrounding `$`s, in the feature
**notation** of the **formula** node.
This gives you the opportunity to view the source code of formulas.

feature | values | description
------- | ------ | ------
**notation** | `TeX` | notation method of the formula
**tex** | `A\over B` | TeX source code of a formula

## Node type [*sentence*](#sentence)

Sentence, i.e. a part in a paragraph terminated by a full stop.
`.` that are used for other purposes do not count as a full stop,
e.g. in abbreviations and numbers.

feature | values | description
------- | ------ | ------
**n** | `1` `2` | sequence number of a sentence within the paragraph.

## Node type [*head*](#head)

Contains a paragraph at the start of a letter, acting as a header line.

## Node type [*opener*](#opener)

Contains paragraphs at the start of a letter, the salutation.

## Node type [*closer*](#closer)

Contains paragraphs at the end of a letter, the sender.

## Node type [*postscriptum*](#postscriptum)

Contains paragraphs at the end of a letter, between closer, and address,
containing a postscript.

## Node type [*address*](#address)

Contains paragraphs at the end of a letter, after the closer,
containing the address of the recipient.

## Node type [*p*](#p)

Section level 3.

Paragraph.

feature | values | description
------- | ------ | ------
**n** | `1` `2` | sequence number of a paragraph within the letter
**level** | `2` `3` | level of a paragraph when it acts like a heading

## Node type [*page*](#page)

Page in the printed edition.

feature | values | description
------- | ------ | ------
**n** | `1` `2` | sequence number of a page within the volume

## Node type [*letter*](#letter)

Section level 2.

Letter, identified by **id**.
There is various metadata attached to letters,
such as senders, recipients, dates, locations.

feature | values | description
------- | ------ | ------
**id** | `1049` | identifier of a letter
**alt_id** | `AM1-005-002,AT,EJB010` | alternative identifiers of a letter
**alt_date** | `1639` | alternative date of a letter
**cert** | `recipientloc:cert=high,senderloc:cert=high` | indication of certitude per feature
**date** | `1619-01-24` | date of a letter
**intermediary** | `Plempius:Vopiscus-Fortunatus:1601-1671` | intermediary in the transmission of a letter
**language** | `fr`, `la`, `nl`, `fr la` | language identifier(s) of a letter
**resp** | `recipientloc:resp=EJB,senderloc:resp=EJB` | indication of responsibility for the value of a feature (EJB = Erik-Jan Bos)
**recipient** | `Beeckman:Isaac:1588-1637` | recipient of a letter
**recipientloc** | `Middelburg, NL` | location of the recipient of a letter
**sender** | `Descartes:Rene:1596-1650` | sender of a letter
**senderloc** | `Egmond aan den Hoef, NL` | location of the sender of a letter

## Node type [*volume*](#volume)

Section level 1.

Paragraph.

feature | values | description
------- | ------ | ------
**n** | `1` `2` | sequence number of a volume in the corpus.

## Additional remark on feature values

### absent

When we say that a feature is *absent* for a node, we mean that the node has no value
for that feature. For example, if the feature `isitalic` is absent for node `n`, then
`F.isitalic.v(n)` results in the Python value `None`, not the string `'None'`.

In queries, you can test for absence by means of `#`:

```
word trans#
```

gives all lines where the feature `trans` is absent.

See also
[search templates](https://annotation.github.io/text-fabric/tf/about/searchusage.html#value-specifications).

# Text formats

The following text formats are defined (you can also list them with `T.formats`).

format | description
--- | ---
`text-orig-full`     | the full text of all words
`layout-orig-full`   | the full text of all words, with special formatting indicating special characteristics of the text.

The formats with `text` result in strings that are plain text, without additional formatting.

The formats with `layout` result in pieces html with css-styles;
the richness of layout enables us to code more information
in the plain representation, e.g. italic words or marginal words.
