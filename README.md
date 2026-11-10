# OpenIGTLink-TrackerSimulator

A simple desktop application that acts as a tracker over OpenIGTLink. It replays
recorded tracking data as OpenIGTLink transform messages, so navigation software
such as 3D Slicer can be developed and tested without a physical tracking system.

## Usage

1. Put one CSV file per tracked tool in the `tracker_logs` folder. Each line is
   one 4×4 transform written as 16 comma-separated values, row by row (see
   `tracker_logs/Format.txt`). The file name is used as the transform's device
   name.
2. Run `python TrackerSimulator.py`.
3. Click **Start OpenIGTLink Server** (default port 18934), then **Load Logs**.
4. Click **Start Playback** to stream the transforms at the chosen rate, or use
   the slider to step through them. In 3D Slicer, connect with the
   OpenIGTLinkIF module as a client to receive the transforms.

## Requirements

Python 3 with `numpy`, `PyQt5`, `pyigtl` and `qdarkstyle`.

## License

Distributed under the 3D Slicer license, a BSD-style license. See
[License.txt](License.txt).
