'''
#--globals--#
file_path = None
FILE = None
COUNT = 0


# --count the words
def word_counter(file_path):
    global COUNT
    if file_path is None:  #--Ensure a file has been selected--#
        return

    try:
        file = open(file_path, "r")
        #total_lines = sum(1 for _ in file)
        file.close()

        file = open(file_path, "r")
        lines_processed = 0
        COUNT = 0

        #progress_bar["maximum"] = total_lines  # Set progress bar max value

        for line in file:
            COUNT += len(line.split())
            lines_processed += 1
            #progress_bar["value"] = lines_processed  # Update progress bar
            #percent_label.config(text=f"{(lines_processed / total_lines) * 100:.2f}%")  # Update percentage label
            #window.update_idletasks()  # Refresh the GUI

        file.close()
        #percent_label.config(text=f"100.00%")
        #result_label.config(text=f"Total words: {COUNT}")
        print(COUNT)
        return COUNT

    except Exception as e:
        print(f"{e}")

        #messagebox.showerror("Error", f"An error occurred: {str(e)}")
'''

def word_counter(file_path):
    if file_path is None:
        print("No file provided.")
        return

    try:
        with open(file_path, "r") as file:
            count = sum(len(line.split()) for line in file)
        print(f"Total words: {count}")
        return count
    except Exception as e:
        print(f"An error occurred: {e}")

