import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class PredictionAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Detection Analysis Tool")
        self.root.geometry("1200x800")
        self.root.config(bg="#f0f0f0")
        
        self.data = None
        self.setup_gui()

    def setup_gui(self):
        # Main container with two main frames
        self.left_frame = tk.Frame(self.root, bg="#f0f0f0", width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.left_frame.pack_propagate(False)

        self.right_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame Contents
        # Title
        title_label = tk.Label(self.left_frame, text="Analysis Controls", 
                             font=("Helvetica", 14, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)

        # Buttons Frame
        button_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=5)

        # Back Button
        self.back_button = tk.Button(button_frame, text="← Back",
                                   command=self.go_back,
                                   bg="#ff4444", fg="white",
                                   font=("Helvetica", 10))
        self.back_button.pack(side=tk.LEFT, padx=5)

        # Upload Button
        self.upload_button = tk.Button(button_frame, text="Upload CSV",
                                     command=self.load_csv,
                                     bg="#4CAF50", fg="white",
                                     font=("Helvetica", 10))
        self.upload_button.pack(side=tk.RIGHT, padx=5)

        # Chart Selection Frame
        self.chart_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.chart_frame.pack(fill=tk.X, pady=10, padx=5)

        # Statistics Frame
        stats_frame = tk.LabelFrame(self.left_frame, text="Statistics", 
                                  bg="#f0f0f0", font=("Helvetica", 10, "bold"))
        stats_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=30, 
                                font=("Helvetica", 9))
        self.stats_text.pack(padx=5, pady=5)

        # Export Button
        self.export_button = tk.Button(self.left_frame, text="Export Chart",
                                     command=self.export_chart,
                                     bg="#2196F3", fg="white",
                                     font=("Helvetica", 10))
        self.export_button.pack(fill=tk.X, pady=10, padx=5)

        # Right Frame Contents
        self.graph_label = tk.Label(self.right_frame, text="Select data and chart type to begin",
                                  font=("Helvetica", 12), bg="#f0f0f0")
        self.graph_label.pack(pady=20)

        # Frame for the graph
        self.graph_frame = tk.Frame(self.right_frame, bg="white")
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

    def load_csv(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv")]
            )
            if file_path:
                self.data = pd.read_csv(file_path)
                # Get available columns for plotting
                self.available_columns = list(self.data.columns)
                self.setup_chart_options()
                self.update_statistics()
                messagebox.showinfo("Success", "Data loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading CSV: {str(e)}")

    def setup_chart_options(self):
        # Clear previous options
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Add column selector
        tk.Label(self.chart_frame, text="Select Column:", 
                bg="#f0f0f0", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=2, padx=5)
        
        self.column_var = tk.StringVar(value=self.available_columns[0] if self.available_columns else "")
        column_menu = ttk.Combobox(self.chart_frame, textvariable=self.column_var,
                                 values=self.available_columns)
        column_menu.pack(fill=tk.X, padx=5, pady=2)
        column_menu.bind('<<ComboboxSelected>>', lambda e: self.show_graph())

        # Chart type options
        tk.Label(self.chart_frame, text="Select Chart Type:", 
                bg="#f0f0f0", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=2, padx=5)

        self.chart_type = tk.StringVar(value="bar")
        charts = [
            ("Bar Chart", "bar"),
            ("Pie Chart", "pie"),
            ("Histogram", "histogram"),
            ("Line Plot", "line")
        ]

        for text, value in charts:
            rb = tk.Radiobutton(self.chart_frame, text=text, value=value,
                              variable=self.chart_type, bg="#f0f0f0",
                              font=("Helvetica", 9),
                              command=self.show_graph)
            rb.pack(anchor=tk.W, pady=2, padx=5)

    def show_graph(self):
        if self.data is None or not hasattr(self, 'column_var'):
            messagebox.showwarning("No Data", "Please upload a CSV file first!")
            return

        selected_column = self.column_var.get()
        if not selected_column:
            messagebox.showwarning("Error", "Please select a column to plot!")
            return

        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        try:
            # Create figure and axis
            plt.clf()
            figure = plt.figure(figsize=(10, 6))
            ax = figure.add_subplot(111)

            data_to_plot = self.data[selected_column]

            if self.chart_type.get() == "bar":
                if pd.api.types.is_numeric_dtype(data_to_plot):
                    # For numeric data, create value ranges
                    counts = pd.cut(data_to_plot, bins=10).value_counts()
                    bars = ax.bar(range(len(counts)), counts.values)
                    ax.set_xticks(range(len(counts)))
                    ax.set_xticklabels([f"{int(i.left)}-{int(i.right)}" for i in counts.index], rotation=45)
                else:
                    # For categorical data, use value counts
                    counts = data_to_plot.value_counts()
                    bars = ax.bar(range(len(counts)), counts.values)
                    ax.set_xticks(range(len(counts)))
                    ax.set_xticklabels(counts.index, rotation=45)

                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')

            elif self.chart_type.get() == "pie":
                counts = data_to_plot.value_counts()
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%')

            elif self.chart_type.get() == "histogram":
                if pd.api.types.is_numeric_dtype(data_to_plot):
                    ax.hist(data_to_plot, bins=20, edgecolor='black')
                else:
                    messagebox.showwarning("Warning", "Histogram requires numeric data!")
                    return

            elif self.chart_type.get() == "line":
                if pd.api.types.is_numeric_dtype(data_to_plot):
                    ax.plot(range(len(data_to_plot)), data_to_plot, '-o')
                    if len(data_to_plot) > 20:  # If too many points, show fewer x-labels
                        ax.set_xticks(range(0, len(data_to_plot), len(data_to_plot)//10))
                else:
                    messagebox.showwarning("Warning", "Line plot requires numeric data!")
                    return

            # Set labels and title
            ax.set_title(f"{selected_column} Distribution")
            ax.set_xlabel(selected_column)
            ax.set_ylabel("Count" if self.chart_type.get() in ["bar", "histogram"] else "Value")

            # Adjust layout
            plt.tight_layout()

            # Create canvas and show plot
            canvas = FigureCanvasTkAgg(figure, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Update graph label
            chart_types = {
                "bar": "Bar Chart",
                "pie": "Pie Chart",
                "histogram": "Histogram",
                "line": "Line Plot"
            }
            self.graph_label.config(text=f"Showing {chart_types[self.chart_type.get()]} for {selected_column}")

        except Exception as e:
            messagebox.showerror("Error", f"Error creating chart: {str(e)}")
            print(f"Detailed error: {str(e)}")  # For debugging

    def update_statistics(self):
        if self.data is None:
            return
            
        try:
            selected_column = self.column_var.get()
            if not selected_column:
                return
                
            stats_text = "Data Statistics:\n\n"
            
            # Get basic statistics
            total_records = len(self.data)
            unique_values = len(self.data[selected_column].unique())
            
            stats_text += f"Total Records: {total_records}\n"
            stats_text += f"Unique Values: {unique_values}\n"
            
            if pd.api.types.is_numeric_dtype(self.data[selected_column]):
                # Add numeric statistics
                mean_val = self.data[selected_column].mean()
                median_val = self.data[selected_column].median()
                std_val = self.data[selected_column].std()
                
                stats_text += f"Mean: {mean_val:.2f}\n"
                stats_text += f"Median: {median_val:.2f}\n"
                stats_text += f"Std Dev: {std_val:.2f}\n"
            else:
                # Add categorical statistics
                mode_val = self.data[selected_column].mode().iloc[0]
                most_common = self.data[selected_column].value_counts().iloc[0]
                
                stats_text += f"Mode: {mode_val}\n"
                stats_text += f"Most Common Count: {most_common}\n"
            
            # Update the statistics text widget
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating statistics: {str(e)}")

    def export_chart(self):
        if not hasattr(self, 'graph_frame') or not self.graph_frame.winfo_children():
            messagebox.showwarning("Warning", "No chart to export!")
            return
            
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("PDF files", "*.pdf")
                ]
            )
            
            if file_path:
                # Get the current figure
                current_figure = None
                for widget in self.graph_frame.winfo_children():
                    if isinstance(widget, FigureCanvasTkAgg):
                        current_figure = widget.figure
                        break
                
                if current_figure:
                    # Save with high DPI for better quality
                    current_figure.savefig(file_path, dpi=300, bbox_inches='tight')
                    messagebox.showinfo("Success", "Chart exported successfully!")
                else:
                    messagebox.showerror("Error", "No chart found to export!")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting chart: {str(e)}")

    def go_back(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PredictionAnalyzer(root)
    root.mainloop()
