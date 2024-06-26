from fpdf import FPDF, XPos, YPos
import json
import os
from django.conf import settings


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_added = False
        self.pagination = False

    def header(self):
        if not self.header_added:
            # Set the font for the header
            self.set_font('DejaVu', 'B', 20)
            self.core_fonts_encoding = 'utf-8'
            # Calculate the width of the title and position it centrally
            title_w = self.get_string_width(self.title) + 6
            doc_w = self.w
            self.set_x((doc_w - title_w) / 2)
            # Set the colors for the frame, background, and text
            self.set_draw_color(128, 128, 128)  # border = gray
            self.set_fill_color(245, 245, 245)  # background = light gray
            self.set_text_color(0, 0, 0)  # text = black
            # Set the thickness of the frame (border)
            self.set_line_width(0.5)
            # Add the title cell with the specified properties
            self.cell(title_w, 25, self.title, border=1, new_x=XPos.LMARGIN,
                      new_y=YPos.NEXT, align='C', fill=1)
            # Add a line break after the title
            self.ln(10)
            self.header_added = True

    def footer(self):
        if self.pagination:
            # Set the position of the footer
            self.set_y(-15)
            # Set the font for the footer
            self.set_font('helvetica', 'I', 8)
            # Set the text color to grey
            self.set_text_color(169, 169, 169)
            # Add the page number in the footer
            self.cell(0, 10, f'Page {self.page_no()-1}', align='C')
        self.pagination = True

    def chapter_title(self, ch_num, ch_title, link):
        # Set the link location for the chapter title if provided
        if link:
            self.set_link(link)
        # Set the font for the chapter title
        self.set_font('DejaVu', 'B', 16)
        # Set the background color for the chapter title
        self.set_fill_color(245, 245, 245)
        # Create the chapter title text
        chapter_title = f'{ch_title}: '
        # Add the chapter title cell with the specified properties
        self.cell(0, 8, chapter_title, new_x=XPos.LMARGIN,
                  new_y=YPos.NEXT, fill=1)
        # Add a line break after the chapter title
        self.ln()

    def chapter_body(self, content, chapter_subheading):

        # adding subheading
        self.set_font('DejaVu', 'I', 20)
        self.cell(0, 7, chapter_subheading, new_x=XPos.LMARGIN,
                  new_y=YPos.NEXT, fill=1)
        self.ln()
        # Set the font for the chapter body
        self.set_font('DejaVu', '', 14)
        # Insert the chapter text using multi_cell
        self.multi_cell(0, 8, content)
        # Add a line break after the chapter body
        self.ln()
        # Add "END OF CHAPTER" text at the end of each chapter
        # self.set_font('DejaVu', 'I', 12)
        # self.cell(0, 5, 'END OF CHAPTER', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def print_chapter(self, ch_num, ch_title, subheadings, link):
        # print(subheadings)
        # Add a new page for the chapter
        self.add_page()
        # Add the chapter title
        if link:
            self.chapter_title(ch_num, ch_title, link)
        else:
            self.chapter_title(ch_num, ch_title, None)
        # Add the chapter body
        for chapter_subheading, content in subheadings.items():
            self.chapter_body(content, chapter_subheading)


def create_pdf_from_dict(ebook_structure, title_image='title.png', author='Your Author Name'):
    # Extract title from the dictionary
    title = list(ebook_structure.keys())[0]
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a PDF object with portrait orientation, millimeter units, and Letter size
    pdf = PDF('P', 'mm', 'Letter')
    pdf.title = title  # Set the title attribute of the PDF object

    # Add fonts (assuming you have these font files in your directory)
    pdf.add_font('DejaVu', '', os.path.join(current_dir, 'DejaVuSans.ttf'))
    pdf.add_font('DejaVu', 'B', os.path.join(
        current_dir, 'DejaVuSans-Bold.ttf'))
    pdf.add_font('DejaVu', 'I', os.path.join(
        current_dir, 'DejaVuSansCondensed-Oblique.ttf'))

    # Set the metadata for the PDF
    pdf.set_title(title)
    # pdf.set_author(author)

    # Set auto page break with a margin of 15 units
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add a new page to the PDF
    pdf.add_page()

    # Add title image to the PDF
    pdf.image(title_image, x=-0.5, w=pdf.w + 1)

    # Add chapters to the PDF
    chapter_num = 1
    for chapter_title, subheadings in ebook_structure[title]['chapters'].items():
        pdf.print_chapter(chapter_num, chapter_title, subheadings, '')
        chapter_num += 1

    # Output the PDF to the specified file
    media_dir = os.path.join(settings.MEDIA_ROOT)
    os.makedirs(media_dir, exist_ok=True)
    # Output the PDF to a file
    pdf_filename = f'{title}.pdf'
    pdf_path = os.path.join(media_dir, pdf_filename)
    pdf.output(pdf_path)

    # Return the relative path from MEDIA_ROOT
    return os.path.relpath(pdf_path, settings.MEDIA_ROOT)


def generate_pdf_from_book(book):
    pdf = PDF('P', 'mm', 'Letter')
    pdf.title = book.title

    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Add fonts with the correct path
    pdf.add_font('DejaVu', '', os.path.join(current_dir, 'DejaVuSans.ttf'))
    pdf.add_font('DejaVu', 'B', os.path.join(
        current_dir, 'DejaVuSans-Bold.ttf'))
    pdf.add_font('DejaVu', 'I', os.path.join(
        current_dir, 'DejaVuSansCondensed-Oblique.ttf'))

    # Set the metadata for the PDF
    pdf.set_title(book.title)
    # Assuming your Book model has an author field
    # pdf.set_author(book.author)

    # Set auto page break with a margin of 15 units
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    # Add chapters to the PDF
    chapter_num = 1
    for chapter_title, subheadings in book.content.items():
        pdf.print_chapter(chapter_num, chapter_title, subheadings, '')
        chapter_num += 1

    media_dir = os.path.join(settings.MEDIA_ROOT)
    os.makedirs(media_dir, exist_ok=True)
    # Output the PDF to a file
    pdf_filename = f'{book.title}.pdf'
    pdf_path = os.path.join(media_dir, pdf_filename)
    pdf.output(pdf_path)

    # Return the relative path from MEDIA_ROOT
    return os.path.relpath(pdf_path, settings.MEDIA_ROOT)
