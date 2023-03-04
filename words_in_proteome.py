from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import askokcancel
from tkinter.filedialog import askopenfile
import os
import time

WORDS_PATH_FILE = './words_list_path.txt'
SEQUENCES_PATH_FILE = './sequences_list_path.txt'


def create_file(file_name_path, content):
    file = open(file_name_path, "a")
    file.write(content)
    file.close()


def read_file(file_name):
    is_exist = os.path.exists(file_name)
    if is_exist is not True:
        return ''
    file = open(file_name, 'r')
    file_content = file.read()
    file_lines = file_content.splitlines()
    file.close()
    return file_lines


def remove_file(file_name):
    os.remove(file_name)


def read_words(file_name):
    origin_words = read_file(file_name)
    supported_words = list(filter(lambda word: len(word) >= 3, origin_words))
    transformed_words = list(map(lambda word: word.upper(), supported_words))
    return transformed_words


def clean_list(source_list):
    return list(filter(bool, source_list))


def read_sequences(file_name):
    origin_sequences = read_file(file_name)
    origin_sequences_as_string = "\n".join(origin_sequences)
    dirty_sequences = clean_list(origin_sequences_as_string.split(">sp"))

    def extract_sequences(dirty_sequence):
        id, dirty_proteome = clean_list(dirty_sequence.split('|'))
        proteome = "\n".join(clean_list(dirty_proteome.split("\n"))[1:])
        return [id, proteome]
    sequences_list = list(map(extract_sequences, dirty_sequences))
    sequences_dictionary = {}
    for sequence in sequences_list:
        id, proteome = sequence
        sequences_dictionary[id] = proteome

    return sequences_dictionary


def search_words_in_proteome(words_list, sequences_dictionary):
    words_counter_dictionary = {}
    for word in words_list:
        for sequence_key in sequences_dictionary:
            proteome = sequences_dictionary[sequence_key]
            if word not in words_counter_dictionary:
                words_counter_dictionary[word] = []
            if word in proteome:
                words_counter_dictionary[word].append(sequence_key)

    for word_counter_key in words_counter_dictionary:
        word_counter = words_counter_dictionary[word_counter_key]
        print(f'{word_counter_key} found in {len(word_counter)} sequences')

    return words_counter_dictionary


def find_most_frequent_word(words_counter_dictionary):
    most_frequenst_word = ''
    most_frequenst_word_frequency = 0
    for word_counter_key in words_counter_dictionary:
        word_frequency = len(words_counter_dictionary[word_counter_key])
        if word_frequency > most_frequenst_word_frequency:
            most_frequenst_word_frequency = word_frequency
            most_frequenst_word = word_counter_key

    print(
        f"most frequent word is {most_frequenst_word} ({most_frequenst_word_frequency})")
    return most_frequenst_word, most_frequenst_word_frequency


def file_upload_widget(window, label, button_text, button_event):
    file_upload_label = Label(window, text=label)
    file_upload_label.grid(row=1, column=1)
    file_upload_button = Button(
        window,
        text=button_text,
        command=lambda: button_event()
    )
    file_upload_button.grid(row=2, column=1)


def open_file(path_name):
    file_path = askopenfile(mode='r', filetypes=[('Text Files', '*.txt')])
    if file_path is not None:
        if path_name == "words":
            create_file(WORDS_PATH_FILE, file_path.name)
        elif path_name == "sequences":
            create_file(SEQUENCES_PATH_FILE, file_path.name)


def file_upload_widget(window, row, col, label_text, handler):
    Label(window, text=label_text, width=30).grid(row=row, column=col, pady=10)
    Button(window, text='Choose File', width=20,
           command=handler).grid(row=row, column=(col + 1))


def filed_upload_handler(window):
    def upload_files(window):
        progressbar_widget = Progressbar(
            window,
            orient=HORIZONTAL,
            length=100,
            mode='determinate'
        )
        progressbar_widget.grid(row=4, columnspan=2, pady=20)
        for _ in range(5):
            window.update_idletasks()
            progressbar_widget['value'] += 20
            time.sleep(1)
        progressbar_widget.destroy()
        Label(window, text='File Uploaded Successfully!',
              foreground='green').grid(row=4, columnspan=3, pady=10)
        time.sleep(3)
        Button(
            window,
            text='Get Most Frequent Word',
            command=lambda:  clean_all_widgets(window)
        ).grid(row=5, columnspan=3, padx=30, pady=10)

    Button(
        window,
        text='Upload Files',
        command=lambda: upload_files(window)
    ).grid(row=3, columnspan=3, pady=10)


def clean_all_widgets(window):
    widgets_list = window.grid_slaves()
    for widget in widgets_list:
        widget.destroy()
    words_list_path, = read_file(WORDS_PATH_FILE)
    Label(window, text="Word Path").grid(
        row=1, pady=10)
    Label(window, text=words_list_path).grid(
        row=2, pady=10)
    sequences_list_path, = read_file(SEQUENCES_PATH_FILE)
    Label(window, text="Sequences Path").grid(
        row=3, pady=10)
    Label(window, text=sequences_list_path).grid(
        row=4, pady=10)
    Label(window, text="------------------------------------------------------").grid(
        row=5, pady=10)
    Label(window, text="Most Frequent Word").grid(
        row=6, pady=10)

    def get_most_frequent_word():
        english_words = read_words(words_list_path)
        sequences = read_sequences(sequences_list_path)
        words_exist_counter_dictionary = search_words_in_proteome(
            english_words, sequences)
        most_frequent_word = find_most_frequent_word(
            words_exist_counter_dictionary)
        Label(window, text=most_frequent_word).grid(
            row=7, pady=10)
    Button(window, text='See Me!',
           command=lambda: get_most_frequent_word()).grid(row=7)


def create_desktop_app():
    window = Tk()
    window.title("Project: 'Mots anglais dans le protéome humain'")
    window.geometry("400x300")
    window.resizable(False, True)
    file_upload_widget(window, row=1, col=0,
                       label_text="Upload words list in txt format", handler=lambda: open_file(path_name="words"))
    file_upload_widget(window, row=2, col=0,
                       label_text="Upload sequence list in txt format", handler=lambda: open_file(path_name="sequences"))
    filed_upload_handler(window)

    def on_closing():
        if askokcancel("Quit", "Do you want to quit?"):
            remove_file(WORDS_PATH_FILE)
            remove_file(SEQUENCES_PATH_FILE)
            window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()


def main():
    create_desktop_app()


main()
