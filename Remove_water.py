import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class WaterRemovalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Underwater Color Removal")

        self.original_image = None
        self.display_image = None
        self.history = []
        self.ref_colors = []
        self.click_points = []

        
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Load Image", command=self.load_image).pack(side="left", padx=3)
        tk.Button(button_frame, text="Apply Water Correction", command=self.apply_processing).pack(side="left", padx=3)
        tk.Button(button_frame, text="Clear Samples", command=self.clear_samples).pack(side="left", padx=3)
        tk.Button(button_frame, text="Undo", command=self.undo).pack(side="left", padx=3)
        tk.Button(button_frame, text="Reset", command=self.reset_image).pack(side="left", padx=3)
        tk.Button(button_frame, text="Save Output", command=self.save_image).pack(side="left", padx=3)

       
        tk.Button(button_frame, text="Quit", command=root.destroy, fg="white", bg="red").pack(side="left", padx=3)

        
        self.strength = tk.Scale(root, from_=0, to=200,
                                orient="horizontal",
                                label="Scale Strength")
        self.strength.set(100)
        self.strength.pack(pady=5)

       
        self.canvas = tk.Canvas(root, width=1000, height=500)
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.pick_color)

    def load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")]
        )
        if not path:
            return

        self.original_image = cv2.imread(path)
        self.display_image = self.original_image.copy()
        self.history = []
        self.ref_colors = []
        self.click_points = []

        self.update_preview()

    def save_image(self):
        if self.display_image is None:
            return

        path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if path:
            cv2.imwrite(path, self.display_image)
            messagebox.showinfo("Saved", "Image saved!")

    def pick_color(self, event):
        if self.original_image is None:
            return

        h, w = self.original_image.shape[:2]

        if event.x > 500:
            x_img = int((event.x - 500) * w / 500)
        else:
            x_img = int(event.x * w / 500)

        y_img = int(event.y * h / 500)

        color = self.original_image[y_img, x_img]
        self.ref_colors.append(color)

        self.click_points.append((event.x, event.y))

        print(f"Sample added: {color} | Total: {len(self.ref_colors)}")

        self.update_preview()

    def clear_samples(self):
        self.ref_colors = []
        self.click_points = []

        print("Samples cleared")
        self.update_preview()

    def apply_processing(self):
        if not self.ref_colors:
            messagebox.showwarning("No samples", "Click water points first.")
            return

        self.history.append(self.display_image.copy())

        avg_color = np.mean(self.ref_colors, axis=0)
        print(f"Average water color: {avg_color}")

        strength = self.strength.get() / 100.0

        img = self.original_image.astype(np.float32)
        ref = avg_color.astype(np.float32)

        ref = np.where(ref == 0, 1, ref)

        scale = (128.0 / ref) * strength + (1 - strength)

        result = img * scale
        result = np.clip(result, 0, 255).astype(np.uint8)

        self.display_image = result
        self.update_preview()

    def undo(self):
        if self.history:
            self.display_image = self.history.pop()
            self.update_preview()

    def reset_image(self):
        if self.original_image is None:
            return

        self.display_image = self.original_image.copy()
        self.history = []
        self.ref_colors = []
        self.click_points = []

        print("Reset complete")
        self.update_preview()

    def update_preview(self):
        if self.original_image is None:
            return

        left = cv2.resize(self.original_image, (500, 500))
        right = cv2.resize(self.display_image, (500, 500))

        combined = np.hstack((left, right))

        # Draw markers
        for (x, y) in self.click_points:
            cv2.circle(combined, (x, y), 5, (0, 0, 255), -1)

        combined_rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(combined_rgb)

        self.tk_image = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = WaterRemovalApp(root)
    root.mainloop()
