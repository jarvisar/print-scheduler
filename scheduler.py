import datetime
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.completion import WordCompleter
import tabulate

schedule_directory = "C:/Scripts/assets/Schedules/"

def initial_get_start_time():
    clear()
    show_schedule([])
    return get_start_time()

def get_start_time():
    start_time = prompt("Enter initial start time or use /load to use an existing schedule: ")
    if start_time.startswith('/load'):
        filename = start_time.split()[1]
        schedule, unformatted_start_time, day_counter = load_schedule(filename)
        start_time = datetime.datetime.strptime(unformatted_start_time, "%I:%M%p")
        show_schedule(schedule)
        print(f"Schedule loaded from {filename}")
        return start_time, schedule, day_counter
    try:
        return datetime.datetime.strptime(start_time, "%I:%M%p"), [], 0
    except ValueError:
        clear()
        show_schedule([])
        print("Invalid time format. Please use '9:00am' or '10:00pm' format.")
        return get_start_time()

def add_print_schedule(schedule, name, duration, start_time, day_counter):
    # print entire schedule for debug
    if duration == "overnight":
        end_time = datetime.datetime.strptime("7:00am", "%I:%M%p")
        if start_time.hour >= 7:
            day_counter += 1
        duration = (end_time - start_time).total_seconds() / 3600
        if duration < 0:
            duration += 24
        elif duration == 0:
            duration = 24
        end_time_str = end_time.strftime("%I:%M%p").lower()
        if day_counter != 0:
            end_time_str += " +" + str(day_counter) + "d"
        schedule.append((start_time.strftime("%I:%M%p").lower(), end_time_str, name, duration))
        return end_time, day_counter
    elif duration == "work":
        end_time = datetime.datetime.strptime("5:00pm", "%I:%M%p")
        if start_time > end_time:
            day_counter += 1
        duration = (end_time - start_time).total_seconds() / 3600
        if duration < 0:
            duration += 24
        elif duration == 0:
            duration = 24
        end_time_str = end_time.strftime("%I:%M%p").lower()
        if day_counter != 0:
            end_time_str += " +" + str(day_counter) + "d"
        schedule.append((start_time.strftime("%I:%M%p").lower(), end_time_str, name, duration))
        return end_time, day_counter
    else:
        duration = float(duration)
        end_time = start_time + datetime.timedelta(hours=duration)
        end_time_str = end_time.strftime("%I:%M%p").lower()
        if end_time.day != start_time.day:
            day_counter += 1
        if day_counter != 0:
            end_time_str += " +" + str(day_counter) + "d"
        schedule.append((start_time.strftime("%I:%M%p").lower(), end_time_str, name, str(duration)))
        return end_time, day_counter

def save_schedule(schedule, filename):
    full_path = schedule_directory + filename
    with open(full_path, 'w') as file:
        for entry in schedule:
            start_time = datetime.datetime.strptime(entry[0], "%I:%M%p")
            duration = float(entry[3])
            end_time = start_time + datetime.timedelta(hours=duration)
            # if day_counter is present, remove the space before the + sign. so 07:00am +2d becomes 07:00am+2d
            entry1 = entry[1]
            if entry[1].find("+") != -1:
                entry1 = entry[1].replace(" ", "")
            file.write(f"{entry[0]} {entry1} {entry[2]} {entry[3]} {end_time.strftime('%I:%M%p').lower()}\n")

def load_schedule(filename):
    schedule = []
    last_end_time = None
    last_day_counter = 0
    full_path = schedule_directory + filename
    with open(full_path, 'r') as file:
        for line in file:
            time, end_time_str, name, duration, end_time = line.strip().split()
            if end_time_str.find("+") != -1:
                end_time_str = end_time_str.replace("+", " +")
            day_counter = 0
            if end_time_str.find("d") != -1:
                day_counter = int(end_time_str.split("+")[1].split("d")[0])
            schedule.append((time, end_time_str, name, duration))
            last_end_time = end_time
            last_day_counter = day_counter
    return schedule, last_end_time, last_day_counter

def show_schedule(schedule):
    headers = ["Start Time", "End Time", "Name", "Duration"]
    # add a blank row to the end of the schedule with the next start time in the first column
    if schedule:
        # check for +d in the end time, need to remove it so we can parse the time
        end_time = schedule[-1][1]
        if end_time.find("+") != -1:
            end_time = end_time.split(" ")[0]
        start_time = datetime.datetime.strptime(end_time, "%I:%M%p")
        schedule.append((start_time.strftime("%I:%M%p").lower(), "", "", ""))
    table = tabulate.tabulate(schedule, headers, tablefmt="grid")
    print(table)
    # remove the blank row
    if schedule:
        schedule.pop()

def main():
    start_time, schedule, day_counter = initial_get_start_time()
    clear()
    show_schedule(schedule)
    completer = WordCompleter(['q', '/save', '/load', '/show', '/remove', '/help'])

    while True:
        input_data = prompt("Add print (or use /help): ", completer=completer)
        clear()  # Clear the screen after each input for a better user experience.
        
        if input_data == 'q':
            if schedule:
                show_schedule(schedule)
                save_option = prompt("Do you want to save the current schedule before quitting? (y/n): ")
                if save_option.lower() == 'y':
                    filename_to_save = prompt("Enter filename to save the current schedule: ")
                    save_schedule(schedule, filename_to_save)
                    print(f"Schedule saved to {filename_to_save}")
            break
        elif input_data.startswith('/save'):
            filename = input_data.split()[1]
            save_schedule(schedule, filename)
            show_schedule(schedule)
            print(f"Schedule saved to {filename}")
        elif input_data.startswith('/load'):
            if schedule:
                show_schedule(schedule)
                save_option = prompt("Do you want to save the current schedule before loading a new one? (y/n): ")
                if save_option.lower() == 'y':
                    filename_to_save = prompt("Enter filename to save the current schedule: ")
                    save_schedule(schedule, filename_to_save)
                    print(f"Schedule saved to {filename_to_save}")
            filename = input_data.split()[1]
            schedule, unformatted_start_time, day_counter = load_schedule(filename)
            start_time = datetime.datetime.strptime(unformatted_start_time, "%I:%M%p")
            clear()
            show_schedule(schedule)
            print(f"Schedule loaded from {filename}")
        elif input_data == '/show':
            show_schedule(schedule)
        elif input_data == '/remove':
            schedule.pop()
            if not schedule:
                start_time = initial_get_start_time()
            else:
                end_time = schedule[-1][1]
                if end_time.find("+") != -1:
                    day_counter = int(end_time.split("+")[1].split("d")[0])
                    end_time = end_time.split(" ")[0]
                else:
                    day_counter = 0
                start_time = datetime.datetime.strptime(end_time, "%I:%M%p")
            show_schedule(schedule)
        elif input_data == '/help':
            print("Commands:")
            print("  /save <filename> - save the current schedule to a file")
            print("  /load <filename> - load a schedule from a file")
            print("  /show - show the current schedule")
            print("  /remove - remove the last print entry")
            print("  /help - show this help message")
            print("  q - quit the program")
        else:
            try:
                name, duration = input_data.split()
                start_time, day_counter = add_print_schedule(schedule, name, duration, start_time, day_counter)
                show_schedule(schedule)
            except ValueError:
                print("Invalid input format. Use 'Name' <duration> (e.g., 'Hook' 1.5 hours)")

if __name__ == "__main__":
    main()
