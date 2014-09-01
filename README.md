Overview
========

Iris is the central controller for the entire OGL OCR pipeline. It oversees and
automates the process of converting raw images into citable collections of
digitized texts. Images can be uploaded directly via Iris' RESTful web portal,
or can be selected from preexisting images located on Iris' image repository.
All images and texts processed by Iris are uniquely identifiable and
retrievable through automatically generated URNs which Iris automatically
assigns to everything it processes. In addition, all texts produced by Iris can
be edited or revised concurrently by an arbitrary number of users without data
loss. For more information on Iris' implementation, see docs/schematic.png


Project Structure
=================

- docs: Miscellaneous documentation other than the README.
- iris: The Iris python package
	- web: Contains all code for communicating with the frontend pages, flask routing, etc.
- exts: C extensions
- share: Static, "non binary" files, e.g. images, etc.
- tests: Unit tests.
	- resources: Auxiliary files required by the unit tests.

Build
=====

To build Iris run

```
$ pip install .
```

in the root directory. pip is required to extract the dependencies for
setuptools from the requirements file, so there is no reason the run setup.py
directly.

The image processing C extension requires the leptonica image processing
library (>=1.70, available from Debian Jessie):

```
$ apt-get install libleptonica-dev
```

If a manual install is required, don't forget to install the apropriate image
format libraries and their headers (libtiff, libpng, libjpeg) or run:

```
$ apt-get build-dep leptonlib
```

Tests
=====

```
$ setup.py test
```

As mentioned above pip has to be installed.


Running
=======

First edit celeryconfig.py and irisconfig.py to fit your needs. Running a
distributed cluster requires a shared storage medium (e.g. NFS) on all nodes. Then start up the celery daemon with something like:

```
$ celery -A iris.tasks worker
```

Right now there isn't an easy to use script available. Core functionality is
exposed by the ''batch'' function of the iris package:

```
>>> import iris
>>> iris.batch({'batch_id': '1234', 'input_files': [u'input.tiff'], 'actions': [[{'method': 'rgb_to_gray'}], [{'method':'binarize', 'thresh': 10}, {'method': 'binarize', 'thresh': 5}], [{'method': 'ocr_tesseract', 'languages': ['eng']}]]})
<GroupResult: 6222f675-330e-461c-94de-1d0ea0a2f444 [0cb9c912-1818-43d3-afd4-9f66e0b9b6f0, c47729a6-cbd6-4882-bec1-73f52400f6d9]>
```

The (absolute) path of the final output is contained in the result field of the subtasks.


Issues
======

* Currently the distributed storage medium has to be mounted in the same
  location on each node. This is caused by the missing conversion of absolute
  paths into storage module format (id, doc tuples).
