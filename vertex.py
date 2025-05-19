from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import traceback
import re

def generateImage(num_characters, max_length, location, style, movie, dialogue):
    print("Generating image..")
    try:
        vertexai.init(project="swift-smoke-459318-f8", location="us-central1")
    except Exception as e:
        print(f"Warning/error during Vertex AI init (probably already initialized): {e}")

    imagen_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
    prompt_for_image = f"Scene from the movie '{movie}', located at {location}, with {num_characters} characters in a {style} style. Focus on the environment and character poses based on the dialogue: {dialogue[:150]}"

    try:
        response = imagen_model.generate_images(
            prompt=prompt_for_image,
            number_of_images=1,
            aspect_ratio='9:16' # Bu oran korunacak, genişlik artınca yükseklik de artacak
        )

        generated_image_data = response.images[0]._image_bytes
        image = Image.open(io.BytesIO(generated_image_data))

        target_width = 820 
        target_height = int(target_width * 16 / 9) 
        image = image.resize((target_width, target_height), Image.LANCZOS)
        draw = ImageDraw.Draw(image)

        
        font_size_regular = 17 
        font_size_bold = 19    
        text_color = "white"
        stroke_width_val = 2   
        
        try:
            font_regular = ImageFont.truetype("arial.ttf", font_size_regular)
            font_bold = ImageFont.truetype("arialbd.ttf", font_size_bold)
        except IOError:
            try:
                font_regular = ImageFont.truetype("DejaVuSans.ttf", font_size_regular)
                font_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size_bold)
            except IOError:
                print("Arial/DejaVu fonts not found, using default PIL font.")
                font_regular = ImageFont.load_default() 
                font_bold = ImageFont.load_default()  

        def wrap_text_segment(text_block_content, drawing_context, target_font, max_width_pixels):
            final_lines = []
            paragraphs = text_block_content.split('\n')
            for para_idx, paragraph_text in enumerate(paragraphs):
                if not paragraph_text.strip():
                    if para_idx > 0: final_lines.append("") 
                    continue
                words = paragraph_text.split()
                if not words: continue
                current_line = ""
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    if drawing_context.textlength(test_line, font=target_font) <= max_width_pixels:
                        current_line = test_line
                    else:
                        if current_line: final_lines.append(current_line)
                        current_line = word
                if current_line: final_lines.append(current_line)
            return final_lines

        
        top_margin = 60  
        left_margin = int(target_width * 0.08) 
        max_text_block_width = int(target_width * 0.45) 

        line_spacing_paragraph_break = int(font_size_regular * 0.6) 
        line_spacing_after_block = 22 
        line_spacing_dialogue_line = 7  
        line_spacing_after_name = 5  

        current_y = top_margin
        dialogue_to_display = dialogue
        raw_lines = dialogue_to_display.strip().split('\n')
        character_line_regex = re.compile(r"^\s*\*\*(.*?):\*\*\s*(.*)")

        scene_description_raw_lines = []
        first_dialogue_line_index = len(raw_lines)
        for i, line_text in enumerate(raw_lines):
            if character_line_regex.match(line_text):
                first_dialogue_line_index = i
                break
            scene_description_raw_lines.append(line_text)

        if scene_description_raw_lines:
            full_scene_desc_text = "\n".join(scene_description_raw_lines).strip()
            if full_scene_desc_text:
                wrapped_scene_lines = wrap_text_segment(full_scene_desc_text, draw, font_regular, max_text_block_width)
                for scene_line_text in wrapped_scene_lines:
                    if current_y + font_size_regular > target_height - top_margin: break
                    line_height_to_add = 0
                    if scene_line_text == "":
                        line_height_to_add = line_spacing_paragraph_break 
                    else:
                        draw.text((left_margin, int(current_y)), scene_line_text, font=font_regular, fill=text_color, stroke_width=stroke_width_val, stroke_fill='black')
                        line_height_to_add = font_size_regular
                    current_y += line_height_to_add + line_spacing_dialogue_line
                current_y += line_spacing_after_block

        dialogue_entries = []
        current_char_name_for_parse = None
        current_dialogue_buffer = []
        for i in range(first_dialogue_line_index, len(raw_lines)):
            line_text = raw_lines[i]
            stripped_line = line_text.strip()
            match = character_line_regex.match(line_text)
            if match:
                if current_char_name_for_parse and current_dialogue_buffer:
                    dialogue_entries.append({"name": current_char_name_for_parse, "dialogue_text": " ".join(current_dialogue_buffer)})
                current_char_name_for_parse = match.group(1).strip()
                current_dialogue_buffer = []
                dialogue_on_same_line = match.group(2).strip()
                if dialogue_on_same_line: current_dialogue_buffer.append(dialogue_on_same_line)
            elif current_char_name_for_parse:
                if stripped_line: current_dialogue_buffer.append(stripped_line)
            elif not stripped_line and current_char_name_for_parse and current_dialogue_buffer:
                 dialogue_entries.append({"name": current_char_name_for_parse, "dialogue_text": " ".join(current_dialogue_buffer)})
                 current_dialogue_buffer = []
                 current_char_name_for_parse = None
        if current_char_name_for_parse and current_dialogue_buffer:
            dialogue_entries.append({"name": current_char_name_for_parse, "dialogue_text": " ".join(current_dialogue_buffer)})

        for entry_idx, entry in enumerate(dialogue_entries):
            if current_y + font_size_bold > target_height - top_margin: break
            character_name = entry["name"]
            dialogue_text = entry["dialogue_text"]
            if entry_idx > 0: current_y += line_spacing_after_block
            if current_y + font_size_bold > target_height - top_margin: break
            draw.text((left_margin, int(current_y)), f"{character_name}:", font=font_bold, fill=text_color, stroke_width=stroke_width_val, stroke_fill='black')
            current_y += font_size_bold + line_spacing_after_name
            if dialogue_text:
                wrapped_dialogue_lines = wrap_text_segment(dialogue_text, draw, font_regular, max_text_block_width)
                for dia_line_text in wrapped_dialogue_lines:
                    if current_y + font_size_regular > target_height - top_margin: break
                    draw.text((left_margin, int(current_y)), dia_line_text, font=font_regular, fill=text_color, stroke_width=stroke_width_val, stroke_fill='black')
                    current_y += font_size_regular + line_spacing_dialogue_line
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_base64

    except Exception as e:
        print(f"An error occurred while creating the image: {e}")
        print(traceback.format_exc())
        raise RuntimeError(f"An error occurred while creating the image: {e}")