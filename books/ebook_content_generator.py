from openai import OpenAI
import json
import re
import requests
import os
from django.conf import settings


class EbookCreator:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.SECRET_KEY)

    def create_chapters_for_title(self, language, ebook_title, chapters, subchapters):
        print(f"Creating chapters for the eBook titled '{ebook_title}'")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens=3000,
            temperature=0.7,
            messages=[
                {"role": "system", "content": f"You are a creative {language} eBook writer. Give the output as JSON and in {language} language."},
                {"role": "user", "content": f"Write the chapters and subheadings for the {language} ebook titled '{ebook_title}'. Make the chapter names as keys and the list of subheadings as values. Give at least {chapters} chapters and {subchapters} subheadings for each chapters."}
            ]
        )
        chapters_structure = json.loads(response.choices[0].message.content)
        ebook_structure = {ebook_title: {'chapters': {}}}

        for chapter, subheadings in chapters_structure.items():
            ebook_structure[ebook_title]['chapters'][chapter] = {}
            for subheading in subheadings:
                ebook_structure[ebook_title]['chapters'][chapter][subheading] = ""

        with open("ebook_structure.json", "w") as chapters_file:
            json.dump(ebook_structure, chapters_file, indent=4)

    def create_chapter_content(self, ebook_title, chapter, subheading, language):
        print("-" * 50)
        print(
            f"Creating content for chapter '{chapter}' with subheading '{subheading}'")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens=3000,
            temperature=0.7,
            messages=[
                {"role": "system", "content": f"You are a creative eBook writer. The title of the eBook you are writing is '{ebook_title}'. Each chapter of the eBook has subheadings."},
                {"role": "user", "content": f"Write the text content in {language} language for the subheading titled '{subheading}' under the chapter titled '{chapter}'. Be elaborate and clear. Do not include the chapter name and subheading in the response."}
            ]
        )
        content = response.choices[0].message.content

        # Clean the response content to remove chapter and subheading info if included
        # Remove 'Chapter [number]: ...' line if it exists
        content = re.sub(r'Chapter \d+: .*?\n', '', content).strip()
        # Remove 'Subheading: ...' line if it exists
        content = re.sub(r'Subheading: .*?\n', '', content).strip()
        # Remove the subheading text at the beginning if it exists
        content = re.sub(r'^' + re.escape(subheading) +
                         r'\n+', '', content).strip()

        # Read the existing JSON file
        with open("ebook_structure.json", "r") as chapters_file:
            ebook_structure = json.load(chapters_file)

        # Update the JSON structure with the new content
        if ebook_title in ebook_structure and chapter in ebook_structure[ebook_title]['chapters']:
            ebook_structure[ebook_title]['chapters'][chapter][subheading] = content
        else:
            print(
                "Error: The specified chapter or subheading does not exist in the current ebook structure.")

        # Save the updated JSON structure back to the file
        with open("ebook_structure.json", "w") as chapters_file:
            json.dump(ebook_structure, chapters_file, indent=4)

        print(f"Updated ebook structure saved in 'ebook_structure.json'")
        return content

    def populate_ebook_content(self, ebook_title, language):
        # Read the existing JSON file
        with open("ebook_structure.json", "r") as chapters_file:
            ebook_structure = json.load(chapters_file)

        # Check if the ebook title exists in the structure
        if ebook_title not in ebook_structure:
            print(
                f"Error: The ebook titled '{ebook_title}' does not exist in the current ebook structure.")
            return

        # Iterate over the chapters and subheadings
        chapters = ebook_structure[ebook_title]['chapters']
        for chapter in chapters:
            subheadings = chapters[chapter]
            for subheading in subheadings:
                content = self.create_chapter_content(
                    ebook_title, chapter, subheading, language=language)
                # Update the structure with the new content
                ebook_structure[ebook_title]['chapters'][chapter][subheading] = content

        # Save the updated JSON structure back to the file
        with open("ebook_structure.json", "w") as chapters_file:
            json.dump(ebook_structure, chapters_file, indent=4)
        return ebook_structure

    def save_image_from_openai(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1, filename="output.png"):

        prompt = f"Generate an cover image for book called '{prompt}' avoiding any text or textual elements such as signs, letters, or written words."

        response = self.client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )

        image_url = response.data[0].url

        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            file_path = os.path.join('book_covers', filename)
            with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb') as f:
                f.write(image_response.content)
            print(f"Image saved as '{file_path}'")
            return True
        else:
            print("Failed to download the image")
            return False

    def create_subchapter_content(self, ebook_title, chapter, subheading, language):
        print("-" * 50)
        print(
            f"Creating content for chapter '{chapter}' with subheading '{subheading}'")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            max_tokens=3000,
            temperature=0.7,
            messages=[
                {"role": "system", "content": f"You are a creative {language} eBook writer. The title of the eBook you are writing is '{ebook_title}'. Each chapter of the eBook has subheadings."},
                {"role": "user", "content": f"Write the text content in {language} for the subheading titled '{subheading}' under the chapter titled '{chapter}'. Be elaborate and clear. Do not include the chapter name and subheading in the response."}
            ]
        )
        content = response.choices[0].message.content
        return content

    def create_all_ebook_content(self, title, language, chapters, subchapters):
        self.save_image_from_openai(
            title, filename=f"{title.replace(' ', '_')}.png")
        self.create_chapters_for_title(
            ebook_title=title, language=language, chapters=chapters, subchapters=subchapters)
        self.populate_ebook_content(title, language=language)
