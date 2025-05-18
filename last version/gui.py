import tkinter as tk
from tkinter import ttk, messagebox
import imdb_parser
import webbrowser
import threading
import gemini
import vertex
import base64
from PIL import Image, ImageTk
import io

# Global Variables
title_label = None
storyline_label = None
description_label = None
imdb_link_label = None
tabs = None
num_characters_var = None
max_length_var = None
location_var = None
style_var = None
dialogue_cache = {}
image_cache = {}  
dialogue_text_widget = None
current_movie_title = None
image_label = None


def generate_dialogue():
    num_characters = num_characters_var.get().strip()
    max_length = max_length_var.get().strip()
    location = location_var.get().strip()
    style = style_var.get().strip()
    movie_name = current_movie_title

    if not movie_name:
        messagebox.showerror("Insuffucent information", "Please pick a movie.")
        return

    if not num_characters.isdigit() or int(num_characters) <= 0:
        messagebox.showerror("Invalid input", "Please enter the number of characters as a positive number.")
        return
    if not max_length.isdigit() or int(max_length) <= 0:
        messagebox.showerror("Invalid input", "Please enter the maximum length as a positive number.")
        return
    if not location:
        messagebox.showerror("Missing Information", "Please enter a location.")
        return
    if style not in ["Marvel", "Futuristic", "Cartoon", "Realistic"]:
        messagebox.showerror("Incorrect Style", "Choose a valid style.")
        return

    if movie_name in dialogue_cache:
        dialogue_text_widget.delete("1.0", tk.END)
        dialogue_text_widget.insert(tk.END, dialogue_cache[movie_name])
        tabs.select(1)
        return

    try:
        response = gemini.geminiDialogueCreation(num_characters, max_length, location, style, movie_name)
        output_text = response.text if hasattr(response, "text") else str(response)

        if not output_text.strip():
            raise ValueError("The API returned an empty response.")

        dialogue_cache[movie_name] = output_text
        dialogue_text_widget.delete("1.0", tk.END)
        dialogue_text_widget.insert(tk.END, output_text)
        tabs.select(1)
    except Exception as e:
        messagebox.showerror("Error", f"Gemini API error: {e}")


def generate_image():
    movie = current_movie_title
    if not movie or movie not in dialogue_cache:
        messagebox.showerror("Missing Data", "First create dialogue for this movie.")
        return

    if movie in image_cache:
        image_label.config(image=image_cache[movie])
        image_label.image = image_cache[movie]
        tabs.select(2)
        return

    dialogue_text = dialogue_cache[movie].strip()
    if not dialogue_text:
        messagebox.showerror("Empty Dialogue", "The dialogue text is empty. Please create a valid dialogue first.")
        return

    params = {
        "num_characters": num_characters_var.get(),
        "max_length": max_length_var.get(),
        "location": location_var.get(),
        "style": style_var.get(),
        "movie": movie,
        "dialogue": dialogue_text
    }

    try:
        base64_image = vertex.generateImage(**params)
        img_bytes = base64.b64decode(base64_image)

        image = Image.open(io.BytesIO(img_bytes))
        #image = image.resize((600, int(image.height * 600 / image.width)), Image.LANCZOS)

        tk_image = ImageTk.PhotoImage(image)
        image_label.config(image=tk_image)
        image_label.image = tk_image

        image_cache[movie] = tk_image
        tabs.select(2)
    except Exception as e:
        messagebox.showerror("Error", f"Could not create image: {e}")


def fetch_and_update_storyline(title):
    storyline = imdb_parser.getMovieStorylineForMovie(title)
    storyline_label.after(0, lambda: storyline_label.config(text=f"Storyline: \n{storyline}"))


def update_details(index, top10MapList):
    global current_movie_title
    movie = top10MapList[index]
    title = movie.get('title', 'N/A')
    current_movie_title = title

    title_label.config(text=f"Title: {title}\n")
    description_label.config(text=f"Description: \n{movie.get('description', 'N/A')}\n")
    imdb_url = movie.get("url", "N/A")
    imdb_link_label.config(text=f"IMDb URL: {imdb_url}\n")
    imdb_link_label.bind("<Button-1>", lambda e: webbrowser.open(imdb_url))

    storyline_label.config(text="Loading storyline...")
    threading.Thread(target=fetch_and_update_storyline, args=(title,), daemon=True).start()

    # Diyalog varsa yükle, yoksa bilgilendir
    if title in dialogue_cache:
        dialogue_text_widget.delete("1.0", tk.END)
        dialogue_text_widget.insert(tk.END, dialogue_cache[title])
    else:
        dialogue_text_widget.delete("1.0", tk.END)
        dialogue_text_widget.insert(tk.END, "Bu film için henüz bir diyalog oluşturulmadı.")

    # Görsel varsa göster, yoksa temizle
    if title in image_cache:
        image_label.config(image=image_cache[title])
        image_label.image = image_cache[title]
    else:
        image_label.config(image="")  
        image_label.image = None


def on_movie_select(event, top10MapList):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        update_details(index, top10MapList)


def guiFunc(top10MapList: list):
    global title_label, description_label, imdb_link_label, storyline_label
    global tabs, dialogue_text_widget, image_label
    global num_characters_var, max_length_var, location_var, style_var

    mainPage = tk.Tk()
    mainPage.title("IMDB Top 10")
    mainPage.geometry("1920x1080")
    mainPage.configure(bg="lightgray")

    num_characters_var = tk.StringVar()
    max_length_var = tk.StringVar()
    location_var = tk.StringVar()
    style_var = tk.StringVar(value="Futuristic")

    font2 = ("Helvetica", 12)

    mainPage.grid_columnconfigure(1, weight=1)
    mainPage.grid_rowconfigure(0, weight=1)

    leftFrame = tk.Frame(mainPage, bd=2, relief="ridge", padx=10, pady=10, bg="lightgray")
    leftFrame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

    tk.Label(leftFrame, text="Top 10 IMDb Movies", font=("Helvetica", 16, "bold"), bg="lightgray").pack(pady=(0, 10))

    lb = tk.Listbox(leftFrame, font=font2, bd=1, width=35, height=20)
    for i, movie in enumerate(imdb_parser.top10NamesParser()):
        lb.insert(i + 1, movie)
    lb.pack(fill="both", expand=True)
    lb.bind("<<ListboxSelect>>", lambda event: on_movie_select(event, top10MapList))

    rightFrame = tk.Frame(mainPage, bd=2, relief="ridge", padx=10, pady=10, bg="white")
    rightFrame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    rightFrame.grid_columnconfigure(0, weight=1)
    rightFrame.grid_rowconfigure(1, weight=1)

    optionsFrame = tk.Frame(rightFrame, bg="lightgray")
    optionsFrame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

    tk.Label(optionsFrame, text="Number of Characters:", bg="lightgray").grid(row=0, column=0, sticky="e", pady=5)
    tk.Entry(optionsFrame, textvariable=num_characters_var, width=5).grid(row=0, column=1, padx=(0, 10), pady=5)

    tk.Label(optionsFrame, text="Max Dialogue Length (words):", bg="lightgray").grid(row=1, column=0, sticky="e", pady=5)
    tk.Entry(optionsFrame, textvariable=max_length_var, width=5).grid(row=1, column=1, padx=(0, 10), pady=5)

    tk.Label(optionsFrame, text="Location:", bg="lightgray").grid(row=0, column=2, sticky="e", pady=5)
    tk.Entry(optionsFrame, textvariable=location_var, width=10).grid(row=0, column=3, padx=(0, 10), pady=5)

    tk.Label(optionsFrame, text="Style:", bg="lightgray").grid(row=1, column=2, sticky="e", pady=5)
    styleCB = ttk.Combobox(optionsFrame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"], textvariable=style_var, width=10)
    styleCB.grid(row=1, column=3, padx=(0, 10), pady=5)

    tk.Button(optionsFrame, text="Generate Dialogue", command=generate_dialogue).grid(row=0, column=4, padx=(0, 5), pady=5)
    tk.Button(optionsFrame, text="Generate Image", command=generate_image).grid(row=1, column=4, pady=5)

    tabs = ttk.Notebook(rightFrame)
    tabs.grid(row=1, column=0, sticky="nsew")

    details_frame = tk.Frame(tabs, padx=10, pady=10, bg="white")
    tabs.add(details_frame, text="Movie Details")

    title_label = tk.Label(details_frame, text="", anchor="w", bg="white")
    title_label.pack(fill='x', pady=(0, 5))

    imdb_link_label = tk.Label(details_frame, text="", anchor="w", fg="blue", cursor="hand2", bg="white")
    imdb_link_label.pack(fill='x', pady=(0, 5))

    description_label = tk.Label(details_frame, text="", anchor="w", justify="left", wraplength=600, bg="white")
    description_label.pack(fill='x', pady=(0, 5))

    storyline_label = tk.Label(details_frame, text="", anchor="w", justify="left", wraplength=600, bg="white")
    storyline_label.pack(fill='both', pady=(0, 5))

    dialogue_frame = tk.Frame(tabs, padx=10, pady=10, bg="white")
    tabs.add(dialogue_frame, text="Generated Dialogue")

    dialogue_text_widget = tk.Text(dialogue_frame, wrap="word", width=100, height=35)
    dialogue_text_widget.pack(fill="both", expand=True)

    image_frame = tk.Frame(tabs, padx=10, pady=10, bg="white")
    tabs.add(image_frame, text="Generated Image")

    image_label = tk.Label(image_frame, bg="white")
    image_label.pack(fill="both", expand=True)

    mainPage.mainloop()
