import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer

# IMDb Top 10 Movie Fetch
def fetch_top_movies():
    url = "https://www.imdb.com/chart/top/"
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.select("td.titleColumn a")
    return [title.text for title in titles[:10]]

# Fetch movie summary and storyline
def get_movie_storyline(title):
    ia = Cinemagoer()
    movies = ia.search_movie(title)
    if movies:
        movie = ia.get_movie(movies[0].movieID)
        summary = movie.get('plot outline', "No storyline available.")
        return summary
    return "No storyline available."

# Handle movie selection
def on_movie_select(event):
    selected_title = movie_combo.get()
    storyline = get_movie_storyline(selected_title)
    info_text.delete(1.0, tk.END)
    info_text.insert(tk.END, f"Title: {selected_title}\n\nStoryline:\n{storyline}")

# GUI main window
root = tk.Tk()
root.title("PDA-226 Movie App")
root.geometry("1000x700")

# Top Movie Combobox
tk.Label(root, text="Select a Movie:", font=("Arial", 12)).pack(pady=10)
movie_combo = ttk.Combobox(root, values=fetch_top_movies(), width=60, font=("Arial", 12))
movie_combo.pack()
movie_combo.bind("<<ComboboxSelected>>", on_movie_select)

# Movie Info Text Area
info_text = tk.Text(root, height=10, width=100, wrap=tk.WORD)
info_text.pack(pady=10)

# Dialogue Parameters
tk.Label(root, text="aDialogue Parameters", font=("Arial", 14, "bold")).pack(pady=10)
param_frame = tk.Frame(root)
param_frame.pack()

tk.Label(param_frame, text="Number of Characters (2-4):").grid(row=0, column=0)
char_count = tk.Entry(param_frame)
char_count.grid(row=0, column=1)

tk.Label(param_frame, text="Dialogue Max Length (words):").grid(row=1, column=0)
dialogue_length = tk.Entry(param_frame)
dialogue_length.grid(row=1, column=1)

# Image Generation Parameters
tk.Label(root, text="Image Generation Parameters", font=("Arial", 14, "bold")).pack(pady=10)
img_frame = tk.Frame(root)
img_frame.pack()

tk.Label(img_frame, text="Location:").grid(row=0, column=0)
location_entry = tk.Entry(img_frame, width=40)
location_entry.grid(row=0, column=1)

tk.Label(img_frame, text="Style:").grid(row=1, column=0)
style_combo = ttk.Combobox(img_frame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"])
style_combo.grid(row=1, column=1)

# Placeholder Buttons for Gemini and Vertex AI
tk.Button(root, text="Generate Dialogue & Image", font=("Arial", 12),
          command=lambda: messagebox.showinfo("Stub", "LLM & Vertex AI call goes here.")
          ).pack(pady=15)

# Output Areas
tk.Label(root, text="Generated Dialogue:", font=("Arial", 12)).pack()
dialogue_text = tk.Text(root, height=8, width=100)
dialogue_text.pack(pady=5)

tk.Label(root, text="Generated Image Placeholder", font=("Arial", 12)).pack()
canvas = tk.Canvas(root, width=400, height=250, bg="lightgray")
canvas.pack(pady=5)

# Start GUI
root.mainloop()
