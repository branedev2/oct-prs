from fastapi import FastAPI,UploadFile,File
import shutil
from pathlib import Path

app=FastAPI()

@app.post('/UploadFile/')
# {fact rule=unrestricted-file-upload@v1.0 defects=1}
async def file(file:UploadFile=File(...)):
    #for create temporar  file path
    video_path=f"temp_{file.filename}"

    #for saving file temporary
# defect
    with open(video_path,'wb') as buffer:
        shutil.copyfileobj(file.file,buffer)
        

    

# {/fact}

