[![DOI](https://zenodo.org/badge/570809409.svg)](https://zenodo.org/badge/latestdoi/570809409)
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![SWH](https://archive.softwareheritage.org/badge/origin/https://github.com/CLARIAH/descartes-tf/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/CLARIAH/descartes-tf)

![descartes](docs/images/logo.png)

# René Descartes - Brieven

Letters of Descartes in Text-Fabric with math display.

In this repository we prepare the letters of
[Descartes](https://en.wikipedia.org/wiki/René_Descartes)
for the application of data science.

The source files are provided by the Huygens Institute, as the result of the CKCC project which was completed
in 2011.

From there we converted it to a
[Text-Fabric](https://github.com/annotation/text-fabric)
representation.

The result can be readily loaded into Python programs for further processing.

See [about](docs/about.md) for the provenance of the data.

See [transcription](docs/transcription.md) for how the resulting data is modelled.

## Quick start

*   if you do not have
    [Python](https://www.python.org)
    installed, install it.

*   if you do not have
    [Text-Fabric](https://github.com/annotation/text-fabric)
    installed, install it by opening a terminal/command line and saying:

    ``` sh
    pip install 'text-fabric[all]'
    ```

    or, if you have it already, check whether an upgrade is available:

    ``` sh
    pip install --upgrade 'text-fabric[all]'
    ```

*   Start the Text-Fabric browser, from the command line:

    ``` sh
    text-fabric CLARIAH/descartes-tf
    ```

    This will fetch the corpus and open a browser window where you can leaf through the
    texts and make queries. 
    Corpus information and Help are provided in the left side bar.

*   Alternatively, you can work in a Jupyter notebook:

    ``` sh
    pip install jupyterlab
    ```

    ``` sh
    jupyter lab
    ```

    and inside the notebook, in a code cell, run

    ``` python
    from tf.app import use

    A = use('CLARIAH/descartes-tei')
    ```

    which will also download the corpus.

In both cases, the corpus ends up in your home directory,
under `text-fabric-data`.

See also 
[start](https://nbviewer.jupyter.org/github/CLARIAH/descartes-tf/blob/main/tutorial/start.ipynb)
and
[search](https://nbviewer.jupyter.org/github/CLARIAH/descartes-tf/blob/main/tutorial/search.ipynb).

# Author

See [about](docs/about.md) for the authors/editors of the data.

[Dirk Roorda](https://github.com/dirkroorda) is the author of the representation in Text-Fabric of the data,
and the tutorials and documentation.
