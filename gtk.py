import sys
import gi
import threading
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GdkPixbuf
import group_photos
import os

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(800, 600)
        self.set_title("AI Gallery Manager")
        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
        self.folder_path = "Select a folder"
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
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.create_start_menu()
        self.main_box.append(self.start_menu_box)
        self.set_child(self.main_box)
    
    def show_open_dialog(self, button):
        self.open_dialog.show()

    def process_photos_click(self, button):
        if self.folder_path != "Select a folder":
            self.start_menu_box.hide()
            threading.Thread(target=self.process_photos).start()
    

    def process_photos(self):
        self.progress_bar = Gtk.ProgressBar.new()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Processing files")
        self.main_box.append(self.progress_bar)
        print(f"Folder path is {self.folder_path}")
        group_photos.process_folder(self.folder_path, self.progress_bar.set_fraction)
        self.main_box.remove(self.progress_bar)
        self.display_results()

    def create_start_menu(self):
        self.start_menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.folder_path_label = Gtk.Label(label=self.folder_path)
        group_faces_button = Gtk.Button(label="Group By Face")
        group_faces_button.connect("clicked", self.process_photos_click)
        self.start_menu_box.append(self.folder_path_label)
        self.start_menu_box.append(group_faces_button)

    def display_results(self):
        results_path = os.path.join(self.folder_path, 'grouped_by_face')
        image_grid = Gtk.Grid.new()
        current_column = 0
        current_row = 0
        for subdir, dirs, files in os.walk(results_path):
            for current_dir in dirs:
                current_path = os.path.join(results_path, current_dir)
                current_box = self.build_image_dir_entry(current_path)
                image_grid.attach(current_box, current_column, current_row, 1, 1)
                current_column+=1
                if current_column%3 == 0:
                    current_column = 0
                    current_row+=1

        self.main_box.append(image_grid)

    def open_file_manager(self, _a, _b, _c, _d, folder_path, current_name_function):
        os.system(f'xdg-open "{os.path.join(os.path.dirname(folder_path), current_name_function())}"')
        
    def build_image_dir_entry(self, current_path):
        current_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title_entry = Gtk.Entry.new_with_buffer(Gtk.EntryBuffer.new(os.path.basename(current_path), len(os.path.basename(current_path))))
        tick_button = Gtk.Button()
        tick_button.set_icon_name("emblem-ok-symbolic")
        tick_button.connect("clicked", self.change_dir_name, current_path, title_entry.get_buffer().get_text)
        sample_image_path = os.path.join(current_path, ".sample.jpg")
        sample_image_pixbuf = GdkPixbuf.Pixbuf.new_from_file(sample_image_path)
        original_width = sample_image_pixbuf.get_width()
        original_height = sample_image_pixbuf.get_height()
        aspect_ratio = original_height / original_width
        new_width = 200
        new_height = int(new_width * aspect_ratio)
        sample_image_pixbuf = sample_image_pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
        sample_image = Gtk.Picture.new_for_pixbuf(sample_image_pixbuf)
        click_controller = Gtk.GestureClick.new()
        click_controller.connect("pressed", self.open_file_manager, current_path, title_entry.get_buffer().get_text)
        sample_image.add_controller(click_controller)
        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        entry_box.append(title_entry)
        entry_box.append(tick_button)
        current_box.append(sample_image)
        current_box.append(entry_box)
        return current_box
        
            
    def change_dir_name(self, button, old_path, new_name_function):
        os.rename(old_path, os.path.join(os.path.dirname(old_path), new_name_function()))
        
    def open_dialog_open_callback(self, dialog, result):
        try:
            if result == Gtk.ResponseType.ACCEPT:
                self.folder_path = dialog.get_file().get_path()
                self.folder_path_label.set_label(self.folder_path) 
                self.open_dialog.destroy()
        except GLib.Error as error:
            print(f"Error opening file: {error.message}")
     


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.leoring.AIGalleryManager")
app.run(sys.argv)
