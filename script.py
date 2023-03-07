import os, time
def run_script():
    process_id = os.system("python3 bot.py & echo $!") # Run script in the background and get the process ID
    print("Script running in the background with process ID:", process_id)
    return process_id

def stop_script(process_id):
    os.kill(process_id, signal.SIGTERM) # Stop the script by sending a SIGTERM signal
    print("Script stopped with process ID:", process_id)

if __name__ == "__main__":
    process_id = run_script() # Run the script and get the process ID
    while True:
        time.sleep(21600) # Wait for 6 hours before stopping the script
        stop_script(process_id) # Stop the script using the process ID
        process_id = run_script() # Run the script again and get a new process ID