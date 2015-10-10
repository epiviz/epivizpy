EpivizPy
=====

The repository contains base code for Python integration with the Epiviz tool. 
It also contains a demo that exemplifies usage and potential extension. 

**A different demo with real world data can be found in the ```demo``` branch**

Running the Demo
-----

(Optional) Open project using Eclipse PyDev

### Dependencies:

* **Python 2.7**
* `pip install simplejson`
* `pip install tornado`
* `pip install enum`
* (For the `demo` branch: `pip install pandas`)

Launch ```main.py```

Open Epiviz to visualize the data: [http://epiviz.cbcb.umd.edu/?websocket-host[]=ws://localhost:8888/ws&settings=default&](http://epiviz.cbcb.umd.edu/?websocket-host[]=ws://localhost:8888/ws&settings=default&)

Type the following commands in the command line to see the demo at work:

```addMeasurements``` will add a mock measurement to Epiviz. You can type this command several times, 
and each time a new measurement will be added. (The measurements have the *Default chart* set to *Line 
Track* and they are prefixed with ```Python Measurement```.)

```removeMeasurements``` will remove the last mock measurement added. If no measurement has been added through EpivizPy, nothing will happen.

```addChart``` once at least one measurement has been added through EpivizPy, this command will add a new *Line Track* to the workspace, showing
that measurement.

```removeChart``` removes the last chart added using EpivizPy

```getCurrentLocation``` queries Epiviz for the current genomic location of the workspace.

```navigate``` can only be called after calling ```getCurrentLocation```. Causes Epiviz to navigate right.

```redraw``` causes Epiviz to redraw all charts.

## Known issues

On Windows, when running `pip install pandas`, you get the following error:

```
Command "C:\Python27\python.exe -c "import setuptools, tokenize;_file__='c:\\users\\mms\\appdata\\local\\temp\\pip-build-v8ycdd\\numpy\\setup.py';exec(compile(getattr(tokenize, 'open', open)(__file_).read().replace('\r\n', '\n'), _file_, 'exec'))" install --record c:\users\mms\appdata\local\temp\pip-n35ir4-record\install-record.txt --single-version-externally-managed --compile" failed with error code 1 in c:\users\mms\appdata\local\temp\pip-build-v8ycdd\numpy
```

This is a known problem with Python in Windows. The solution, as outlined in [this post](http://shop.wickeddevice.com/2013/12/11/windows-7-python-virtualenv-and-the-unable-to-find-vcvarsall-bat-error/) is:

1. 	Make sure you are running **Python 2.7 (32 Bit version)**
2. 	Install visual c++ 2008: http://go.microsoft.com/?linkid=7729279 (pip needs the C++ compiler from this version of Visual Studio; **newer versions will not work!**
3. 	Now for the even more annoying part: open `regedit` (Windows Start button > type `regedit` <enter>); find the following key path: `HKEY_LOCAL_MACHINE\Software\Wow6432Node\Microsoft\VisualStudio\9.0\Setup\VC` (on a 64 bit Windows). If any of those keys does not exist, create them. 
4. 	Right-click on the `VC` key, and select `New > String value`. The name should be `ProductDir`, and the value, the directory location of `vcvarsall.bat` (for example: `c:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\`).
5. 	Open command prompt **with administrator privileges**, go to `c:\Python27\Scripts` (or your corresponding location of the Python 2.7 installation), and run `pip install pandas` again. This may take a long time but should not fail this time.
 	

