EpivizPy
=====

The repository contains base code for Python integration with the Epiviz tool. 
It also contains a demo that exemplifies usage and potential extension. 

**A different demo with real world data can be found in the ```demo``` branch**

Running the Demo
-----

(Optional) Open project using Eclipse PyDev

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

