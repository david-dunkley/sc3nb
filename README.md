# sc3nb

sc3nb is a python package that offers a SuperCollider3 (sc3)interface, with special support to be used within jupyter notebooks.
It establishes shortcuts and familiar functions used by sc3 to make it easier to program and interactively try sound synthesis, and for sonification development.

  * Documentation: https://interactive-sonification.github.io/sc3nb
  * Source code: https://github.com/interactive-sonification/sc3nb
  * Bug reports: https://github.com/interactive-sonification/sc3nb/issues

It provides:
  * helper functions such as linlin, cpsmidi, midicps, clip, ampdb, dbamp which work like their sc3 counterparts.
  * SC - a class to interface with sc3 (both sclang and scsynth)
  * Buffer - a class to administer buffers, fill them with numpy arrays, transfer sc3 buffers to numpy arrays, etc.
  * SynthDef - a class to support the creation and context-specific manipulation of synthesizer definitions via sclang to scsynth
  * Synth - a class to create an instance of a synth, update it and free it
  * TimedQueue - a class to enable timed execution of methods, which is useful for playing larger scores in synchronization with real-time plotting.
  * (more classes to be added as needed)

sc3nb can be used for
* multi-channel audio processing
* auditory display and sonification
* sound synthesis experiment
* audio applications in general such as games or GUI-enhancements
* signal analysis and plotting
* computer music and just-in-time music control
* any usecase that the SuperCollider 3 language supports

For more information and examples, please read the documentation.

## Installation

**Disclaimer**: We are currently making sure that sc3nb can be uploaded to PyPI, until then - or if you prefer a manual installation - clone the master branch and from inside the sc3nb directory install via
```bash
pip install -e .
```

This will install the library in development mode (i.e. changes to sc3nb code will automatically be "re-installed").
For more information, please refer to the documentation.


## A simple example

### Startup:

    import sc3nb as scn
    sc = scn.startup()  # this boots the server and returns the SC class instance

In Jupyter notebooks, use the cell magic `%sc` to directly write one-line sc3 code

    %sc Synth.new(\default)

Stop the synth via CMD-. (registered jupyter shortcut), or use

    %sc s.freeAll

The %sc shortcut is now the same as the %scv magic, a verbose version which inlines the sc3 output in the jupyter output cell. Suppress the output by using the %scs magic.

Cell magic work in between python code, e.g.

    %sc x = Synth.new(\default, [\freq, 100])
    for p in range(1, 10):  # a bouncing ball
        time.sleep(1/p)
        %scs Synth.new(\s1, [\freq, 200]) // %sc line so sc3 comments instead of #
    %sc x.free

Create an sc3 cell with the cell magic %%sc resp. %%scv or %%scs.
For example, to create an osc responder

    %%scv
    OSCdef(\dinger, { | msg, time, addr, recvPort |
        var freq = msg[2];
        {Pulse.ar(freq, 0.04, 0.3)!2 * EnvGen.ar(Env.perc, doneAction:2)}.play
    }, '/ding')

and trigger it like this:

    for i in range(100):
        sc.server.msg("/ding", ["freq", 1000-5*i], receiver="sclang")
