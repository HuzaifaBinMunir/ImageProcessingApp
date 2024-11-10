# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 21:08:07 2024

@author: huzai
"""

import os
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
from tkinterdnd2 import TkinterDnD, DND_FILES

class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processing App")
        self.root.geometry("600x700")

        # Initialize save format variable
        self.save_format = StringVar(value="JPEG")

        # Placeholder for the background image to avoid garbage collection
        self.bg_img_tk = None

        # Variable to store the original image (for threshold adjustments)
        self.original_img = None

        # Load background image
        self.load_background_image()

        # Create layout
        self.create_widgets()

        # Enable Drag-and-Drop functionality
        self.enable_drag_and_drop()

    def load_background_image(self):
        try:
            self.bg_img = Image.open("ip.jpg")
            self.bg_img = self.bg_img.resize((600, 700), Image.Resampling.LANCZOS)
            self.bg_img_tk = ImageTk.PhotoImage(self.bg_img)
            self.root.bg_img_tk = self.bg_img_tk

            self.bg_canvas = Canvas(self.root, width=600, height=700)
            self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_canvas.create_image(0, 0, anchor=NW, image=self.bg_img_tk)

        except Exception as e:
            print(f"Error loading background image: {e}")

    def create_widgets(self):
        title_label = Label(
            self.root,
            text="Image Processing App",
            font=("Arial", 30, "bold"),
            fg="white",
            bg="black",
            padx=10,
            pady=5
        )
        title_label.place(relx=0.5, rely=0.05, anchor="n")

        self.center_widgets()

    def center_widgets(self):
        center_frame = Frame(self.root, bg="#F0F0F0")
        center_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        button_frame = Frame(center_frame, bg="#F0F0F0")
        button_frame.pack(pady=10)

        browse_button = Button(button_frame, text="Browse", command=self.load_image)
        browse_button.grid(row=0, column=0, padx=10, pady=5)

        save_button = Button(button_frame, text="Save Image", command=self.save_image)
        save_button.grid(row=0, column=1, padx=10, pady=5)

        info_button = Button(button_frame, text="Image Info", command=self.show_image_info)
        info_button.grid(row=0, column=2, padx=10, pady=5)

        convert_button = Button(button_frame, text="Convert to B/W", command=self.convert_to_bw)
        convert_button.grid(row=1, column=0, padx=10, pady=5)

        crop_button = Button(button_frame, text="Crop Image", command=self.crop_image)
        crop_button.grid(row=1, column=1, padx=10, pady=5)

        resize_button = Button(button_frame, text="Resize Image", command=self.resize_image)
        resize_button.grid(row=1, column=2, padx=10, pady=5)

        flip_h_button = Button(button_frame, text="Flip Horizontally", command=self.flip_horizontal)
        flip_h_button.grid(row=2, column=0, padx=10, pady=5)

        flip_v_button = Button(button_frame, text="Flip Vertically", command=self.flip_vertical)
        flip_v_button.grid(row=2, column=1, padx=10, pady=5)

        combine_button = Button(button_frame, text="Combine Images", command=self.combine_images)
        combine_button.grid(row=2, column=2, padx=10, pady=5)

        # Save Format Radio Buttons Frame
        self.format_frame = Frame(center_frame, bg="#F0F0F0")
        self.format_frame.pack(pady=10)
        Label(self.format_frame, text="Save Format:", bg="#F0F0F0").pack(anchor=W)
        self.create_save_format_radiobuttons(self.format_frame)

        self.image_label_frame = Frame(center_frame, width=400, height=300, bg="black", relief="sunken")
        self.image_label_frame.pack(pady=20)

        self.image_label = Label(self.image_label_frame, text="Drag and drop an image here", bg="gray")
        self.image_label.pack()

        # Slider for threshold adjustment (initially hidden)
        self.threshold_slider = Scale(self.root, from_=0, to=255, orient=HORIZONTAL, label="Adjust Threshold", command=self.update_threshold)
        self.threshold_slider.set(128)
        self.threshold_slider.pack_forget()  # Hide slider until needed

    def create_save_format_radiobuttons(self, parent):
        formats = ["JPEG", "PNG", "BMP", "TIFF"]
        for format in formats:
            Radiobutton(parent, text=format, variable=self.save_format, value=format, bg="#F0F0F0").pack(anchor=W)

    def load_image(self):
        self.img_path = filedialog.askopenfilename()
        if self.img_path:
            self.display_loaded_image(self.img_path)

    def display_loaded_image(self, img_path):
        try:
            self.img = Image.open(img_path)
            self.original_img = self.img.copy()  # Save the original image for threshold adjustments
            self.display_image(self.img)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load image: {e}")

    def display_image(self, img):
        max_width, max_height = 400, 300
        img_width, img_height = img.size
        ratio = min(max_width / img_width, max_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        resized_image = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        self.displayed_image = ImageTk.PhotoImage(resized_image)
        self.image_label.config(image=self.displayed_image, text="")
        self.image_label.image = self.displayed_image

    def show_image_info(self):
        if self.img:
            width, height = self.img.size
            img_format = self.img.format
            file_size = os.path.getsize(self.img_path) / 1024
            info = (f"Width: {width}px\nHeight: {height}px\nFormat: {img_format}\nFile Size: {file_size:.2f} KB")
            messagebox.showinfo("Image Info", info)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def save_image(self):
        if not self.img:
            messagebox.showerror("Error", "No image to save.")
            return

        file_extension = self.save_format.get().lower()
        save_path = filedialog.asksaveasfilename(defaultextension=f".{file_extension}",
                                                 filetypes=[(self.save_format.get(), f"*.{file_extension}")])

        if save_path:
            try:
                # Check if the format is JPEG to allow custom compression levels
                if file_extension == "jpeg" or file_extension == "jpg":
                    # Ask user for a compression quality level
                    quality = simpledialog.askinteger("Input", "Enter JPEG quality (1-100)", minvalue=1, maxvalue=100)
                    if quality is not None:
                        self.img.save(save_path, format="JPEG", quality=quality)
                    else:
                        messagebox.showwarning("Warning", "Compression level not set. Image not saved.")
                else:
                    # Save without custom compression for other formats
                    self.img.save(save_path, format=self.save_format.get())
                messagebox.showinfo("Success", f"Image saved successfully as {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")

    def convert_to_bw(self):
        if self.img:
            # Place the threshold slider right below the save format radio buttons
            self.threshold_slider.pack(pady=10, after=self.format_frame)
            self.update_threshold(self.threshold_slider.get())  # Update the image with the slider's value
        else:
            messagebox.showerror("Error", "No image loaded.")

    def update_threshold(self, threshold):
        if self.original_img:
            gray_img = self.original_img.convert("L")  # Convert to grayscale
            bw_img = gray_img.point(lambda p: p > int(threshold) and 255)  # Apply threshold
            self.img = bw_img  # Update current image
            self.display_image(bw_img)  # Show updated image
        else:
            messagebox.showerror("Error", "No image loaded to apply the threshold.")

    def crop_image(self):
        if self.img:
            crop_area = simpledialog.askstring("Input", "Enter crop dimensions (left, top, right, bottom):")
            if crop_area:
                try:
                    left, top, right, bottom = map(int, crop_area.split(","))
                    self.img = self.img.crop((left, top, right, bottom))
                    self.display_image(self.img)
                except ValueError:
                    messagebox.showerror("Error", "Invalid crop dimensions.")
        else:
            messagebox.showerror("Error", "No image loaded.")

    def resize_image(self):
        if self.img:
            new_size = simpledialog.askstring("Input", "Enter new size (width, height):")
            if new_size:
                try:
                    width, height = map(int, new_size.split(","))
                    self.img = self.img.resize((width, height), Image.Resampling.LANCZOS)
                    self.display_image(self.img)
                except ValueError:
                    messagebox.showerror("Error", "Invalid size.")
        else:
            messagebox.showerror("Error", "No image loaded.")

    def flip_horizontal(self):
        if self.img:
            self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_image(self.img)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def flip_vertical(self):
        if self.img:
            self.img = self.img.transpose(Image.FLIP_TOP_BOTTOM)
            self.display_image(self.img)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def combine_images(self):
        first_img_path = filedialog.askopenfilename(title="Select First Image")
        second_img_path = filedialog.askopenfilename(title="Select Second Image")
        if first_img_path and second_img_path:
            try:
                img1 = Image.open(first_img_path)
                img2 = Image.open(second_img_path)

                combined_type = simpledialog.askstring("Input", "Type 'side' for side-by-side or 'overlay' for overlay:")

                if combined_type == "side":
                    total_width = img1.width + img2.width
                    max_height = max(img1.height, img2.height)
                    combined_image = Image.new('RGB', (total_width, max_height))
                    combined_image.paste(img1, (0, 0))
                    combined_image.paste(img2, (img1.width, 0))
                elif combined_type == "overlay":
                    combined_image = Image.blend(img1.convert("RGBA"), img2.convert("RGBA"), alpha=0.5)
                else:
                    messagebox.showerror("Error", "Invalid combine option.")
                    return

                self.img = combined_image
                self.display_image(self.img)

            except Exception as e:
                messagebox.showerror("Error", f"Unable to combine images: {e}")
        else:
            messagebox.showerror("Error", "Both images must be selected.")

    def enable_drag_and_drop(self):
        # Enable drag-and-drop functionality for the image label
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        # Get the file path from the drag-and-drop event
        file_path = event.data
        if os.path.isfile(file_path):
            self.display_loaded_image(file_path)

# Run the application
if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Using TkinterDnD for drag-and-drop
    app = ImageEditorApp(root)
    root.mainloop()
