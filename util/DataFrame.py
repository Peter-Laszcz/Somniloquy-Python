import os
import pandas as pd
import platform
import subprocess
import tkinter as tk
from tkinter import ttk


data_path = os.getcwd()+"/data/dataframe.parquet"

class DataFrameUtility:
    @staticmethod
    def setup():
        if not os.path.exists(data_path):
            df = pd.DataFrame(columns=['Date Created', 'Length (s)', 'Transcript Exists', 'Transcript', 'File Path'])
            df = df.astype({
                'Date Created': 'datetime64[ns]',
                'Length (s)': 'int64',
                'Transcript Exists': 'bool',
                'Transcript': 'object',
                'File Path': 'object',
            })
            df.to_parquet(data_path, engine='pyarrow')

    @staticmethod
    def get_untranscribed_files():
        df = pd.read_parquet(data_path)
        untranscribed = df.loc[df['Transcript Exists'] == False, 'File Path'].tolist()
        return untranscribed

    @staticmethod
    def add_transcript(file_path, transcript):
        df = pd.read_parquet(data_path)
        idx = df.index[df['File Path'] == file_path]
        df.loc[idx, ['Transcript', 'Transcript Exists']] = transcript, True
        df.to_parquet(data_path)

    @staticmethod
    def add_entry(length, is_transcribed, transcript, file_path):
        existing_df = pd.read_parquet(data_path)
        new_data = {
            'Date Created': pd.Timestamp.now(),
            'Length (s)': length,
            'Transcript Exists': is_transcribed,
            'Transcript': transcript,
            'File Path': file_path
        }
        new_df = pd.DataFrame([new_data])

        result_df = pd.concat([existing_df, new_df], ignore_index=True)
        result_df.to_parquet(data_path)

class DataBrowser:
    def __init__(self, root, df):
        self.root = tk.Toplevel(root)
        self.df = df
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Browse Clips")
        self.root.geometry("1000x600")

        clip_frame = ttk.Frame(self.root, padding="10")
        clip_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(clip_frame, columns=list(self.df.columns), show="headings")
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(clip_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click) # Open files on double-clicking path


        self.populate_tree()

    def populate_tree(self):
        for _, row in self.df.iterrows():
            self.tree.insert("", "end", values=list(row))

    @staticmethod
    def open_clip(file_path):
        # Uses OS to call correct subroutine
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(file_path)
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        except Exception as e:
            print(f"Error opening {file_path}: {e}")

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        file_path = values[4]  # file column here

        if os.path.exists(file_path):
            self.open_clip(file_path)
        else:
            print(f"File not found: {file_path}")
