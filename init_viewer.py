import PhaseViewer

### event folder ###
# event_folder = "src/event_folder_order_1" # first-order folder: contain sac files (*.sac)
event_folder = "src/event_folder_order_2" # second-order folder: contain event files (subfolder: contain *.sac)

### folder order ###
folder_order = 2 # 1: first-order folder; 2: second-order folder

### sort event by epicentral distance ###
sort_by_distance = True # True: sort by distance; False: no sort

### filter data ###
filter_data = True # True: filter data; False: no filter
filter_freq = [1, 3] # filter frequency range (Hz), default: [1, 3] and corners=4
filter_corner = 4 # corners of filter
zerophase = False # True: zero-phase filter

### filter sets ###
# predicted arrival time by different filter sets based on the main filter_freq
filter_freq_perturb = 0.3       # perturb frequency (Hz)
filter_freq_min = 0.5           # min frequency corner (Hz)
filter_freq_max = 5.0           # max frequency corner (Hz)
filter_freq_interval = 0.1      # frequency interval (Hz)
filter_freq_band_min = 0.5      # min frequency band (Hz) 

### load selected event information ###
# event_info = None   # if load selected event information, set event_info = "event_info.csv"
event_info = "event_info.csv"
skip_load_event = False  # True: skip recorded event information; False: load event information from first data
correct_current_data = True # True: just correct current data; False: load current data and load unprocessed data

### output file ###
output_file = "event_info_test.csv" # output file name

# phase viewer: return event_info,csv file (event informatin)
PhaseViewer.Phaseviewer(event_folder, folder_order=folder_order, filter=filter_data, filter_corner=filter_corner, zerophase=zerophase,
                        filter_freq=filter_freq, filter_freq_perturb=filter_freq_perturb, filter_freq_min=filter_freq_min, filter_freq_max=filter_freq_max, 
                        filter_freq_interval=filter_freq_interval, filter_freq_band_min=filter_freq_band_min, event_info=event_info, skip_load_event=skip_load_event, 
                        sort_by_dis=sort_by_distance, correct_current_data=correct_current_data, output_file=output_file)
