# PhaseViewer
![Author](https://img.shields.io/badge/Author-TianyuCui-blue.svg)

Seismic Phase Viewer with GUI Interface (classify and pick-up phases)


## features:
1. GUI interface for seismic phase view and phase pick.
2. raw seismic data or filter data (format: SAC files (*.sac))
3. return comprehensive seismic data information (event_info.csv).


|**PcP and PKiKP phase viewer**    |
|:--------------------------------------------------------------:|
|<img src="https://github.com/cuitianyu20/PhaseViewer/blob/main/src/demo.png" alt="fcwtaudio" width="400"/>|
***

## dependencies
obspy, signal, numpy, pandas, matplotlib, tkinter
***

## parameters setting
### 1. para in code
```python

    1. data folder with *sac files;
    2. filter: if True, apply bandpass filter (4-order), default: False;
    3. filter_freq: min_frequency and max_frequency, default: [1, 3].
    4. event_info: load ever processed event info file (format:csv) for processing same data
    5. output file name : *csv file

```
### 2. para in final event_info.csv
```python

    event_wave: seismic waveform data name
    PcP_classify: PcP phase classification result (0: no PcP; 1: PcP)
    PKiKP_classify: PKiKP phase classification result (0: no PKiKP; 1: PKiKP)
    PcP_predic_pick: PcP phase predicted pick time (unit: second)
    PKiKP_predic_pick: PKiKP phase predicted pick time (unit: second)
    PcP_manual_pick: PcP phase manual pick time (unit: second)
    PKiKP_manual_pick: PKiKP phase manual pick time (unit: second)
    PcP_cc_pcik: PcP phase cross-correlation pick time (unit: second)
    PKiKP_cc_pick: PKiKP phase cross-correlation pick time (unit: second)
    PcP_cc_max: PcP phase cross-correlation coefficient
    PKiKP_cc_max: PKiKP phase cross-correlation coefficient
    PcP_wave: PcP phase waveform cut data
    PKiKP_wave: PKiKP phase waveform cut data
    PcP_cc_wave: PcP phase cross-correlation waveform cut data
    PKiKP_cc_wave: PKiKP phase cross-correlation waveform cut data

```

## example
```bash
    python init_viewer.py
```

