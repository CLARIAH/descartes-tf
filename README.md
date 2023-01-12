# descartes-tf

[![DOI](https://zenodo.org/badge/570809409.svg)](https://zenodo.org/badge/latestdoi/570809409)

Letters of Descartes in Text-Fabric with math display.
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

![descartes](docs/images/logo.png)

# René Descartes - Brieven

In this repository we prepare the letters of
[Descartes](https://en.wikipedia.org/wiki/René_Descartes)
for the application of data science.

The source files are provided by the Huygens Institute, as the result of the CKCC project which was completed
in 2012.

From there we converted it to a
[Text-Fabric](https://github.com/annotation/text-fabric)
representation.

The result can be readily loaded into Python programs for further processing.

See [about](about.md) for the provenance of the data.

See [transcription](transcription.md) for how the resulting data is modelled.

## How to use

### Having Text-Fabric installed

This data can be processed by 
[Text-Fabric](https://annotation.github.io/text-fabric/tf).

Text-Fabric will automatically download the corpus data.

After [installing Text-Fabric](https://annotation.github.io/text-fabric/tf/about/install.html),
you can start the Text-Fabric browser by this command

```sh
text-fabric CLARIAH/descartes-tei
```

Alternatively, you can work in a Jupyter notebook and say

```python
from tf.app import use

A = use('CLARIAH/descartes-tei')
```

In both cases the data is downloaded and ends up in your home directory,
under `text-fabric-data`.

See also 
[start](https://nbviewer.jupyter.org/github/CLARIAH/descartes-tei/blob/master/tutorial/start.ipynb)
and
[search](https://nbviewer.jupyter.org/github/CLARIAH/descartes-tei/blob/master/tutorial/search.ipynb).

# Author

See [about](about.md) for the authors/editors of the data.

[Dirk Roorda](https://github.com/dirkroorda) is the author of the representation in Text-Fabric of the data,
and the tutorials and documentation.
