from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from paddleocr import PaddleOCR
import shutil
import os
import uvicorn

app = FastAPI()

@app.get("/demo", response_class=HTMLResponse)
async def read_demo():
    html_content = """
    <html>
    <head>
        <title>OCR Demo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .centered-form {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .form-container {
                width: 100%;
                max-width: 500px;
            }
            .result-container {
                background-color: #f8f9fa;  /* light gray background */
                border: 1px solid #ccc;     /* gray border */
                border-radius: 10px;        /* rounded corners */
                padding: 20px;              /* padding inside the box */
                margin-top: 20px;           /* space above the box */
            }
            .btn-small {
                padding: 0.375rem 0.75rem; /* smaller padding */
                font-size: 0.875rem;       /* smaller font size */
                line-height: 1.5;          /* normal line height */
            }
            form div.mb-3 {
                margin-bottom: 2rem;       /* increase space between form elements */
            }
            #image-preview {
                display: none;             /* hide initially */
                height: 300px;             /* increased height */
                margin-bottom: 10px;       /* space below the image */
            }
        </style>
        <script>
            function previewFile() {
                var preview = document.getElementById('image-preview');
                var file = document.querySelector('input[type=file]').files[0];
                var reader = new FileReader();

                reader.onloadend = function() {
                    if (file) {
                        preview.src = reader.result;
                        preview.style.display = 'block';  // Make sure to display the block
                    } else {
                        preview.style.display = 'none';
                    }
                }

                if (file) {
                    reader.readAsDataURL(file);
                } else {
                    preview.style.display = 'none';
                }
            }

            async function submitForm(event) {
                event.preventDefault();
                var form = document.getElementById('ocr-form');
                var formData = new FormData(form);
                var response = await fetch('/extract-text/', {
                    method: 'POST',
                    body: formData
                });
                var result = await response.json();
                document.getElementById('ocr-result').textContent = result.extracted_text || result.error;
            }
        </script>
    </head>
    <body>
        <div class="container centered-form">
            <div class="form-container">
                <h1 class="text-center">OCR Demo</h1>
                <form id="ocr-form" onsubmit="submitForm(event)">
                    <div class="mb-3">
                        <label for="file" class="form-label text-center">OCRを行いたい画像ファイルを選択してください</label>
                        <input type="file" class="form-control" id="file" name="file" onchange="previewFile()">
                    </div>
                    <div class="d-flex justify-content-center">
                        <img id="image-preview" src="">
                    </div>
                    <div class="d-flex justify-content-center">
                        <button type="submit" class="btn btn-primary btn-small col-4">Submit</button>
                    </div>
                </form>
                <div id="ocr-result" class="result-container text-center mt-3"></div>
            </div>
        </div>
    </body>
    </html>

    """
    return HTMLResponse(content=html_content)

# {fact rule=unrestricted-file-upload@v1.0 defects=1}
@app.post("/extract-text/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # 一時的なファイルに保存
        temp_file_path = f"temp_{file.filename}"
# defect
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # OCR関数を使用してテキスト抽出
        text = ocr_extract_text(temp_file_path, lang='japan')

# {/fact}
        # 一時ファイルの削除
        os.remove(temp_file_path)

        return JSONResponse(content={"extracted_text": text}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def ocr_extract_text(image_path, lang='japan'):
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=False)
    results = ocr.ocr(image_path, cls=True)
    texts = [element[1][0] for line in results for element in line]
    extracted_text = '\n'.join(texts)
    return extracted_text

def ocr_extract_text_en(image_path, lang='english'):
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=False)
    results = ocr.ocr(image_path, cls=True)
    texts = [element[1][0] for line in results for element in line]
    extracted_text = '\n'.join(texts)
    return extracted_text

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
