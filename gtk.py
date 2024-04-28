import sys
import gi
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
import group_photos
import os

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(600, 250)
        self.set_title("AI Gallery Manager")
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        self.open_button = Gtk.Button(label="Open")
        self.header.pack_start(self.open_button)
        self.open_button.set_icon_name("document-open-symbolic")
        self.open_dialog = Gtk.FileChooserNative.new("Pick a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, "_Open", "_Cancel")
        self.open_dialog.set_title("Select an Image Folder")
        f = Gtk.FileFilter()
        f.set_name("Folders")
        f.add_mime_type("inode/directory")
        self.open_dialog.add_filter(f)  # Set the filters for the open dialog
        self.open_dialog.connect("response", self.open_dialog_open_callback)
        self.open_button.connect('clicked', self.show_open_dialog)
        self.main_box = Gtk.Box()
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
    
    def show_open_dialog(self, button):
        self.open_dialog.show()

    def process_photos(self):
        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Processing files")
        self.main_box.append(self.progress_bar)
        if self.folder_path is not None:
            print(f"Folder path is {self.folder_path}")
            #group_photos.process_folder(self.folder_path, self.progress_bar.set_fraction)
        self.main_box.remove(self.progress_bar)
        self.display_results()

    def display_results(self):
        results_path = os.path.join(self.folder_path, 'results')
        image_grid = Gtk.Grid.new()
        current_column = 0
        current_row = 0
        for subdir, dirs, files in os.walk(results_path):
            for current_dir in dirs:
                print(current_dir)
                current_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                sample_image = Gtk.Picture.new_for_filename(get_first_file_path(os.path.join(results_path, current_dir)))
                title_entry = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(current_dir, len(current_dir)))
                tick_button = Gtk.Button()
                tick_button.set_icon_name("emblem-ok-symbolic")
                tick_button.connect("clicked", self.change_dir_name, os.path.join(results_path, current_dir), title_entry.get_buffer().get_text)
                entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                entry_box.append(title_entry)
                entry_box.append(tick_button)
                current_box.append(sample_image)
                current_box.append(entry_box)
                image_grid.attach(current_box, current_column, current_row, 1, 1)
                current_column+=1
                if current_column%3 == 0:
                    current_column = 0
                    current_row+=1

        self.main_box.append(image_grid)

        
    def change_dir_name(self, button, old_path, new_name_function):
        os.rename(old_path, os.path.join(os.path.dirname(old_path), new_name_function()))
        
    def open_dialog_open_callback(self, dialog, result):
        try:
            if result == Gtk.ResponseType.ACCEPT:
                self.folder_path = dialog.get_file().get_path()
                self.open_dialog.destroy()
                threading.Thread(target=self.process_photos).start()
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")
     


def get_first_file_path(directory_path):
    directory_contents = os.listdir(directory_path)
    for item in directory_contents:
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            return item_path
    return None

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.leoring.AIGalleryManager")
app.run(sys.argv)
