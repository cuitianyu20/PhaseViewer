"""
This is part of the Seismic Phase View (SPV) Python Package (PcP and PKiKP phases)
Author: Tianyu Cui
"""

import math
import obspy
import numpy as np  
from scipy import signal
import matplotlib.pyplot as plt
from obspy.signal.cross_correlation import correlate_template, xcorr_max
from .utils import predicted_phase_arrival, phase_wave_cut


'''
waveform view and phase pick
'''
def phase_fig(data_wave, ref_model="ak135", filter_data=False, filter_freq=[1, 3], phase_name=["P","PcP","PKiKP"], wave_view_win=[0,1200], view_win=[-30,30], sta_win=[-10, 10], lta_win=[-30, -10], cross_win=[-10, 10]):
    
    def get_data_info(st):
        event_depth = st[0].stats.sac.evdp
        epi_distance = st[0].stats.sac.gcarc
        samplate = st[0].stats.sampling_rate
        # arrival time
        arrival_time = predicted_phase_arrival(event_depth=event_depth, distance=epi_distance, phase_list=phase_name, ref_model=ref_model)
        if 'P' not in arrival_time.keys():
            if 'P' in phase_name:
                phase_name.remove('P')
            P_wave_yes = 0
        else:
            P_wave_yes = 1
        # wave cut
        time_win_list = {"view_cut": view_win, "sta_cut": sta_win, "lta_cut": lta_win, "cross_cut": cross_win}
        wave_cut_times = {}
        for key in time_win_list:
            wave_cut_times[key] = np.arange(time_win_list[key][0], time_win_list[key][1], 1/samplate)
        phase_wave_info = {}
        for key in time_win_list:
            phase_wave_info[key] = phase_wave_cut(st.copy(), arrival_time, time_win_list[key])
        # calculate mean, SNR and max amplitude percentage of total data values for each phase
        mean_info = {}
        SNR_info = {}
        amp_percent_info = {}
        for phase in phase_name:
            mean_info[phase] = np.abs(np.mean(phase_wave_info['view_cut'][phase]))
            # calculate SNR
            noise_power = np.sum(phase_wave_info['lta_cut'][phase]**2)
            signal_power = np.sum(phase_wave_info['sta_cut'][phase]**2)
            SNR_info[phase] = 10 * np.log10(signal_power / noise_power)
            # SNR_info[phase] = np.max(np.abs(phase_wave_info['sta_cut'][phase]))/np.max(np.abs(phase_wave_info['lta_cut'][phase]))
            mag_phase = np.max(phase_wave_info['view_cut'][phase]) - np.min(phase_wave_info['view_cut'][phase])
            mag_total = np.max(st[0].data) - np.min(st[0].data)
            amp_percent_info[phase] = round(mag_phase/mag_total, 4)
        # cross correlation between P and PcP or PKiKP
        cross_corr = {}
        if P_wave_yes == 1:
            for phase in phase_name[1:]:    
                cross_corr[phase] = {}
                cross_corr[phase]['corr_wave'] = correlate_template(phase_wave_info['cross_cut'][phase], phase_wave_info['cross_cut']['P'], mode='full', normalize='naive')
                lag_max, corr_max = xcorr_max(cross_corr[phase]['corr_wave'], abs_max=False)
                corr_lag = signal.correlation_lags(phase_wave_info['cross_cut'][phase].size, phase_wave_info['cross_cut']['P'].size, mode='full')
                cross_corr[phase]['corr_lag'] = corr_lag/samplate
                cross_corr[phase]['lag_max'] = lag_max/samplate
                cross_corr[phase]['corr_max'] = corr_max
        return arrival_time, wave_cut_times, phase_wave_info, mean_info, SNR_info, amp_percent_info, cross_corr, P_wave_yes


    def ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, phase_special_name, phase_special_color, backgroud_color, mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc):
        ax.plot(wave_cut_times['lta_cut'], phase_wave_info['lta_cut'][phase_special_name], color='silver')
        ax.plot(wave_cut_times['sta_cut'], phase_wave_info['sta_cut'][phase_special_name], color=phase_special_color)
        ax.plot(wave_cut_times['view_cut'][int((sta_win[1]-view_win[0])*samplate):], phase_wave_info['view_cut'][phase_special_name][int((sta_win[1]-view_win[0])*samplate):], color='k')
        if np.abs(lta_win[0]) < np.abs(view_win[0]):
            ax.plot(wave_cut_times['view_cut'][:int((lta_win[0]-view_win[0])*samplate)], phase_wave_info['view_cut'][phase_special_name][:int((lta_win[0]-view_win[0])*samplate)], color='k')
        ax.text(view_win[0],ax.get_ylim()[0]*text_loc[0],'MEAN:%.2f'%mean_info[phase_special_name], color=phase_special_color)
        ax.text(view_win[0],ax.get_ylim()[1]*text_loc[1],'SNR:%.2f'%SNR_info[phase_special_name], color=phase_special_color)
        ax.fill_between([sta_win[0],sta_win[1]],ax.get_ylim()[0],ax.get_ylim()[1],facecolor=backgroud_color, alpha=0.3)
        ax.fill_between([lta_win[0],lta_win[1]],ax.get_ylim()[0],ax.get_ylim()[1],facecolor='lightgrey', alpha=0.3)
        ax.set_xlim(view_win)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        return ax
        
    phase_name = ["P","PcP","PKiKP"]
    # label color list
    phase_color = ['red', 'blue']
    # read data
    st = obspy.read(data_wave)
    st_ori = st.copy()
    if filter_data == True:
        st.filter('bandpass', freqmin=filter_freq[0], freqmax=filter_freq[1], corners=4, zerophase=True)
        st.taper(max_percentage=0.05, type='cosine')
    # filter data
    arrival_time, wave_cut_times, phase_wave_info, mean_info, SNR_info, amp_percent_info, cross_corr, P_wave_yes = get_data_info(st)
    samplate = st[0].stats.sampling_rate
    # original data
    arrival_time_ori, wave_cut_times_ori, phase_wave_info_ori, mean_info_ori, SNR_info_ori, amp_percent_info_ori, cross_corr_ori, P_wave_yes_ori = get_data_info(st_ori)

    # figure plot
    text_loc = [0.7, 0.6]
    fig = plt.figure(figsize=(8.5, 7))
    row_num = 5
    column_num = 2
    # row 1: total data
    ax = plt.subplot(row_num, 1, 1)
    ax.plot(st[0].times(), st[0].data, 'k')
    for i,phase in enumerate(phase_name):
        if phase == 'P':
            ax.vlines(arrival_time[phase], np.min(st[0].data), np.max(st[0].data), colors='green', linestyles='dashed', label=phase) 
        else:
            ax.text(wave_view_win[0], ax.get_ylim()[i-1]*text_loc[i-1], '%s_Pct:%.2f'%(phase, amp_percent_info[phase]), color='r')
            ax.vlines(arrival_time[phase], np.min(st[0].data), np.max(st[0].data), colors=phase_color[i-1], linestyles='dashed', label=phase)
    ax.set_xlim(wave_view_win)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.legend(loc='upper right')
    if P_wave_yes == 1:
        ax.set_title('Event(%s):'%str(st[0].stats.starttime)+' '+st[0].stats.network+'.'+st[0].stats.station+'.'+st[0].stats.channel+' with P arrival')
    else:
        ax.set_title('Event(%s):'%str(st[0].stats.starttime)+' '+st[0].stats.network+'.'+st[0].stats.station+'.'+st[0].stats.channel+' without P arrival')
    # row 2: P phase
    for j in range(column_num):
        # filtered data
        if j == 0:
            ax = plt.subplot(row_num, column_num, j+3)
            if P_wave_yes_ori == 1:
                ax_plot_wave_cut(ax,wave_cut_times_ori,phase_wave_info_ori, 'P', 'green', 'lightgreen', mean_info_ori, SNR_info_ori, lta_win, sta_win, view_win, samplate, text_loc)
            ax.set_title('Phase: P (raw)')
        # raw data
        elif j == 1:
            ax = plt.subplot(row_num, column_num, j+3)
            if P_wave_yes == 1:
                ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, 'P', 'green', 'lightgreen', mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc)
            if filter_data == True:
                ax.set_title('Phase: P (filter: %s-%s Hz)'%(filter_freq[0], filter_freq[1]))
            else:
                ax.set_title('Phase: P (raw)')
    # row 3: PcP, row 4: PKiKP phases, row 5: cross correlation with P phase
    fill_color = ['salmon','lightblue']
    phase_ori_color = ['#E58A8A', '#00BCD4']
    if P_wave_yes == 1:
        phase_name = phase_name[1:]
    else:
        phase_name = phase_name
    row_ini = 5
    for i,phase in enumerate(phase_name):
        for j in range(column_num):
            ax = plt.subplot(row_num, column_num, i+row_ini+j)
            if j == 0:
                ax_plot_wave_cut(ax,wave_cut_times_ori,phase_wave_info_ori, phase, phase_color[i], fill_color[i], mean_info_ori, SNR_info_ori, lta_win, sta_win, view_win, samplate, text_loc)
                if P_wave_yes_ori == 1:
                    ax.vlines(cross_corr_ori[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_ori_color[i], linestyles='dashed')
                ax.set_title('Phase: %s (raw)' % phase)
            elif j == 1:
                ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, phase, phase_color[i], fill_color[i], mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc)
                if P_wave_yes == 1:
                    ax.vlines(cross_corr[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_color[i], linestyles='dashed')
                    ax.vlines(cross_corr_ori[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_ori_color[i], linestyles='dashed')
                if filter_data == True:
                    ax.set_title('Phase: %s (filter: %s-%s Hz)'%(phase, filter_freq[0], filter_freq[1]))
                else:
                    ax.set_title('Phase: %s (raw)' % phase)
        row_ini += 1
    row_ini = 9
    for i,phase in enumerate(phase_name):
        ax = plt.subplot(row_num, column_num, i+row_ini)
        if P_wave_yes == 1:
            ax.plot(cross_corr[phase]['corr_lag'], cross_corr[phase]['corr_wave'], color='k')
            ax.vlines(cross_corr[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_color[i], linestyles='dashed')
            ax.text(np.min(cross_corr[phase]['corr_lag']), -0.7, 'lag:%.2f s'%cross_corr[phase]['lag_max'], color=phase_color[i])
            ax.text(np.min(cross_corr[phase]['corr_lag']), 0.6, 'corr:%.2f'%cross_corr[phase]['corr_max'], color=phase_color[i])
            ax.set_xlim(-1*math.ceil(np.abs(np.min(cross_corr[phase]['corr_lag']))/10)*10, math.ceil(np.max(cross_corr[phase]['corr_lag'])/10)*10)
            ax.set_ylim(-1, 1)
        ax.set_xlabel('Lag time (s)')
        ax.set_ylabel('Correlation')
        ax.set_title('Cross-correlation (filtered %s-P)'%phase)
    plt.tight_layout()
    return fig, arrival_time, phase_wave_info, cross_corr

