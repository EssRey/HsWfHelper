# need to adjust paths and files

import glob
import json
import requests
import csv

successes_v1={}
successes_v2={}

files = glob.glob("logs/v1/200/*.json")
for filename in files:
    with open(filename) as f:
        wf = json.load(f)
        try:
            old_id = int(filename[20:-9])
        except:
            print(filename)
            assert False
        new_id = int(wf["migrationStatus"]["workflowId"])
        successes_v1[old_id] = new_id

files = glob.glob("logs/*.json")
for filename in files:
    with open(filename) as f:
        if filename[-8:-5] == "200":
            wf = json.load(f)
            old_id = int(filename[13:-9])
            new_id = int(wf["migrationStatus"]["workflowId"])
            successes_v2[old_id] = new_id

#print(successes_v1)
#print(successes_v2)

redundant_wfs=[]
double_counted_wfs=[]
counter=0
for wf in successes_v2:
    if wf in successes_v1:
        counter+=1
        redundant_wfs.append(successes_v2[wf])
        double_counted_wfs.append(str(wf))

# drop double_counted in 2
# drop any wf not in d_c in 1

files = ["LIVE_v1_full_migration_log.csv", "LIVE_v2_full_migration_log.csv"]



file_counter=0
header_was_written=False
for filename in files:
    combined_log = []
    file_counter+=1
    with open(filename, newline="") as f:
        reader = csv.reader(f)
        row_counter = 0
        for row in reader:
            row_counter += 1
            if row_counter == 1:
                combined_log.append(row)
            else:
                if row[0] != "workflow":
                    combined_log.append(row)
                elif str(row[1]) in double_counted_wfs and filename == files[0]:
                    combined_log.append(row)
                elif str(row[1]) not in double_counted_wfs and filename == files[1]:
                    combined_log.append(row)
    output_file = open("select_log_"+str(file_counter)+".csv", 'w', newline ="")
    with output_file:    
        write = csv.writer(output_file)
        write.writerows(combined_log)

#for wf in redundant_wfs:
#    url = "https://api.hubapi.com/automation/v3/workflows/" + str(wf) + "?hapikey=eu1-3940-f2b9-440c-aa74-b8c91363161b"
#    #x = requests.delete(url)
#print("yo")
