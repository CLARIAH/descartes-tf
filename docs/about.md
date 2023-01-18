# Source

The
[complete letters of Descartes](http://emlo-portal.bodleian.ox.ac.uk/collections/?catalogue=rene-descartes)
have been converted to Text-Fabric in 2 stages:

* During the
  [CKCC project in 2011](https://ckcc.huygens.knaw.nl), from ASCII to TEI;
* At the [Humanities Cluster](https://di.huc.knaw.nl/text-analysis-en.html), in 2023, from TEI to Text-Fabric.

## From ASCII to TEI

The source data
[JapAM.txt](https://github.com/CLARIAH/descartes-tei/tree/master/2012-01-17/data)
is a file created in 1998 by

* Katsuzo Murakami (University of Tokyo)
* Meguru Sasaki (École normale superieure d'Hokkaido)
* Takehumi Tokoro (University of Chyuo) 1998

This file is in a private ASCII encoding using characters 32-254, with identifier JAPAM.txt.

It was received on CD by Erik-Jan Bos and in 2011 converted by

* Erik-Jan Bos, then [Descartes Centre, University of Utrecht](http://www.descartescentre.com>)
* Dirk Roorda, then [Data Archiving and Networked Services (DANS)](http://www.dans.knaw.nl/en>)

The conversion result (file
[JapAM-EJB-DR.xml](https://github.com/CLARIAH/descartes-tei/tree/master/result)
is XML-TEI.

The
[illustrations](https://github.com/CLARIAH/descartes-tf/tree/main/source/illustrations)
are taken from *Oeuvres de Descartes, 11 vols.,*,
editor: Charles Adam et Paul Tannery, Paris, Vrin, 1896-1911.

More information about this conversion is in this 
[report](https://github.com/CLARIAH/descartes-tei/blob/master/docs/convert.md).

## From TEI to Text-Fabric

Because of the srtructured nature of TEI it was not very difficult or time consuming to
migrate the result further to
[Text-Fabric](https://github.com/annotation/text-fabric).

Text-Fabric is a tool that helps to make a corpus representation suitable for computing.
It can be used in Jupyter notebooks and it has a built-in corpus browser.
Both interfaces

* make use of a search engine that can look for structural patterns;
* support the display of illustrations and mathematical formulas.

All in all this results in a tool by which users can research this
corpus in a self-contained way on their own computer.

See [transcription](transcription.md) for how the features of the TF data are defined.

# Authors 

* [Erik-Jan Bos](https://nl.linkedin.com/in/erik-jan-bos-001)
  Expert on Descartes and his works.
  Found the source data, supplied additional metadata from his own database.
* [Dirk Roorda](https://pure.knaw.nl/portal/en/persons/dirk-roorda)
  Expert in text-conversion, wrote Text-Fabric.
