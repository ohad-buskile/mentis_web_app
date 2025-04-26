import os
local_model_path = r"C:\Users\ohad.buskile\OneDrive - Kaltura\Desktop\אפקה\פרוייקט גמר\mentis_web_updated\mentis_summarization\t5-small-local"

print(f"📂 Checking contents of: {local_model_path}")
for file in os.listdir(local_model_path):
    print("   🔸", file)
