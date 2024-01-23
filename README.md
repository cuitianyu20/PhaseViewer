# PhaseViewer
![Author](https://img.shields.io/badge/Author-TianyuCui-blue.svg)
Seismic Phase Viewer with GUI Interface (classify and pick-up phases)

features:
1. GUI interface for seismic phase view and phase pick.
2. raw seismic data or filter data (format: SAC files (*.sac))
3. return comprehensive seismic data information (event_info.csv).

|**analysis for a single signal**    |
|:--------------------------------------------------------------:|
|<img src="https://github.com/cuitianyu20/PhaseViewer/blob/main/src/demo.png" alt="fcwtaudio" width="400"/>|
***

## dependencies
obspy, signal, numpy, pandas, matplotlib, tkinter
***

## 
#### parameters
1. data folder with *sac files;
2. filter: if True, apply bandpass filter (4-order), default: False;
3. filter_freq: min_frequency and max_frequency, default: [1, 3].

***
## example
```bash
    python init_viewer.py
```

