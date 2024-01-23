import glob 
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from .phase_map import phase_fig

"""
GUI for seismic phase view and pick-up
"""
class Phaseviewer:
    # initialize
    def __init__(self, datafolder, filter=False, filter_freq=[1, 3]):
        master = tk.Tk()
        master.geometry("900x700")
        self.event_info = []
        self.master = master
        self.master.title("Seismic Phase Viewer")
        # self.file folder path
        self.data_folder_path = datafolder
        self.data_files = glob.glob(self.data_folder_path + "/*.sac")
        if len(self.data_files) == 0:
            raise ValueError('No sac file in the folder!!!')
        # filter data
        self.filter = filter
        self.filter_freq = filter_freq
        self.index = 0
        # phase
        self.PcP_classify = 0
        self.PKiKP_classify = 0
        self.PcP_pick = 0
        self.PKiKP_pick = 0
        # initial figure
        self.plot_figure()
        # mainloop
        tk.mainloop()

    # plot seismic phases for the next data self.file
    def plot_figure(self):
        if self.index < len(self.data_files):
            file_path = self.data_files[self.index]
            self.fig, self.travel_times, self.phase_wave, self.cross_corr = phase_fig(data_wave=file_path, filter_data=self.filter, filter_freq=self.filter_freq)
            # predicted phase arrival
            self.PcP_predic_pick = self.travel_times['PcP']
            self.PKiKP_predic_pick = self.travel_times['PKiKP']
            # phase wave cut
            self.PcP_wave = self.phase_wave['view_cut']['PcP']
            self.PKiKP_wave = self.phase_wave['view_cut']['PKiKP']
            if 'P' not in self.travel_times.keys():
                print('%s : no P arrival.' % self.data_files[self.index])
                # phase cross correlation
                self.PcP_cc_wave = 0 
                self.PKiKP_cc_wave = 0
                self.PcP_cc_max = 0
                self.PKiKP_cc_max = 0
                self.PcP_cc_lag = 0
                self.PKiKP_cc_lag = 0
            else:
                # phase cross correlation
                self.PcP_cc_wave = self.cross_corr['PcP']['corr_wave']
                self.PKiKP_cc_wave = self.cross_corr['PKiKP']['corr_wave']
                self.PcP_cc_max = self.cross_corr['PcP']['corr_max']
                self.PKiKP_cc_max = self.cross_corr['PKiKP']['corr_max']
                self.PcP_cc_lag = self.cross_corr['PcP']['lag_max']
                self.PKiKP_cc_lag = self.cross_corr['PKiKP']['lag_max']
            self.embed_fig_in_tkinter(self.fig)
            self.canvas.draw()
        else:
            # quit button
            self._quit()

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
        # next button
        next_button = tk.Button(self.canvas_container, text="Next", command=self.plot_next_data)
        next_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=5)
        # Last button
        last_button = tk.Button(self.canvas_container, text="Last", command=self.plot_last_data)
        last_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=5)
        # phase classification button
        PcP_class_button = tk.Button(self.canvas_container, text=" PcP ", command=lambda: self.phase_classify(1))
        PcP_class_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        self.PcP_classify_value = tk.Label(self.canvas_container, text='yes' if self.PcP_classify==1 else 'no')
        self.PcP_classify_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        PKiKP_class_button = tk.Button(self.canvas_container, text="PKiKP", command=lambda: self.phase_classify(2))
        PKiKP_class_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        self.PKiKP_classify_value = tk.Label(self.canvas_container, text='yes' if self.PKiKP_classify==1 else 'no')
        self.PKiKP_classify_value.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        # pick-up PcP button
        PcP_pick_button = tk.Button(self.canvas_container, text=" PcP Pick ", command=lambda: self.phase_pick(1))
        PcP_pick_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        # PcP value
        self.PcP_pick_value = tk.Label(self.canvas_container, text='=%.3f s'%self.PcP_pick)
        self.PcP_pick_value.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        # pick-up PKiKP button
        PKiKP_class_button = tk.Button(self.canvas_container, text="PKiKP Pick", command=lambda: self.phase_pick(2))
        PKiKP_class_button.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        # # PKiKP value
        self.PKiKP_pick_value = tk.Label(self.canvas_container, text='s %.3f='%self.PKiKP_pick)
        self.PKiKP_pick_value.pack(side=tk.RIGHT, fill=tk.BOTH, anchor=tk.CENTER, padx=10, pady=5)
        # quit button
        quit_button = tk.Button(self.canvas_container, text="Quit", command=self._quit)
        quit_button.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.CENTER, padx=15, pady=5)
    
    # classify seismic phases
    def phase_classify(self, phase_num):
        if phase_num == 1:
            if self.PcP_classify == 1:
                self.PcP_classify = 0
                self.PcP_classify_value.config(text='no')
            else:
                self.PcP_classify = 1
                self.PcP_classify_value.config(text='yes')
        elif phase_num == 2:
            if self.PKiKP_classify == 1:
                self.PKiKP_classify = 0
                self.PKiKP_classify_value.config(text='no')
            else:
                self.PKiKP_classify = 1
                self.PKiKP_classify_value.config(text='yes')
    
    # phase pick-up
    def phase_pick(self, phase_num):
        if phase_num == 1:
            self.PcP_pick_active = 1
            self.PKiKP_pick_active = 0
        elif phase_num == 2:
            self.PcP_pick_active = 0
            self.PKiKP_pick_active = 1        
        self.fig.canvas.mpl_connect('button_press_event', self.phase_mouse_pick)
    def phase_mouse_pick(self, event):
        if self.PcP_pick_active == 0 and self.PKiKP_pick_active == 1:
            # in axes and left double click
            if event.inaxes and event.button == 1 and event.dblclick:
                self.PKiKP_pick = event.xdata
                self.PKiKP_pick_value.config(text='s %.3f='%self.PKiKP_pick)
                # update PKiKP classification
                if self.PKiKP_pick != 0:
                    self.PKiKP_classify = 1
                    self.PKiKP_classify_value.config(text='yes')
        elif self.PcP_pick_active == 1 and self.PKiKP_pick_active == 0:
            # in axes and left double click
            if event.inaxes and event.button == 1 and event.dblclick:
                self.PcP_pick = event.xdata
                self.PcP_pick_value.config(text='=%.3f s'%self.PcP_pick)
                # update PcP classification
                if self.PcP_pick != 0:
                    self.PcP_classify = 1
                    self.PcP_classify_value.config(text='yes')
    
    # plot seismic phases for the next data self.file
    def plot_next_data(self):
        self.update_event_info(self.data_files[self.index])
        # clear the previous fig object
        if hasattr(self, 'canvas_container'):
            self.canvas_container.destroy()
        # resert phase classification and pick-up
        self.PcP_classify = 0
        self.PKiKP_classify = 0
        self.PcP_pick = 0
        self.PKiKP_pick = 0
        # plot the next data file
        self.index += 1
        self.plot_figure()
    
    # plot seismic phases for the previous data self.file
    def plot_last_data(self):
        if self.index and self.index < len(self.data_files):
            # self.update_event_info(self.data_files[self.index])
            # clear the previous fig object
            if hasattr(self, 'canvas_container'):
                self.canvas_container.destroy()
            # retrive the previous phase classification and pick-up
            self.PcP_classify = self.event_info[-1][1]
            self.PKiKP_classify = self.event_info[-1][2]
            self.PcP_pick = self.event_info[-1][5] - self.event_info[-1][3]
            self.PKiKP_pick = self.event_info[-1][6] - self.event_info[-1][4]
            # plot the previous data file
            self.index -= 1
            self.plot_figure()
        else:
            print('Alert: this is the first event data!!!')
    
    # update event info if the event is already in the event info list
    def update_event_info(self, event_wave):
        data_info = [event_wave, self.PcP_classify, self.PKiKP_classify, self.PcP_predic_pick, self.PKiKP_predic_pick, 
                        self.PcP_predic_pick+self.PcP_pick, self.PKiKP_predic_pick+self.PKiKP_pick, self.PcP_predic_pick+self.PcP_cc_lag, 
                        self.PKiKP_predic_pick+self.PKiKP_cc_lag, self.PcP_cc_max, self.PKiKP_cc_max, self.PcP_wave, self.PKiKP_wave, 
                        self.PcP_cc_wave, self.PKiKP_cc_wave]
        duplicate_flag = 0
        for i, value in enumerate(self.event_info):
            if value[0] == event_wave:
                # update event info
                self.event_info[i] = data_info
                duplicate_flag = 1
        if duplicate_flag == 0:
            self.event_info.append(data_info)
    
    # quit button
    def _quit(self):
        # save event info for last event
        if self.index < len(self.data_files):
            self.event_info.append([self.data_files[self.index], self.PcP_classify, self.PKiKP_classify, self.PcP_predic_pick, self.PKiKP_predic_pick, 
                                self.PcP_predic_pick+self.PcP_pick, self.PKiKP_predic_pick+self.PKiKP_pick, self.PcP_predic_pick+self.PcP_cc_lag, 
                                self.PKiKP_predic_pick+self.PKiKP_cc_lag, self.PcP_cc_max, self.PKiKP_cc_max, self.PcP_wave, self.PKiKP_wave, 
                                self.PcP_cc_wave, self.PKiKP_cc_wave])
        # save event info to csv file
        print('Save event info to csv file (event_info.csv)...')
        self.event_info = pd.DataFrame(self.event_info, columns=['event_wave', 'PcP_classify', 'PKiKP_classify', 'PcP_predic_pick', 'PKiKP_predic_pick', 
                                                                 'PcP_manual_pick', 'PKiKP_manual_pick', 'PcP_cc_pcik', 'PKiKP_cc_pick', 'PcP_cc_max', 
                                                                 'PKiKP_cc_max', 'PcP_wave', 'PKiKP_wave', 'PcP_cc_wave', 'PKiKP_cc_wave'])
        self.event_info.to_csv('event_info.csv', index=False)
        print('Done!')
        print('Close the window...')
        self.master.quit()     # abort mainloop
        self.master.destroy()  




if __name__ == '__main__':
    app = Phaseviewer("event_demo")
    
    