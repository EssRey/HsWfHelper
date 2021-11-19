# need to adjust paths and files

import csv

from logger import set_logging_object, set_segment_context, log_event, write_todo

log_files = ["select_log_1.csv", "select_log_2.csv"]

for log_file in log_files:
    with open(log_file, newline="") as f:
        reader = csv.reader(f)
        row_counter = 0
        for row in reader:
            row_counter += 1
            if row_counter == 1:
                number_of_rows=len(row)
                dict_keys = row[4:]
            else:
                try:
                    assert len(row)==number_of_rows
                except:
                    print(row)
                    print(len(row))
                    print(number_of_rows)
                    assert False
                object_type=row[0]
                object_id=row[1]
                segment_context=row[2]
                log_key=row[3]
                set_logging_object(object_type,object_id)
                if row[2] in ["enrollment", "reenrollment", "branching", "goal"]:
                    set_segment_context(row[2])
                else:
                    assert row[2] == ""
                event_dict = {}
                for j in range(len(dict_keys)):
                    if row[j+4] != "":
                        event_dict[dict_keys[j]]=row[j+4]
                log_event(log_key, event_dict)
write_todo("test_todo")