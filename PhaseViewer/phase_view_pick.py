import os
import glob 
import obspy
import pandas as pd
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from .phase_map import phase_fig

"""
GUI for seismic phase view and pick-up
"""
class Phaseviewer:
    # initialize
    def __init__(self, datafolder, folder_order=1, filter=False, filter_freq=[1, 3], filter_corner=4, zerophase=False, filter_freq_perturb=0.3, filter_freq_min=0.5, filter_freq_max=5.0, 
                 filter_freq_interval=0.05, filter_freq_band_min=0.5, event_info=None, skip_load_event=False, sort_by_dis=True, correct_current_data=False, cross_win=[-8,8], view_win=[-8,8],
                 cc_min=0.4, output_file='event_info.csv'):
        print("==========================================================================")
        print("===================  Welcome to Seismic Phase Viewer!  ===================")
        print("===================  Usage:                            ===================")
        print("===================  1. Left signle click: classify phases ===============")
        print("===================  2. Left double click: pick-up phases  ===============")
        print("===================  3. Leave and save result: click 'Quit' button =======")
        print("==========================================================================")
        master = tk.Tk()
        master.geometry("930x930")
        if event_info is not None:
            # load event info
            self.event_info_file = 1
            self.event_info = pd.read_csv(event_info,usecols=range(15)).values.tolist()
        else:
            self.event_info_file = 0
            self.event_info = []
        self.master = master
        self.master.title("Seismic Phase Viewer")
        # skip load event info
        self.skip_load_event = skip_load_event
        # self.file folder path
        self.data_folder_path = datafolder
        if correct_current_data:
            try:
                self.data_files = pd.read_csv(event_info,usecols=range(15))['event_wave'].tolist()
            except:
                raise ValueError('Please load the correct event info file!!!')
        else:
            if folder_order == 1:
                self.data_files = glob.glob(self.data_folder_path + "/*.sac")
                if sort_by_dis:
                    dis_list = [obspy.read(data)[0].stats.sac.gcarc for data in self.data_files ]
                    self.data_files = [x for _,x in sorted(zip(dis_list,self.data_files))]
            elif folder_order == 2:
                event_list = sorted(list(set([data.split('/')[-2] for data in glob.glob(self.data_folder_path + "/*/*.sac")])))
                self.data_files = []
                for event in event_list:
                    event_files = sorted(glob.glob(self.data_folder_path + "/" + event + "/*.sac"))
                    if sort_by_dis:
                        dis_list = []
                        for data in event_files:
                            try:
                                st_data = obspy.read(data)
                                dis_list.append(st_data[0].stats.sac.gcarc)
                            except:
                                print('Error load and remove: %s' % data)
                                os.system("rm " + data)
                                continue
                        # dis_list = [obspy.read(data)[0].stats.sac.gcarc for data in event_files ]
                        event_files = [x for _,x in sorted(zip(dis_list,event_files))]
                    self.data_files += event_files
            else:
                raise ValueError('Folder order error!!!')
        if len(self.data_files) == 0:
            raise ValueError('No sac file in the folder!!!')
        # time window
        self.cross_win = cross_win
        self.view_win = view_win
        # filter data
        self.filter = filter
        self.filter_freq = filter_freq
        self.filter_freq_perturb = filter_freq_perturb
        self.filter_freq_min = filter_freq_min
        self.filter_freq_max = filter_freq_max
        self.filter_freq_interval = filter_freq_interval
        self.filter_freq_band_min = filter_freq_band_min
        self.filter_corner = filter_corner
        self.zerophase = zerophase
        # data index
        self.index = 0
        # minimum cross correlation value
        self.cc_min = cc_min
        # correct index
        self.correct_index = 0
        # output data name
        self.output_file = output_file
        # phase
        self.P_classify = 0
        self.PcP_classify = 0
        self.PKiKP_classify = 0
        self.P_pick = 0
        self.PcP_pick = 0
        self.PKiKP_pick = 0
        self.P_pick_tmp = 0
        self.PcP_pick_tmp = 0
        self.PKiKP_pick_tmp = 0
        # correct phase pick-up
        self.correct_flag = False
        # load data
        if self.index < len(self.data_files):
            if self.index == 0 and self.event_info_file == 1:
                if self.data_files[self.index] == self.event_info[0][0]:
                    print('Success: load event info!!!')
                    # skip to the record index
                    if self.skip_load_event:
                        self.index = len(self.event_info) - 1
                        
                        print('Skip to the record index: %s' % self.event_info[-1][0])
                    # load event info
                    self.load_event_info()
                else:
                    print('Error: load event info error!!!')
                    print("Alert: event info file is not match with the data file!!!")
                    self.event_info = []
        # drop data
        self.drop_data_flag = 0
        # initial figure
        self.plot_figure()
        # mainloop
        tk.mainloop()

    # plot seismic phases for the next data self.file
    def plot_figure(self, correct_flag=False, correct_pick=[0, 0, 0], cc_cal=False):
        file_path = self.data_files[self.index]        
        try:
            if cc_cal == False:
                self.fig, self.travel_times, self.phase_wave, self.cross_corr = phase_fig(data_wave=file_path, filter_data=self.filter, filter_freq=self.filter_freq, filter_corner=self.filter_corner, 
                                                                                        zerophase=self.zerophase, filter_freq_perturb=self.filter_freq_perturb, filter_freq_min=self.filter_freq_min, 
                                                                                        filter_freq_max=self.filter_freq_max, filter_freq_interval=self.filter_freq_interval, cross_win=self.cross_win, 
                                                                                        view_win=self.view_win, filter_freq_band_min=self.filter_freq_band_min,correct_flag=correct_flag,correct_pick=correct_pick,
                                                                                        return_cc=cc_cal)
            else:
                self.travel_times, self.phase_wave, self.cross_corr = phase_fig(data_wave=file_path, filter_data=self.filter, filter_freq=self.filter_freq, filter_corner=self.filter_corner, 
                                                                                zerophase=self.zerophase, filter_freq_perturb=self.filter_freq_perturb, filter_freq_min=self.filter_freq_min, 
                                                                                filter_freq_max=self.filter_freq_max, filter_freq_interval=self.filter_freq_interval, cross_win=self.cross_win, 
                                                                                view_win=self.view_win, filter_freq_band_min=self.filter_freq_band_min,correct_flag=correct_flag,correct_pick=correct_pick,
                                                                                return_cc=cc_cal)
            self.wave_data_fig = True
            # if cross correlation value is less than cc_min
            self.cc_min_flag = False
            # predicted phase arrival
            self.PcP_predic_pick = self.travel_times['PcP']
            self.PKiKP_predic_pick = self.travel_times['PKiKP']
            # phase wave cut
            self.PcP_wave = self.phase_wave['view_cut']['PcP']
            self.PKiKP_wave = self.phase_wave['view_cut']['PKiKP']
            if ('P' not in self.travel_times.keys()):
                if cc_cal == False:
                    print('%s : no P arrival.' % self.data_files[self.index])
                # phase cross correlation
                self.P_predic_pick = 0
                self.PcP_cc_wave = 0 
                self.PKiKP_cc_wave = 0
                self.PcP_cc_max = 0
                self.PKiKP_cc_max = 0
                self.PcP_cc_lag = 0
                self.PKiKP_cc_lag = 0
                self.cc_min_flag = True
            else:
                self.P_predic_pick = self.travel_times['P']
                # phase cross correlation
                self.PcP_cc_wave = self.cross_corr['PcP']['corr_wave']
                self.PKiKP_cc_wave = self.cross_corr['PKiKP']['corr_wave']
                self.PcP_cc_max = self.cross_corr['PcP']['corr_max']
                self.PKiKP_cc_max = self.cross_corr['PKiKP']['corr_max']
                if self.PcP_cc_max > self.cc_min or self.PKiKP_cc_max > self.cc_min:
                    self.cc_min_flag = True
                else:
                    self.cc_min_flag = False
                self.PcP_cc_lag = self.cross_corr['PcP']['lag_max']
                self.PKiKP_cc_lag = self.cross_corr['PKiKP']['lag_max']
            if self.correct_flag:
                self.P_pick_tmp += self.P_pick
                self.PcP_pick_tmp += self.PcP_pick
                self.PKiKP_pick_tmp += self.PKiKP_pick
                self.P_pick = 0
                self.PcP_pick = 0
                self.PKiKP_pick = 0
                self.cc_min_flag = True
        except ValueError as e:
            self.wave_data_fig = False
            self.fig = plt.figure(figsize=(10, 8))
            print('Error: load error (%s:%s)' % (self.data_files[self.index], e))
        if cc_cal == False:
            self.embed_fig_in_tkinter(self.fig)
            self.canvas.draw()


    # embed Matplotlib figure into Tkinter window
    def embed_fig_in_tkinter(self, fig):
        # create container for Matplotlib figure
        self.canvas_container = tk.Frame(self.master)
        self.canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # embed fig object into Tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        # toolbar for seismic phase view
        toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_container)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.CENTER, expand=True)
        # buttons and labels
        self.canvas_label = tk.Frame(self.master)
        self.canvas_label.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        self.canvas_button = tk.Frame(self.master)
        self.canvas_button.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)
        # next button
        next_button = tk.Button(self.canvas_button, text=" Next", command=self.plot_next_data)
        next_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=5)
        # Last button
        last_button = tk.Button(self.canvas_button, text="Last ", command=self.plot_last_data)
        last_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=5)
        # drop button
        drop_button = tk.Button(self.canvas_button, text="Drop ", command=self.drop_data)
        drop_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        # drop value
        self.drop_data_value = tk.Label(self.canvas_button, text='yes' if self.drop_data_flag==1 else 'no ')
        self.drop_data_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # phase classification button
        P_class_button = tk.Button(self.canvas_button, text="  P  ", command=lambda: self.phases_classify(1))
        P_class_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        self.P_classify_value = tk.Label(self.canvas_button, text='yes' if self.P_classify==1 else ' no')
        self.P_classify_value.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # correct figure button
        correct_button = tk.Button(self.canvas_button, text="  Correct ", command=self.correct_phase_pick)
        correct_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        # pick-up P button
        P_pick_button = tk.Button(self.canvas_button, text="  P Pick  ", command=lambda: self.phase_pick(1))
        P_pick_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        # P value
        self.P_pick_value = tk.Label(self.canvas_button, text='=%.3f s'%self.P_pick if self.P_pick >=0 else '=%.3fs'%self.P_pick)
        self.P_pick_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # reset button
        reset_button = tk.Button(self.canvas_label, text="Reset", command=self.reset_view)
        reset_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=10)
        # quit button
        quit_button = tk.Button(self.canvas_label, text=" Quit", command=self._quit)
        quit_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=10)
        # phase classification button
        PcP_class_button = tk.Button(self.canvas_label, text=" PcP ", command=lambda: self.phases_classify(2))
        PcP_class_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        self.PcP_classify_value = tk.Label(self.canvas_label, text='yes' if self.PcP_classify==1 else 'no ')
        self.PcP_classify_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        PKiKP_class_button = tk.Button(self.canvas_label, text="PKiKP", command=lambda: self.phases_classify(3))
        PKiKP_class_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        self.PKiKP_classify_value = tk.Label(self.canvas_label, text='yes' if self.PKiKP_classify==1 else ' no')
        self.PKiKP_classify_value.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # pick-up PcP button
        PcP_pick_button = tk.Button(self.canvas_label, text=" PcP Pick ", command=lambda: self.phase_pick(2))
        PcP_pick_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        # PcP value
        self.PcP_pick_value = tk.Label(self.canvas_label, text='=%.3f s'%self.PcP_pick if self.PcP_pick >=0 else '=%.3fs'%self.PcP_pick)
        self.PcP_pick_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # pick-up PKiKP button
        PKiKP_class_button = tk.Button(self.canvas_label, text="PKiKP Pick", command=lambda: self.phase_pick(3))
        PKiKP_class_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=10)
        # # PKiKP value
        self.PKiKP_pick_value = tk.Label(self.canvas_label, text='s %.3f='%self.PKiKP_pick if self.PKiKP_pick >=0 else 's%.3f='%self.PKiKP_pick)
        self.PKiKP_pick_value.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=5, pady=5)
        # Last event button
        last_event_button = tk.Button(self.canvas_button, text="Last Event", command=self.last_event)
        last_event_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=17, pady=10)
        # next event button
        next_event_button = tk.Button(self.canvas_label, text="Next Event", command=self.next_event)
        next_event_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=17, pady=10)

    # return index of the last event
    def load_last_event(self, first_data=False):
        current_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
        # current_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
        self.index -= 1
        last_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
        # last_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
        self.plot_figure(cc_cal=True)
        self.reset_view()
        self.load_event_info()
        while current_event_time == last_event_time:
            self.index -= 1
            last_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
            # last_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
            self.plot_figure(cc_cal=True)
            self.reset_view()
            self.load_event_info()
        if first_data:
            self.index += 1

    # plot seismic phases for the previous data self.file
    def last_event(self):
        if self.index > 0:
            self.load_last_event()
            self.load_last_event(first_data=True)
            # load event info if ever see this event
            self.reset_view()
            self.load_event_info()
            self.close_window = False
            # clear the previous fig object
            if hasattr(self, 'canvas_container'):
                plt.close()
                self.canvas_container.destroy()
                self.canvas_button.destroy()
                self.canvas_label.destroy()
            # plot the previous data file
            self.plot_figure()
        else:
            print('Alert: this is the first event data!!!')

    def next_event(self):
        # update event info for last event
        self.update_event_info()
        if self.index < len(self.data_files)-1:
            current_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
            # current_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
            self.index += 1
            next_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
            # next_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
            # update event info, reset and load event info
            self.reset_view()
            self.load_event_info()
            self.update_event_info()
            # skip the same event
            while current_event_time == next_event_time:
                self.index += 1
                next_event_time = self.data_files[self.index].split('/')[-1].split('.')[0]
                # next_event_time = obspy.read(self.data_files[self.index])[0].stats.starttime.strftime("%Y-%m-%d-%H-%M-%S")
                # update event info, reset and load event info
                self.plot_figure(cc_cal=True)
                self.reset_view()
                self.load_event_info()
                self.update_event_info()
            # load event info if ever see this event
            self.reset_view()
            self.load_event_info()
            self.close_window = False
            # clear the previous fig object
            if hasattr(self, 'canvas_container'):
                plt.close()
                self.canvas_container.destroy()
                self.canvas_button.destroy()
                self.canvas_label.destroy()
            # plot the next data file
            self.plot_figure()
        else:
            # quit button
            self._quit()

    # classify seismic phases
    def phases_classify(self, phase_num):
        if phase_num == 1:
            if self.P_classify == 1:
                self.P_classify = 0
                self.P_classify_value.config(text='no ')
            else:
                self.P_classify = 1
                self.P_classify_value.config(text='yes')
        elif phase_num == 2:
            # switch_classify(self.PcP_classify, self.PcP_classify_value)
            if self.PcP_classify == 1:
                self.PcP_classify = 0
                self.PcP_classify_value.config(text='no ')
            else:
                self.PcP_classify = 1
                self.PcP_classify_value.config(text='yes')
        elif phase_num == 3:
            if self.PKiKP_classify == 1:
                self.PKiKP_classify = 0
                self.PKiKP_classify_value.config(text=' no')
            else:
                self.PKiKP_classify = 1
                self.PKiKP_classify_value.config(text='yes')
    
    # phase pick-up
    def phase_pick(self, phase_num):
        if phase_num == 1:
            self.pick_active = [1, 0, 0]
        elif phase_num == 2:
            self.pick_active = [0, 1, 0]      
        elif phase_num == 3:
            self.pick_active = [0, 0, 1]
        self.fig.canvas.mpl_connect('button_press_event', self.phase_mouse_pick)

    def phase_mouse_pick(self, event):
        if self.pick_active[0] == 1:
            # in axes and left double click
            if event.inaxes and event.button == 1 and event.dblclick:
                self.P_pick = event.xdata
                self.P_pick_value.config(text='=%.3f s'%self.P_pick)
                # update phase classification
                if self.P_pick != 0:
                    self.P_classify = 1
                    self.P_classify_value.config(text='yes')
        elif self.pick_active[1] == 1:
            if event.inaxes and event.button == 1 and event.dblclick:
                self.PcP_pick = event.xdata
                self.PcP_pick_value.config(text='=%.3f s'%self.PcP_pick)
                if self.PcP_pick != 0:
                    self.PcP_classify = 1
                    self.PcP_classify_value.config(text='yes')
        elif self.pick_active[2] == 1:
            if event.inaxes and event.button == 1 and event.dblclick:
                self.PKiKP_pick = event.xdata
                self.PKiKP_pick_value.config(text='s %.3f='%self.PKiKP_pick)
                if self.PKiKP_pick != 0:
                    self.PKiKP_classify = 1
                    self.PKiKP_classify_value.config(text='yes')
    
    # correct seismic phase pick-up
    def correct_phase_pick(self):
        self.correct_flag = True
        if self.correct_index == 0:
            correct_pick = [self.P_pick, self.PcP_pick, self.PKiKP_pick]
        else:
            correct_pick = [self.P_pick+self.P_pick_tmp, self.PcP_pick+self.PcP_pick_tmp, self.PKiKP_pick+self.PKiKP_pick_tmp]
        self.close_window = False
        # clear the previous fig object
        if hasattr(self, 'canvas_container'):
            plt.close()
            self.canvas_container.destroy()
            self.canvas_button.destroy()
            self.canvas_label.destroy()
        self.plot_figure(self.correct_flag, correct_pick)
        self.correct_index += 1

    # plot seismic phases for the next data self.file
    def plot_next_data(self):
        # update event info for last event
        self.update_event_info()
        if self.index < len(self.data_files)-1:
            self.index += 1
            # statisfy the minimum cross correlation value
            self.plot_figure(cc_cal=True)
            self.reset_view()
            self.load_event_info()
            while self.cc_min_flag == False:
                self.update_event_info() 
                self.index += 1
                self.plot_figure(cc_cal=True)
                self.reset_view()
                self.load_event_info()
            self.close_window = False
            # clear the previous fig object
            if hasattr(self, 'canvas_container'):
                plt.close()
                self.canvas_container.destroy()
                self.canvas_button.destroy()
                self.canvas_label.destroy()
            # plot the next data file
            self.plot_figure()
        else:
            # quit button
            self._quit()
    
    # plot seismic phases for the previous data self.file
    def plot_last_data(self):
        if self.index > 0:
            self.index -= 1
            self.plot_figure(cc_cal=True)
            # load event info if ever see this event
            self.reset_view()
            self.load_event_info()
            while self.cc_min_flag == False and self.index > 0:
                self.index -= 1
                self.plot_figure(cc_cal=True)
                self.reset_view()
                self.load_event_info()
            self.close_window = False
            # clear the previous fig object
            if hasattr(self, 'canvas_container'):
                plt.close()
                self.canvas_container.destroy()
                self.canvas_button.destroy()
                self.canvas_label.destroy()
            # plot the previous data file
            self.plot_figure()
        else:
            print('Alert: this is the first event data!!!')
    
    # load event info if ever see this event
    def load_event_info(self):
        if self.index < len(self.event_info):
            # retrive the previous phase classification and pick-up
            self.P_classify = self.event_info[self.index][1]
            self.PcP_classify = self.event_info[self.index][2]
            self.PKiKP_classify = self.event_info[self.index][3]
            self.P_pick = self.event_info[self.index][7] - self.event_info[self.index][4]
            self.PcP_pick = self.event_info[self.index][8] - self.event_info[self.index][5]
            self.PKiKP_pick = self.event_info[self.index][9] - self.event_info[self.index][6]
            self.drop_data_flag = self.event_info[self.index][-1]
            self.correct_flag = False
        else:
            # resert phase classification and pick-up
            self.reset_view()
        
    # resert phase classification and pick-up
    def reset_view(self):
        self.P_classify = 0
        self.PcP_classify = 0
        self.PKiKP_classify = 0
        self.P_pick = 0
        self.PcP_pick = 0
        self.PKiKP_pick = 0
        self.P_pick_tmp = 0
        self.PcP_pick_tmp = 0
        self.PKiKP_pick_tmp = 0
        self.drop_data_flag = 0
        self.correct_index = 0
        self.correct_flag = False
        self.P_classify_value.config(text=' no')
        self.PcP_classify_value.config(text='no ')
        self.PKiKP_classify_value.config(text=' no')
        self.P_pick_value.config(text='=%.3f s'%self.P_pick)
        self.PcP_pick_value.config(text='=%.3f s'%self.P_pick)
        self.PKiKP_pick_value.config(text='s %.3f='%self.PKiKP_pick)
        self.drop_data_value.config(text='no ')

    # update event info if the event is already in the event info list
    def update_event_info(self):
        data_info = self.single_wave_data()
        duplicate_flag = 0
        for i, value in enumerate(self.event_info):
            if value[0] == self.data_files[self.index]:
                # update event info
                self.event_info[i] = data_info
                duplicate_flag = 1
        if duplicate_flag == 0:
            self.event_info.append(data_info)

    # get single wave data
    def single_wave_data(self):
        if self.wave_data_fig:
            data_info = [self.data_files[self.index], self.P_classify, self.PcP_classify, self.PKiKP_classify, self.P_predic_pick, self.PcP_predic_pick, 
                         self.PKiKP_predic_pick, self.P_predic_pick+self.P_pick_tmp+self.P_pick, self.PcP_predic_pick+self.PcP_pick_tmp+self.PcP_pick, 
                         self.PKiKP_predic_pick+self.PKiKP_pick_tmp+self.PKiKP_pick, self.PcP_predic_pick+self.PcP_cc_lag, self.PKiKP_predic_pick+self.PKiKP_cc_lag, 
                         self.PcP_cc_max, self.PKiKP_cc_max, self.drop_data_flag]
        else:
            data_info = [self.data_files[self.index], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        return data_info

    # save event info to csv file
    def save_info(self):
        # save event info for last event
        if self.index < len(self.data_files):
            self.correct_phase_pick()
            self.update_event_info()
        # save event info to csv file
        print('Save event info to csv file (event_info.csv)...')
        event_data = pd.DataFrame(self.event_info, columns=['event_wave', 'P_classify', 'PcP_classify', 'PKiKP_classify', 'P_predic_pick', 'PcP_predic_pick', 'PKiKP_predic_pick', 
                                                            'P_manual_pick', 'PcP_manual_pick', 'PKiKP_manual_pick', 'PcP_cc_pick', 'PKiKP_cc_pick', 'PcP_cc_max', 'PKiKP_cc_max', 'drop_data_flag'])
        event_data.to_csv(self.output_file, index=False)
        print('Saving...... Done!')

    # drop the current data self.file
    def drop_data(self):
        if self.drop_data_flag == 0:
            self.drop_data_flag = 1
            self.drop_data_value.config(text='yes')
        else:
            self.drop_data_flag = 0
            self.drop_data_value.config(text='no ')

    # quit button
    def _quit(self):
        result = messagebox.askyesnocancel("Confirmation", "Do you sure to exit?")
        if result is True:
            self.save_info()
            print('Save data and close the window...')
            self.master.quit()
            self.master.destroy()
        elif (result is False) or (result is None):
            print("Cancel to exit.")


if __name__ == '__main__':
    app = Phaseviewer("event_demo")
    
    