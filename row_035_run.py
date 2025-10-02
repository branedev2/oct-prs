#!/usr/bin/python
# -*- coding:utf-8 -*-
import epaper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import logging
from PIL import Image
import os
import shutil

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# {fact rule=unrestricted-file-upload@v1.0 defects=1}
EINK_MODEL = 'epd7in5b_V2'

@app.post("/upload")
async def upload_bmp(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
# defect
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        epd = epaper.epaper(EINK_MODEL).EPD()  
        logging.info("init and Clear")
# {/fact}
        epd.init()
        # epd.Clear()

        # Sample image
        logging.info("Drawing bmp")
        Himage = Image.open(file_location)
        epd.display(epd.getbuffer(Himage), epd.getbuffer(Himage))

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epaper.epaper(EINK_MODEL).epdconfig.module_exit()
        exit()


    return {"filename": file.filename}

@app.get("/health")
async def health_status():
    return JSONResponse(content={"status": "ok"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

