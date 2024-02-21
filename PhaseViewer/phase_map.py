"""
This is part of the Seismic Phase View (SPV) Python Package (PcP and PKiKP phases)
Author: Tianyu Cui
"""

import math
import obspy
import numpy as np  
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from obspy.signal.cross_correlation import correlate_template, xcorr_max
from .utils import predicted_phase_arrival, phase_wave_cut

'''
waveform view and phase pick
'''
def phase_fig(data_wave, ref_model="ak135", filter_data=False, filter_freq=[1, 3], phase_name=["P","PcP","PKiKP"], wave_view_win=[0,1200], view_win=[-30,30], sta_win=[-10, 10], lta_win=[-30, -10], 
              cross_win=[-10, 10], filter_freq_perturb=0.3, filter_freq_min=0.5, filter_freq_max=5, filter_freq_interval=0.05, filter_freq_band_min=0.5):
    # filters test
    def cal_cc_filter(st_tmp, phase_name_tmp, P_wave_yes, arrival_time_tmp, filter_freq, samplate):
        st_tmp.filter('bandpass', freqmin=filter_freq[0], freqmax=filter_freq[1], corners=4, zerophase=True)
        st_tmp.taper(max_percentage=0.05, type='cosine')
        # wave cut
        time_win_list = {"cross_cut": cross_win}
        phase_wave_info = {}
        for key in time_win_list:
            phase_wave_info[key] = phase_wave_cut(st_tmp.copy(), arrival_time_tmp, time_win_list[key])
        # cross correlation between P and PcP or PKiKP
        cross_corr = {}
        if P_wave_yes == 1:
            for phase in phase_name_tmp[1:]:    
                cross_corr[phase] = {}
                cross_corr[phase]['corr_wave'] = correlate_template(phase_wave_info['cross_cut'][phase], phase_wave_info['cross_cut']['P'], mode='full', normalize='naive')
                lag_max, corr_max = xcorr_max(cross_corr[phase]['corr_wave'], abs_max=False)
                corr_lag = signal.correlation_lags(phase_wave_info['cross_cut'][phase].size, phase_wave_info['cross_cut']['P'].size, mode='full')
                cross_corr[phase]['corr_lag'] = corr_lag/samplate
                cross_corr[phase]['lag_max'] = lag_max/samplate
                cross_corr[phase]['corr_max'] = corr_max
        return cross_corr
    # get data information
    def get_data_info(st_data, phase_name_tmp, P_wave_yes, arrival_time, samplate):
        # wave cut
        time_win_list = {"view_cut": view_win, "sta_cut": sta_win, "lta_cut": lta_win, "cross_cut": cross_win}
        wave_cut_times = {}
        for key in time_win_list:
            wave_cut_times[key] = np.arange(time_win_list[key][0], time_win_list[key][1], 1/samplate)
        phase_wave_info = {}
        for key in time_win_list:
            phase_wave_info[key] = phase_wave_cut(st_data.copy(), arrival_time, time_win_list[key])
        # calculate mean, SNR and max amplitude percentage of total data values for each phase
        mean_info = {}
        SNR_info = {}
        amp_percent_info = {}
        for phase in phase_name_tmp:
            mean_info[phase] = np.abs(np.mean(phase_wave_info['view_cut'][phase]))
            # calculate SNR
            noise_power = np.sum(phase_wave_info['lta_cut'][phase]**2)
            signal_power = np.sum(phase_wave_info['sta_cut'][phase]**2)
            SNR_info[phase] = 10 * np.log10(signal_power / noise_power)
            # SNR_info[phase] = np.max(np.abs(phase_wave_info['sta_cut'][phase]))/np.max(np.abs(phase_wave_info['lta_cut'][phase]))
            mag_phase = np.max(phase_wave_info['view_cut'][phase]) - np.min(phase_wave_info['view_cut'][phase])
            mag_total = np.max(st_data[0].data) - np.min(st_data[0].data)
            amp_percent_info[phase] = round(mag_phase/mag_total, 4)
        # cross correlation between P and PcP or PKiKP
        cross_corr = {}
        if P_wave_yes == 1:
            for phase in phase_name_tmp[1:]:    
                cross_corr[phase] = {}
                cross_corr[phase]['corr_wave'] = correlate_template(phase_wave_info['cross_cut'][phase], phase_wave_info['cross_cut']['P'], mode='full', normalize='naive')
                lag_max, corr_max = xcorr_max(cross_corr[phase]['corr_wave'], abs_max=False)
                corr_lag = signal.correlation_lags(phase_wave_info['cross_cut'][phase].size, phase_wave_info['cross_cut']['P'].size, mode='full')
                cross_corr[phase]['corr_lag'] = corr_lag/samplate
                cross_corr[phase]['lag_max'] = lag_max/samplate
                cross_corr[phase]['corr_max'] = corr_max
        return  wave_cut_times, phase_wave_info, mean_info, SNR_info, amp_percent_info, cross_corr
    # plot wave cut
    def ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, phase_special_name, phase_special_color, mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc):
        ax.plot(wave_cut_times['lta_cut'], phase_wave_info['lta_cut'][phase_special_name], color='silver')
        ax.plot(wave_cut_times['sta_cut'], phase_wave_info['sta_cut'][phase_special_name], color=phase_special_color)
        ax.plot(wave_cut_times['view_cut'][int((sta_win[1]-view_win[0])*samplate):], phase_wave_info['view_cut'][phase_special_name][int((sta_win[1]-view_win[0])*samplate):], color='k')
        if np.abs(lta_win[0]) < np.abs(view_win[0]):
            ax.plot(wave_cut_times['view_cut'][:int((lta_win[0]-view_win[0])*samplate)], phase_wave_info['view_cut'][phase_special_name][:int((lta_win[0]-view_win[0])*samplate)], color='k')
        ax.text(view_win[0],ax.get_ylim()[0]*text_loc[0],'MEAN:%.2f'%mean_info[phase_special_name], color=phase_special_color)
        ax.text(view_win[0],ax.get_ylim()[1]*text_loc[1],'SNR:%.2f'%SNR_info[phase_special_name], color=phase_special_color)
        ax.fill_between([lta_win[0],lta_win[1]],ax.get_ylim()[0],ax.get_ylim()[1],facecolor='lightgrey', alpha=0.3)
        ax.set_xlim(view_win)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        return ax
    # filter set information
    def get_filter_set(filter_freq_perturb, filter_freq_min, filter_freq_max, filter_freq_interval, filter_freq_band_min, filter_freq):
        # filter lower and higher corner frequency
        freq_set_low_min = [filter_freq[0]-filter_freq_perturb  if filter_freq[0]-filter_freq_perturb > filter_freq_min else filter_freq_min][0]
        freq_set_low_max = [filter_freq[0]+filter_freq_perturb if filter_freq[0]+filter_freq_perturb < filter_freq_max else filter_freq_max][0]
        freq_set_high_min = [filter_freq[1]-filter_freq_perturb  if filter_freq[1]-filter_freq_perturb > filter_freq_min else filter_freq_min][0]
        freq_set_high_max = [filter_freq[1]+filter_freq_perturb if filter_freq[1]+filter_freq_perturb < filter_freq_max else filter_freq_max][0]
        # print('Scanning lower and higher corner frequency: %.2f hz(%.2f-%.2f hz), %.2fhz (%.2f-%.2fhz)'%\
            # (filter_freq[0], freq_set_low_min, freq_set_low_max, filter_freq[1], freq_set_high_min, freq_set_high_max))
        filter_set_lower = np.arange(freq_set_low_min, freq_set_low_max, filter_freq_interval)
        if freq_set_low_max not in filter_set_lower:
            filter_set_lower = np.append(filter_set_lower, freq_set_low_max)
        filter_set_higher = np.arange(freq_set_high_min, freq_set_high_max, filter_freq_interval)
        if freq_set_high_max not in filter_set_higher:
            filter_set_higher = np.append(filter_set_higher, freq_set_high_max)
        # filter set
        filter_set = [['%.2f'%x, '%.2f'%y] for x in filter_set_lower for y in filter_set_higher if y-x > filter_freq_band_min]
        return filter_set
    # color list
    phase_name = ["P","PcP","PKiKP"]
    phase_color = ['#D21312','#3652AD']
    phase_raw_color = ['#FF6969', '#40A2E3']
    cmap_list = ['Reds', 'Blues']
    # read data
    st = obspy.read(data_wave)
    st_ori = st.copy()
    if filter_data == True:
        st.filter('bandpass', freqmin=filter_freq[0], freqmax=filter_freq[1], corners=4, zerophase=True)
        st.taper(max_percentage=0.05, type='cosine')
    # arrival time
    event_depth = st_ori[0].stats.sac.evdp
    epi_distance = st_ori[0].stats.sac.gcarc
    samplate = st_ori[0].stats.sampling_rate
    arrival_time_data = predicted_phase_arrival(event_depth=event_depth, distance=epi_distance, phase_list=phase_name, ref_model=ref_model)
    P_wave_yes = [1 if 'P' in arrival_time_data.keys() else 0][0]
    if P_wave_yes == 0:
        phase_name = phase_name[1:]
    # filtered data
    wave_cut_times, phase_wave_info, mean_info, SNR_info, amp_percent_info, cross_corr = get_data_info(st, phase_name, P_wave_yes, arrival_time_data, samplate)
    # raw data
    wave_cut_times_ori, phase_wave_info_ori, mean_info_ori, SNR_info_ori, amp_percent_info_ori, cross_corr_ori = get_data_info(st_ori, phase_name, P_wave_yes, arrival_time_data, samplate)
    if filter_data == True and P_wave_yes == 1:
        filter_set = get_filter_set(filter_freq_perturb, filter_freq_min, filter_freq_max, filter_freq_interval, filter_freq_band_min, filter_freq)
        # calculate the predicted arrival time by cross correlation for different filter set
        cc_pred_arrival = []
        for i in range(len(filter_set)):
            cc_info = cal_cc_filter(st_ori.copy(), phase_name, P_wave_yes, arrival_time_data, [float(filter_set[i][0]), float(filter_set[i][1])], samplate)
            cc_pred_arrival.append([cc_info['PcP']['lag_max'], cc_info['PKiKP']['lag_max']])    
        cc_pred_arrival = np.array(cc_pred_arrival)
        # calculate the density of predicted arrival time
        phase_density_list = []
        phase_bins_list = []
        sm_cmap_list = []
        for i in range(2):
            phase_density, phase_bins = np.histogram(cc_pred_arrival[:,i], bins=int(filter_freq_perturb*2/filter_freq_interval), density=True)
            phase_density = phase_density/np.max(phase_density)
            phase_density_list.append(phase_density)
            phase_bins_list.append(phase_bins)
            cmap = plt.get_cmap(cmap_list[i])
            norm = Normalize(vmin=min(phase_density), vmax=max(phase_density))
            cmap_cut = mcolors.LinearSegmentedColormap.from_list("new_cmap", cmap(np.linspace(0.1, 0.8, 256)))
            sm = ScalarMappable(norm=norm, cmap=cmap_cut)
            sm_cmap_list.append(sm)
    # figure plot
    text_loc = [0.7, 0.6]
    fig = plt.figure(figsize=(8.5, 7))
    row_num = 5
    column_num = 2
    arrival_line_width = 1.5
    # row 1: total data
    ax = plt.subplot(row_num, 1, 1)
    ax.plot(st[0].times(), st[0].data, 'k')
    for i,phase in enumerate(phase_name):
        if phase == 'P':
            ax.vlines(arrival_time_data[phase], np.min(st[0].data), np.max(st[0].data), colors='green', linestyles='dashed', label=phase) 
        else:
            ax.text(wave_view_win[0], ax.get_ylim()[i-1]*text_loc[i-1], '%s_Pct:%.2f'%(phase, amp_percent_info[phase]), color='r')
            ax.vlines(arrival_time_data[phase], np.min(st[0].data), np.max(st[0].data), colors=phase_color[i-1], linestyles='dashed', label=phase)
    ax.set_xlim(wave_view_win)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')
    ax.legend(loc='upper right', fontsize=8)
    if P_wave_yes == 1:
        ax.set_title('Event(%s):'%str(st[0].stats.starttime)+' '+st[0].stats.network+'.'+st[0].stats.station+'.'+st[0].stats.channel+' with P arrival')
    else:
        ax.set_title('Event(%s):'%str(st[0].stats.starttime)+' '+st[0].stats.network+'.'+st[0].stats.station+'.'+st[0].stats.channel+' without P arrival')
    # row 2: P phase
    for j in range(column_num):
        # raw data
        if j == 0:
            ax = plt.subplot(row_num, column_num, j+3)
            if P_wave_yes == 1:
                ax_plot_wave_cut(ax,wave_cut_times_ori,phase_wave_info_ori, 'P', 'green',  mean_info_ori, SNR_info_ori, lta_win, sta_win, view_win, samplate, text_loc)
            ax.set_title('Phase: P (raw)')
        # filtered data
        elif j == 1:
            ax = plt.subplot(row_num, column_num, j+3)
            if P_wave_yes == 1:
                ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, 'P', 'green', mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc)
            if filter_data == True:
                ax.set_title('Phase: P (filter: %s-%s Hz)'%(filter_freq[0], filter_freq[1]))
            else:
                ax.set_title('Phase: P (raw)')
    # row 3: PcP, row 4: PKiKP phases, row 5: cross correlation with P phase
    if P_wave_yes == 1:
        phase_name = phase_name[1:]
    else:
        phase_name = phase_name
    row_ini = 5
    for i,phase in enumerate(phase_name):
        for j in range(column_num):
            ax = plt.subplot(row_num, column_num, i+row_ini+j)
            if j == 0:
                ax_plot_wave_cut(ax,wave_cut_times_ori,phase_wave_info_ori, phase, phase_raw_color[i], mean_info_ori, SNR_info_ori, lta_win, sta_win, view_win, samplate, text_loc)
                if P_wave_yes == 1:
                    ax.vlines(cross_corr_ori[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_raw_color[i], linestyles='dashed',linewidths=arrival_line_width, zorder=0)
                ax.set_title('Phase: %s (raw)' % phase)
            elif j == 1:
                ax_plot_wave_cut(ax,wave_cut_times,phase_wave_info, phase, phase_color[i], mean_info, SNR_info, lta_win, sta_win, view_win, samplate, text_loc)
                if P_wave_yes == 1:
                    min_ylim = ax.get_ylim()[0]
                    max_ylim = ax.get_ylim()[1]
                    ax.vlines(cross_corr[phase]['lag_max'], min_ylim, max_ylim, colors=phase_color[i], linestyles='dashed',linewidths=arrival_line_width, zorder=0)
                    ax.vlines(cross_corr_ori[phase]['lag_max'], min_ylim, max_ylim, colors=phase_raw_color[i], linestyles='dashed',linewidths=arrival_line_width, zorder=0)
                    # fill predicted arrival time density
                    if filter_data == True:
                        for k in range(len(phase_bins_list[i])-1):
                            ax.fill_between([phase_bins_list[i][k],phase_bins_list[i][k+1]],min_ylim,max_ylim,
                                            facecolor=sm_cmap_list[i].to_rgba(phase_density_list[i][k]), alpha=0.6, zorder=0)
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
            ax.vlines(cross_corr[phase]['lag_max'], ax.get_ylim()[0], ax.get_ylim()[1], colors=phase_color[i], linestyles='dashed',linewidths=arrival_line_width)
            ax.text(np.min(cross_corr[phase]['corr_lag']), -0.7, 'lag:%.2f s'%cross_corr[phase]['lag_max'], color=phase_color[i])
            ax.text(np.min(cross_corr[phase]['corr_lag']), 0.6, 'corr:%.2f'%cross_corr[phase]['corr_max'], color=phase_color[i])
            ax.set_xlim(-1*math.ceil(np.abs(np.min(cross_corr[phase]['corr_lag']))/10)*10, math.ceil(np.max(cross_corr[phase]['corr_lag'])/10)*10)
            ax.set_ylim(-1, 1)
        ax.set_xlabel('Lag time (s)')
        ax.set_ylabel('Correlation')
        ax.set_title('Cross-correlation (filtered %s-P)'%phase)
    plt.tight_layout()
    # plt.show()
    # plt.savefig('phase_fig_%s_%s.png'%(filter_freq[0], filter_freq[1]))
    return fig, arrival_time_data, phase_wave_info, cross_corr

