import io
import json
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from PIL import Image as PILImage
import io
import uvicorn
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/vision-analyze")
async def vision_analyze(image: UploadFile = File(...)):
    try:
        
        contents = await image.read()

       
        prompt = """
Ini adalah gambar struk pembelian.
Silakan ekstrak 
Kita hitung ulang berdasarkan total yang dibayar dibagi jumlah masing-masing item.
Semua harga dibagi per item unik, tidak boleh duplikat, dan harga satuan sudah termasuk pajak.
- "item": nama barang
 
- "price": harga satuan  

Kembalikan hanya JSON-nya saja seperti contoh ini:
[
  { "item": "MIE GACOAN LV 2", "price": 12000 }, 
  { "item": "ES TEH", "price": 5000 } ]

"""
        try:

            image_obj = PILImage.open(io.BytesIO(contents))

            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[prompt, image_obj]
            )
        except Exception as pil_error:
          
            import base64
            image_b64 = base64.b64encode(contents).decode('utf-8')

            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=[
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": image.content_type,
                                    "data": image_b64
                                }
                            }
                        ]
                    }
                ]
            )

        
        result_text = response.text.strip()

     
        start = result_text.find("[")
        end = result_text.rfind("]") + 1

        if start == -1 or end == 0:
            raise HTTPException(
                status_code=500, detail="No valid JSON found in response")

        json_string = result_text[start:end]
        parsed_result = json.loads(json_string)

        # 6. Kirim ke frontend
        return {
            "result": parsed_result,
            "raw_response": result_text  # Optional: untuk debugging
        }

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"JSON parsing error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing image: {str(e)}")



@app.get("/")
async def root():
    return {"message": "Gemini Vision API is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
