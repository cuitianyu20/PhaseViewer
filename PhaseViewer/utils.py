"""
This is part of the Seismic Phase View (SPV) Python Package (PcP and PKiKP phases)
Author: Tianyu Cui
"""

import obspy
from obspy.taup import TauPyModel

'''
return predicted phase arrival time 
'''
def predicted_phase_arrival(event_depth, distance, phase_list, ref_model="ak135"):
    model = TauPyModel(model=ref_model)
    arrival_phase = {}
    arrivals = model.get_travel_times(source_depth_in_km=event_depth, distance_in_degree=distance, phase_list=phase_list)
    for index, arrival in enumerate(arrivals):
        phase_name = arrival.name
        # choose the first arrival time of P arrival
        if phase_name == "P" and index == 0:
            phase_arrival = arrival.time
            arrival_phase[phase_name] = phase_arrival
        elif phase_name == "P" and index != 0:
            continue
        else:
            phase_arrival = arrival.time
            arrival_phase[phase_name] = phase_arrival
    return arrival_phase

'''
return cut data based on predicted phase arrival
'''
def phase_wave_cut(data_raw, arrivals, time_win=[-10, 10]):
    # cut data based on predicted phase arrival
    phase_wave_cut = {}
    for i,phase_name in enumerate(arrivals):
        data = data_raw.copy()[0]
        phase_arrival = arrivals[phase_name]
        samplate = data.stats.sampling_rate
        starttime_cut = obspy.UTCDateTime(data.stats.starttime+phase_arrival+time_win[0])
        endtime_cut = obspy.UTCDateTime(data.stats.starttime+phase_arrival+time_win[1])
        phase_wave_cut[phase_name] = data.data[int((starttime_cut-data.stats.starttime)*samplate):int((endtime_cut-data.stats.starttime)*samplate)]
    return phase_wave_cut

