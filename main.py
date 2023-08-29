import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os

class ImageAnnotationApp:
    def __init__(self, root, image_paths, txt_paths):
        self.root = root
        self.image_paths = image_paths
        self.txt_paths = txt_paths
        self.current_index = 0

        # Initialize with the first valid image and its text file
        self.image = None
        self.txt_file_path = None
        self.find_next_valid_image()

        self.canvas = tk.Canvas(root, width=self.image.width, height=self.image.height)
        self.canvas.pack()

        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)

        self.rectangles = []
        self.load_rectangles()

        self.remove_button = tk.Button(root, text="Remove Rectangle", command=self.remove_rectangle)
        self.remove_button.pack()

        self.drawing = False
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)  # Right-click

        # Bind the 'n' key to move to the next image
        root.bind("<KeyPress-n>", self.next_image)
        # Bind the 'p' key to move to the previous image
        root.bind("<KeyPress-p>", self.previous_image)

    def find_next_valid_image(self):
        while self.current_index < len(self.image_paths):
            self.image = Image.open(self.image_paths[self.current_index])
            self.txt_file_path = self.txt_paths[self.current_index]

            if os.path.exists(self.txt_file_path):
                break  # Found a valid image with a corresponding text file
            else:
                self.current_index += 1

    def next_image(self, event=None):
        self.save_rectangles()  # Save the rectangles before moving to the next image

        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self.find_next_valid_image()

        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
        self.rectangles = []
        self.load_rectangles()

    def previous_image(self, event=None):
        self.save_rectangles()  # Save the rectangles before moving to the previous image

        self.current_index = (self.current_index - 1) % len(self.image_paths)
        self.find_next_valid_image()

        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
        self.rectangles = []
        self.load_rectangles()

    def next_image(self, event=None):
        self.save_rectangles()  # Save the rectangles before moving to the next image
        
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self.load_image_and_text()
        
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
        self.rectangles = []
        self.load_rectangles()

    def load_image_and_text(self):
        self.image = Image.open(self.image_paths[self.current_index])
        self.txt_file_path = self.txt_paths[self.current_index]

    def load_rectangles(self):
        with open(self.txt_file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.strip().split()
            class_number = int(parts[0])
            albumentations_coords = [float(x) for x in parts[1:]]
            image_width, image_height = self.image.size
            x_min = int(albumentations_coords[0] * image_width)
            y_min = int(albumentations_coords[1] * image_height)
            width = int(albumentations_coords[2] * image_width)
            height = int(albumentations_coords[3] * image_height)
            self.rectangles.append((x_min, y_min, width, height, class_number))
            self.draw_rectangle(x_min, y_min, width, height, class_number)

    def draw_rectangle(self, x_min, y_min, width, height, class_number):
        outline_color = "green"
        outline_width = 2
        # if (method == "load"):  
        self.canvas.create_rectangle(x_min - width/2, y_min - height/2, x_min + width/2, y_min + height/2, outline=outline_color, width=outline_width)
        # else:
        #     self.canvas.create_rectangle(x_min- width/2, y_min-height/2, x_min + width, y_min + height, outline=outline_color, width=outline_width)
        self.canvas.create_text(x_min + width/2, y_min - 15, text=f"Class: {class_number}", fill=outline_color)

    def remove_rectangle(self):
        if self.rectangles:
            last_rectangle = self.rectangles.pop()
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
            for rect in self.rectangles:
                self.draw_rectangle(*rect)

    def on_canvas_click(self, event):
        self.drawing = True
        self.start_x = event.x
        self.start_y = event.y

    def on_canvas_drag(self, event):
        if self.drawing:
            x = event.x
            y = event.y
            self.canvas.delete("temp_rectangle")
            self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline="red", width=2, tags="temp_rectangle")

    def on_canvas_release(self, event):
        if self.drawing:
            x = event.x
            y = event.y
            self.drawing = False
            self.canvas.delete("temp_rectangle")

            x_min = min(self.start_x, x)
            y_min = min(self.start_y, y)
            width = abs(x - self.start_x)
            height = abs(y - self.start_y)

            self.rectangles.append((x_min + width/2, y_min + height/2, width, height, 0))  # Class number is initially 0
            self.draw_rectangle(x_min+ width/2, y_min+ height/2, width, height, 0)

    def on_canvas_right_click(self, event):
        x, y = event.x, event.y
        clicked_rectangle = None

        for rect in self.rectangles:
            x_min, y_min, width, height, _ = rect
            x_max, y_max = x_min + width, y_min + height

            if x_min <= x <= x_max and y_min <= y <= y_max:
                clicked_rectangle = rect
                break

        if clicked_rectangle:
            self.rectangles.remove(clicked_rectangle)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)
            for rect in self.rectangles:
                self.draw_rectangle(*rect)
    def save_rectangles(self):
        with open(self.txt_file_path, 'w') as file:
            for rect in self.rectangles:
                x_min, y_min, width, height, class_number = rect
                print(rect)
                image_width, image_height = self.image.size
                albumentations_coords = [
                    x_min / image_width,
                    y_min / image_height,
                    (width) / image_width,
                    (height) / image_height
                ]
                line = f"{class_number} {' '.join(map(str, albumentations_coords))}\n"
                file.write(line)

if __name__ == "__main__":
    root = tk.Tk()

    image_folder = "./images"
    txt_folder = "./labels"

    image_paths = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder)]

    # Generate corresponding text file paths by changing the extension to .txt
    txt_paths = [os.path.join(txt_folder, os.path.splitext(os.path.basename(image_path))[0] + ".txt") for image_path in image_paths]

    app = ImageAnnotationApp(root, image_paths, txt_paths)

    root.mainloop()
