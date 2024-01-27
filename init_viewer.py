
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

### load selected event information ###
event_info = None   # if load selected event information, set event_info = "event_info.csv"
# event_info = "event_info.csv"

### output file ###
output_file = "event_info_out.csv" # output file name

# phase viewer: return event_info,csv file (event informatin)
PhaseViewer.Phaseviewer(event_folder, folder_order=folder_order, filter=filter_data, filter_freq=filter_freq, event_info=event_info, sort_by_dis=sort_by_distance, output_file=output_file)


