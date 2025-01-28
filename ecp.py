import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import threading
import pyttsx3
from datetime import datetime
import csv
import pandas as pd
import streamlit as st # Added for Streamlit integration (if needed)
import io # Added for Streamlit integration (if needed)


class SecuritySystem:
    def __init__(self):
        self.initialized = True
        self.prev_frame = None
        self.motion_threshold = 25
        self.min_motion_area = 500
        self.detection_history = []
        self.max_history = 1000

    def set_sensitivity(self, sensitivity: int):
        """Adjust motion detection sensitivity (0-100)"""
        self.motion_threshold = int(50 - (sensitivity * 0.4))
        self.min_motion_area = int(1000 - (sensitivity * 8))

    def detect_changes(self, current_frame):
        """Basic motion detection using PIL and numpy"""
        if current_frame is None:
            return False, None, []

        # Convert PIL image to grayscale numpy array
        gray = current_frame.convert('L')
        gray_np = np.array(gray)

        if self.prev_frame is None:
            self.prev_frame = gray_np
            return False, current_frame, []

        # Calculate absolute difference
        frame_delta = np.abs(gray_np - self.prev_frame)
        motion_detected = np.mean(frame_delta) > self.motion_threshold

        # Update previous frame
        self.prev_frame = gray_np

        if motion_detected:
            # Simple zone detection (divide image into 9 zones)
            h, w = gray_np.shape
            zones = []
            for i in range(3):
                for j in range(3):
                    zone = frame_delta[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
                    if np.mean(zone) > self.motion_threshold:
                        zones.append(i * 3 + j)
            return True, current_frame, zones

        return False, current_frame, []

    def process_frame(self, frame):
        """Process frame for basic detection"""
        try:
            if not self.initialized or frame is None:
                return [], frame

            # Convert to PIL Image if needed
            if not isinstance(frame, Image.Image):
                frame = Image.fromarray(frame)

            # Perform motion detection
            motion_detected, processed_frame, zones = self.detect_changes(frame)

            detections = []
            if motion_detected:
                detections.append({
                    'class': 'motion',
                    'confidence': 1.0,
                    'zones': zones,
                    'timestamp': datetime.now().isoformat()
                })

                # Update detection history
                self.detection_history.append({
                    'type': 'motion',
                    'zones': zones,
                    'timestamp': datetime.now().isoformat()
                })
                if len(self.detection_history) > self.max_history:
                    self.detection_history = self.detection_history[-self.max_history:]

            return detections, processed_frame

        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return [], frame

    def get_statistics(self):
        """Get basic statistics"""
        if not self.detection_history:
            return {}

        return {
            'total_detections': len(self.detection_history),
            'motion_events': len([d for d in self.detection_history if d['type'] == 'motion']),
            'last_detection': self.detection_history[-1]['timestamp'] if self.detection_history else None
        }

class YOLOv5App:
    def __init__(self, root):
        self.root = root
        self.root.title("ECP Technology | S.Tamilselvan ")
        self.root.geometry("1200x800")
        self.root.config(bg="#d9e2ef")

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)

        # Detection settings
        self.confidence_threshold = tk.DoubleVar(value=0.25)
        self.detection_mode = tk.StringVar(value="all")  
        self.paused = False

        # Initialize GUI components
        self.create_widgets()

        # Variables to store file paths and results
        self.image_path = None
        self.video_path = None
        self.cap = None
        self.results_image = None

        # Set up drag-and-drop handling
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)
        self.security_system = SecuritySystem() #Added security system instance


    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.root, bg="#d9e2ef")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel for controls and detections list
        left_panel = tk.Frame(main_container, bg="#d9e2ef", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_panel.pack_propagate(False)

        # Control buttons
        control_frame = tk.Frame(left_panel, bg="#d9e2ef")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Refresh button at the top
        self.refresh_button = tk.Button(control_frame, text="↻ Refresh", command=self.refresh_app,
                                      bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
        self.refresh_button.pack(fill=tk.X, pady=2)

        # Predictions button - Removed as per instruction
        #self.predictions_button = tk.Button(control_frame, text="📊 Predictions Analysis", 
        #                                  command=self.open_predictions,
        #                                  bg="#9C27B0", fg="white", 
        #                                  font=("Helvetica", 10, "bold"))
        #self.predictions_button.pack(fill=tk.X, pady=2)
        # Separator after buttons
        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=5)

        self.upload_image_button = tk.Button(control_frame, text="Upload Image", command=self.upload_image, bg="#4a86e8", fg="white")
        self.upload_image_button.pack(fill=tk.X, pady=2)

        self.upload_video_button = tk.Button(control_frame, text="Upload Video", command=self.upload_video, bg="#4a86e8", fg="white")
        self.upload_video_button.pack(fill=tk.X, pady=2)

        self.start_detection_button = tk.Button(control_frame, text="Start Detection", command=self.start_detection, bg="#4a86e8", fg="white", state=tk.DISABLED)
        self.start_detection_button.pack(fill=tk.X, pady=2)

        self.save_button = tk.Button(control_frame, text="Save Result", command=self.save_result, bg="#4a86e8", fg="white", state=tk.DISABLED)
        self.save_button.pack(fill=tk.X, pady=2)

        self.export_button = tk.Button(control_frame, text="Export Results", command=self.export_results, bg="#4a86e8", fg="white", state=tk.DISABLED)
        self.export_button.pack(fill=tk.X, pady=2)

        # Video control buttons
        self.pause_button = tk.Button(control_frame, text="Pause", command=self.pause_video, bg="#4a86e8", fg="white", state=tk.DISABLED)
        self.pause_button.pack(fill=tk.X, pady=2)

        self.resume_button = tk.Button(control_frame, text="Resume", command=self.resume_video, bg="#4a86e8", fg="white", state=tk.DISABLED)
        self.resume_button.pack(fill=tk.X, pady=2)

        # Add detection mode selection
        mode_frame = tk.LabelFrame(control_frame, text="Detection Mode", bg="#d9e2ef")
        mode_frame.pack(fill=tk.X, pady=5)

        modes = [("All", "all"), 
                ("Vehicles Only", "vehicles"),
                ("People Only", "people"),
                ("Hand Gestures", "hands")]

        for text, mode in modes:
            tk.Radiobutton(mode_frame, 
                          text=text,
                          variable=self.detection_mode,
                          value=mode,
                          bg="#d9e2ef").pack(anchor=tk.W)


        # Confidence threshold
        threshold_frame = tk.Frame(left_panel, bg="#d9e2ef")
        threshold_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.threshold_label = tk.Label(threshold_frame, text="Confidence Threshold:", bg="#d9e2ef")
        self.threshold_label.pack()
        
        self.threshold_slider = tk.Scale(threshold_frame, from_=0, to=1, resolution=0.01, orient='horizontal', 
                                      variable=self.confidence_threshold, bg="#d9e2ef")
        self.threshold_slider.pack(fill=tk.X)

        # Detections list
        detections_frame = tk.Frame(left_panel, bg="#d9e2ef")
        detections_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(detections_frame, text="Detected Objects:", bg="#d9e2ef", font=("Helvetica", 12, "bold")).pack()
        
        # Create a frame for the detection list with scrollbar
        list_frame = tk.Frame(detections_frame, bg="#d9e2ef")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detections_list = tk.Listbox(list_frame, bg="white", fg="black", 
                                        font=("Helvetica", 10), height=15,
                                        yscrollcommand=scrollbar.set)
        self.detections_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.detections_list.yview)

        # Right panel for image display
        right_panel = tk.Frame(main_container, bg="#d9e2ef")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_label = tk.Label(right_panel, bg="#d9e2ef")
        self.image_label.pack(expand=True, fill=tk.BOTH)

        self.result_label = tk.Label(right_panel, text="", bg="#d9e2ef", font=("Helvetica", 14))
        self.result_label.pack(pady=5)

    def speak_detection(self, text):
        """Speak the detection text using text-to-speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Text-to-speech error: {e}")

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("JPEG Files", "*.jpg"), ("PNG Files", "*.png"), ("JPEG Files", "*.jpeg")])

        if self.image_path:
            self.display_image(self.image_path)
            self.start_detection_button.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("No Selection", "No image file selected.")

    def upload_video(self):
        try:
            self.video_path = filedialog.askopenfilename(
                title="Select Video File",
                filetypes=[("Video Files", "*.mp4"), ("AVI Files", "*.avi"), ("MOV Files", "*.mov"), ("MKV Files", "*.mkv"), ("All Files", "*.*")]
            )
            if self.video_path:
                self.cap = cv2.VideoCapture(self.video_path)
                if not self.cap.isOpened():
                    messagebox.showerror("Error", "Could not open video file.")
                    return
                self.start_detection_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.NORMAL)
                self.result_label.config(text=f"Loaded video: {self.video_path}")
            else:
                messagebox.showwarning("No Selection", "No video file selected.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def start_detection(self):
        
        current_mode = self.detection_mode.get()

        if self.image_path:
            self.detect_image(self.image_path, current_mode)
        elif self.cap:
            threading.Thread(target=lambda: self.detect_video(current_mode)).start()
        else:
            messagebox.showwarning("No File Selected", 
                                 "Please upload an image or video before starting detection.")

    def display_image(self, path):
        img = Image.open(path)
        img = img.resize((800, 600), Image.LANCZOS)  
        img = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img)
        self.image_label.image = img

    def detect_image(self, path, mode="all"):
        try:
            img = Image.open(path)
            img_np = np.array(img)
            
            detections, processed_img = self.security_system.process_frame(img_np)

            # Clear previous detections
            self.detections_list.delete(0, tk.END)
            detection_texts = []

            # Process and display detections
            if detections:
                for detection in detections:
                    detection_texts.append(f"Motion detected in zones: {detection['zones']}")

            processed_img = Image.fromarray(processed_img)
            processed_img = processed_img.resize((800, 600), Image.LANCZOS)
            self.results_image = ImageTk.PhotoImage(processed_img)
            self.image_label.configure(image=self.results_image)

            # Update detections list and speak
            for text in detection_texts:
                self.detections_list.insert(tk.END, text)
                threading.Thread(target=self.speak_detection, args=(text,)).start()

            # Enable save and export buttons
            self.save_button.config(state=tk.NORMAL)
            self.export_button.config(state=tk.NORMAL)

            # Save detection results for export
            self.current_results = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'detections': detection_texts,
                'confidence': self.confidence_threshold.get(),
                'mode': mode
            }

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during detection: {str(e)}")

    def detect_video(self, mode="all"):
        self.paused = False
        self.export_results_list = []

        # Clear previous detections
        self.detections_list.delete(0, tk.END)

        if self.cap is None:
            return

        while self.cap.isOpened():
            if self.paused:
                self.root.update()
                continue

            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)

            detections, processed_frame = self.security_system.process_frame(frame)

            for detection in detections:
                detection_text = f"[{datetime.now().strftime('%H:%M:%S')}] Motion detected in zones: {detection['zones']}"
                self.detections_list.insert(tk.END, detection_text)
                self.detections_list.see(tk.END)  
                threading.Thread(target=self.speak_detection, 
                               args=(f"Motion detected",)).start()
                self.export_results_list.append(detection_text)

            processed_frame = processed_frame.resize((800, 600), Image.LANCZOS)
            processed_frame = ImageTk.PhotoImage(processed_frame)

            self.image_label.configure(image=processed_frame)
            self.image_label.image = processed_frame
            self.root.update()

        self.cap.release()

    def save_result(self):
        if self.results_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("Image Files", "*.jpg;*.png")])
            if file_path:
                self.results_image.save(file_path)

    def export_results(self):
        if not self.export_results_list:
            messagebox.showwarning("No Data", "No detection results to export!")
            return

        # Create export options window
        export_window = tk.Toplevel(self.root)
        export_window.title("Export Options")
        export_window.geometry("400x300")
        export_window.config(bg="#d9e2ef")

        # Export options
        options_frame = tk.Frame(export_window, bg="#d9e2ef")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # File format selection
        format_frame = tk.LabelFrame(options_frame, text="Export Format", bg="#d9e2ef")
        format_frame.pack(fill=tk.X, pady=5)
        
        format_var = tk.StringVar(value="csv")
        tk.Radiobutton(format_frame, text="CSV", variable=format_var, value="csv", bg="#d9e2ef").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(format_frame, text="Excel", variable=format_var, value="excel", bg="#d9e2ef").pack(side=tk.LEFT, padx=5)

        # Column selection
        columns_frame = tk.LabelFrame(options_frame, text="Include Columns", bg="#d9e2ef")
        columns_frame.pack(fill=tk.X, pady=5)

        timestamp_var = tk.BooleanVar(value=True)
        object_var = tk.BooleanVar(value=True)
        confidence_var = tk.BooleanVar(value=True)
        coordinates_var = tk.BooleanVar(value=True)

        tk.Checkbutton(columns_frame, text="Timestamp", variable=timestamp_var, bg="#d9e2ef").pack(anchor=tk.W)
        tk.Checkbutton(columns_frame, text="Object Name", variable=object_var, bg="#d9e2ef").pack(anchor=tk.W)
        tk.Checkbutton(columns_frame, text="Confidence", variable=confidence_var, bg="#d9e2ef").pack(anchor=tk.W)
        tk.Checkbutton(columns_frame, text="Coordinates", variable=coordinates_var, bg="#d9e2ef").pack(anchor=tk.W)

        def export_with_options():
            try:
                # Get selected columns
                columns = []
                if timestamp_var.get(): columns.append("Timestamp")
                if object_var.get(): columns.append("Object")
                if confidence_var.get(): columns.append("Confidence")
                if coordinates_var.get(): columns.append("Coordinates")

                if not columns:
                    messagebox.showwarning("Export Error", "Please select at least one column to export!")
                    return

                # Prepare data
                data = []
                for detection in self.export_results_list:
                    # Parse detection string
                    parts = detection.split("]")
                    timestamp = parts[0].strip("[")
                    det_info = parts[1].strip()
                    
                    # Extract object name and confidence
                    obj_conf = det_info.split("(")
                    obj_name = obj_conf[0].strip()
                    confidence = "N/A" #No confidence in motion detection

                    
                    # Create row based on selected columns
                    row = {}
                    if "Timestamp" in columns: row["Timestamp"] = timestamp
                    if "Object" in columns: row["Object"] = obj_name
                    if "Confidence" in columns: row["Confidence"] = confidence
                    if "Coordinates" in columns: row["Coordinates"] = "N/A"  # Add coordinates if available
                    
                    data.append(row)

                # Create DataFrame
                df = pd.DataFrame(data)

                # Get save file path
                file_format = format_var.get()
                if file_format == "csv":
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv")]
                    )
                    if file_path:
                        df.to_csv(file_path, index=False)
                else:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx")]
                    )
                    if file_path:
                        df.to_excel(file_path, index=False)

                if file_path:
                    messagebox.showinfo("Success", f"Results exported successfully to {file_path}")
                    export_window.destroy()

            except Exception as e:
                messagebox.showerror("Export Error", f"Error during export: {str(e)}")

        # Export button
        tk.Button(options_frame, text="Export", command=export_with_options,
                 bg="#4a86e8", fg="white").pack(pady=10)

    def refresh_app(self):
        """Reset the application state and clear all detections"""
        try:
            # Reset video capture if it exists
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
                self.cap = None

            # Clear detection list
            self.detections_list.delete(0, tk.END)
            
            # Clear export results
            self.export_results_list = []
            
            # Reset image display
            self.image_label.configure(image='')
            self.image_label.image = None
            
            # Reset result label
            self.result_label.config(text="")
            
            # Reset file paths
            self.image_path = None
            self.video_path = None
            
            # Reset buttons states
            self.start_detection_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.export_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            
            # Reset results image
            self.results_image = None
            
            # Show success message
            messagebox.showinfo("Refresh", "Application has been reset successfully!")
            
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Error during refresh: {str(e)}")

    def pause_video(self):
        self.paused = True

    def resume_video(self):
        self.paused = False

    def handle_drop(self, event):
        self.image_path = event.data.strip('{}')  
        self.display_image(self.image_path)
        self.start_detection_button.config(state=tk.NORMAL)

    def open_predictions(self):
        pass # Placeholder -  remove this function entirely if not needed


# Main application loop
root = TkinterDnD.Tk()  
app = YOLOv5App(root)
root.mainloop()