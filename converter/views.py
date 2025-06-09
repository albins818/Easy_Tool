from django.shortcuts import render
from django.http import HttpResponse
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from docx import Document
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from PIL import Image
import fitz
import zipfile
import shutil
from docx import Document
from pdf2docx import Converter
from PyPDF2 import PdfReader, PdfWriter
from docx2pdf import convert
import pikepdf




def home(request):
    return render(request, 'converter/home.html')

def word_to_pdf(request):
    return HttpResponse("Convert Word to PDF feature")

def image_to_pdf(request):
    return HttpResponse("Convert Image to PDF feature")

def pdf_to_image(request):
    return HttpResponse("Convert PDF to Image feature")

def pdf_to_word(request):
    return HttpResponse("Convert PDF to Word feature")

def extract_pdf(request):
    return HttpResponse("Extract text/images from PDF feature")

def delete_pages(request):
    return HttpResponse("Delete pages from PDF feature")
def word_to_pdf(request):
    if request.method == 'POST' and request.FILES.get('word_file'):
        word_file = request.FILES['word_file']
        fs = FileSystemStorage()
        filename = fs.save(word_file.name, word_file)
        input_path = fs.path(filename)

        # Convert using docx2pdf (Windows only)
        output_path = input_path.replace(".docx", "_converted.pdf")
        try:
            convert(input_path, output_path)
            with open(output_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=converted.pdf'

            # Clean up
            os.remove(input_path)
            os.remove(output_path)
            return response

        except Exception as e:
            return HttpResponse(f"Conversion failed: {str(e)}", status=500)

    return render(request, 'converter/word_to_pdf.html')

# Create your views here.


def word_to_pdf(request):
    if request.method == 'POST' and request.FILES.get('word_file'):
        word_file = request.FILES['word_file']
        fs = FileSystemStorage()
        filename = fs.save(word_file.name, word_file)
        input_path = fs.path(filename)

        # Convert using docx2pdf (Windows only)
        output_path = input_path.replace(".docx", "_converted.pdf")
        try:
            convert(input_path, output_path)
            with open(output_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=converted.pdf'

            # Clean up
            os.remove(input_path)
            os.remove(output_path)
            return response

        except Exception as e:
            return HttpResponse(f"Conversion failed: {str(e)}", status=500)

    return render(request, 'converter/word_to_pdf.html')

def image_to_pdf(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        image_objs = []

        fs = FileSystemStorage()
        for img in images:
            filename = fs.save(img.name, img)
            img_path = fs.path(filename)
            img_obj = Image.open(img_path).convert('RGB')
            image_objs.append(img_obj)

        if image_objs:
            buffer = BytesIO()
            first_image = image_objs[0]
            rest = image_objs[1:]
            first_image.save(buffer, format='PDF', save_all=True, append_images=rest)

            # Cleanup uploaded images
            for img in images:
                os.remove(fs.path(img.name))

            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')

    return render(request, 'converter/image_to_pdf.html')
def compress_pdf_images_only(file_like_obj):
    doc = fitz.open(stream=file_like_obj.read(), filetype="pdf")
    new_pdf = fitz.open()

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=100)  # Downsample

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_buffer = BytesIO()
        img.save(img_buffer, format="JPEG", quality=30, optimize=True)
        img_buffer.seek(0)

        # Create new page and insert image
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        new_page = new_pdf.new_page(width=pix.width, height=pix.height)
        new_page.insert_image(rect, stream=img_buffer.getvalue())

    output_buffer = BytesIO()
    new_pdf.save(output_buffer)
    new_pdf.close()
    doc.close()

    output_buffer.seek(0)
    return output_buffer



def compress_docx(input_path):
    tmp_dir = 'tmp_docx_extract'
    os.makedirs(tmp_dir, exist_ok=True)

    with zipfile.ZipFile(input_path, 'r') as zin:
        zin.extractall(tmp_dir)

    media_dir = os.path.join(tmp_dir, 'word', 'media')
    if os.path.exists(media_dir):
        for img_file in os.listdir(media_dir):
            img_path = os.path.join(media_dir, img_file)
            try:
                if os.path.getsize(img_path) > 50 * 1024:
                    img = Image.open(img_path)
                    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
                    img.save(img_path, optimize=True, quality=20)
            except Exception:
                continue

    compressed_io = BytesIO()
    with zipfile.ZipFile(compressed_io, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for foldername, _, filenames in os.walk(tmp_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, tmp_dir)
                zout.write(file_path, arcname)

    shutil.rmtree(tmp_dir)
    compressed_io.seek(0)
    return compressed_io


def recompress_xlsx(input_path):
    tmp_dir = 'tmp_xlsx_extract'
    os.makedirs(tmp_dir, exist_ok=True)

    with zipfile.ZipFile(input_path, 'r') as zin:
        zin.extractall(tmp_dir)

    compressed_io = BytesIO()
    with zipfile.ZipFile(compressed_io, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for foldername, _, filenames in os.walk(tmp_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, tmp_dir)
                zout.write(file_path, arcname)

    shutil.rmtree(tmp_dir)
    compressed_io.seek(0)
    return compressed_io


def compress_file(request):
    if request.method == 'POST' and request.FILES.get('upload_file'):
        uploaded_file = request.FILES['upload_file']
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        input_path = fs.path(filename)

        try:
            # Load file into memory to avoid locking issues
            with open(input_path, 'rb') as f:
                file_data = f.read()
            original_size = len(file_data)

            # Process file based on extension
            if file_ext == '.pdf':
                buffer = compress_pdf_images_only(BytesIO(file_data))
            elif file_ext in ['.docx', '.xlsx']:
                # Re-save to temp path for zip-based processing
                with open(input_path, 'wb') as f:
                    f.write(file_data)
                buffer = compress_docx(input_path) if file_ext == '.docx' else recompress_xlsx(input_path)
            else:
                os.remove(input_path)
                return HttpResponse("Unsupported file type. Upload .pdf, .docx, or .xlsx only.", status=400)

            compressed_size = buffer.getbuffer().nbytes
            reduction = round((original_size - compressed_size) * 100 / original_size, 2)
            print(f"Compressed {uploaded_file.name}: {original_size} ➜ {compressed_size} bytes ({reduction}% smaller)")

        except Exception as e:
            try:
                os.remove(input_path)
            except Exception:
                pass
            return HttpResponse(f"Compression error: {str(e)}", status=500)

        try:
            os.remove(input_path)
        except Exception:
            pass

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename=compressed{file_ext}'
        return response

    return render(request, 'converter/compress_file.html')
def pdf_to_image(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        uploaded_pdf = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_pdf.name, uploaded_pdf)
        input_path = fs.path(filename)

        try:
            doc = fitz.open(input_path)
            image_files = []

            for page_number in range(len(doc)):
                page = doc.load_page(page_number)
                pix = page.get_pixmap(dpi=150)
                img_io = BytesIO()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(img_io, format='PNG')
                img_io.seek(0)
                image_files.append((f"page_{page_number + 1}.png", img_io.read()))

            doc.close()
            os.remove(input_path)

            # Create ZIP archive
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for name, data in image_files:
                    zip_file.writestr(name, data)

            zip_buffer.seek(0)
            return HttpResponse(
                zip_buffer,
                content_type='application/zip',
                headers={'Content-Disposition': 'attachment; filename=pdf_images.zip'}
            )

        except Exception as e:
            return HttpResponse(f"Error converting PDF to images: {str(e)}", status=500)

    return render(request, 'converter/pdf_to_image.html')
def pdf_to_word(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        uploaded_pdf = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_pdf.name, uploaded_pdf)
        input_path = fs.path(filename)

        try:
            output_path = input_path.replace('.pdf', '_converted.docx')
            cv = Converter(input_path)
            cv.convert(output_path, start=0, end=None)
            cv.close()

            with open(output_path, 'rb') as docx_file:
                data = docx_file.read()

            # Clean up files
            os.remove(input_path)
            os.remove(output_path)

            response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = 'attachment; filename=converted.docx'
            return response

        except Exception as e:
            return HttpResponse(f"Error converting PDF to Word: {str(e)}", status=500)

    return render(request, 'converter/pdf_to_word.html')


def extract_from_pdf(request):
    extracted_text = ""

    if request.method == 'POST' and request.FILES.get('pdf_file'):
        uploaded_pdf = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_pdf.name, uploaded_pdf)
        input_path = fs.path(filename)

        try:
            doc = fitz.open(input_path)
            for page in doc:
                extracted_text += page.get_text() + "\n\n"
            doc.close()
            os.remove(input_path)

        except Exception as e:
            return HttpResponse(f"Error extracting text: {str(e)}", status=500)

    return render(request, 'converter/extract_from_pdf.html', {'extracted_text': extracted_text})
def delete_pdf_pages(request):
    if request.method == 'POST' and request.FILES.get('pdf_file') and request.POST.get('pages_to_delete'):
        uploaded_pdf = request.FILES['pdf_file']
        pages_to_delete = request.POST.get('pages_to_delete')  # Example input: 2,4,5
        fs = FileSystemStorage()
        filename = fs.save(uploaded_pdf.name, uploaded_pdf)
        input_path = fs.path(filename)

        try:
            doc = fitz.open(input_path)
            total_pages = len(doc)

            # Parse page numbers, convert to zero-based, and remove duplicates
            delete_pages = sorted(set([
                int(p.strip()) - 1 for p in pages_to_delete.split(',') if p.strip().isdigit()
            ]), reverse=True)

            # Remove pages in reverse order
            for p in delete_pages:
                if 0 <= p < total_pages:
                    doc.delete_page(p)

            output = BytesIO()
            doc.save(output)
            doc.close()
            os.remove(input_path)

            output.seek(0)
            return HttpResponse(output, content_type='application/pdf', headers={
                'Content-Disposition': 'attachment; filename=modified.pdf'
            })

        except Exception as e:
            return HttpResponse(f"Error deleting pages: {str(e)}", status=500)

    return render(request, 'converter/delete_pdf_pages.html')

def protect_pdf(request):
    if request.method == 'POST' and request.FILES.get('pdf_file') and request.POST.get('password'):
        uploaded_pdf = request.FILES['pdf_file']
        password = request.POST.get('password')
        fs = FileSystemStorage()
        filename = fs.save(uploaded_pdf.name, uploaded_pdf)
        input_path = fs.path(filename)

        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            output = BytesIO()
            writer.write(output)
            output.seek(0)

            os.remove(input_path)

            return HttpResponse(
                output,
                content_type='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=protected.pdf'}
            )

        except Exception as e:
            return HttpResponse(f"Error protecting PDF: {str(e)}", status=500)

    return render(request, 'converter/protect_pdf.html')
