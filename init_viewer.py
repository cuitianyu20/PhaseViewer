
import PhaseViewer

### event folder ###
event_folder = "src/event_demo" # first-order folder: contain sac files (*.sac)
# event_folder = "event_demo/event" # second-order folder: contain sac files (*.sac)

### filter data ###
filter_data = True # True: filter data; False: no filter
filter_freq = [1, 2] # filter frequency range (Hz), default: [1, 3] and corners=4

### output file ###
output_file = "event_info.csv" # output file name

# phase viewer: return event_info,csv file (event informatin)
PhaseViewer.Phaseviewer(event_folder, filter=filter_data, filter_freq=filter_freq, output_file=output_file)





