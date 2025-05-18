import google.generativeai as genai

def geminiDialogueCreation(num_characters, max_length, location, style, movie_name):
    print("Dialogue is generating..")
    # Gemini API
    # API key
    genai.configure(api_key="AIzaSyBsldWs2a7SGRZaYx5fFq9VmaN8yFVrpm4")
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Create a dialogue with {num_characters} characters, max {max_length} words,
    set in {location}, with a {style} style.
    for the movie {movie_name}
    """

    response = model.generate_content(prompt)
    print("Dialogue is generated.")

    return response
