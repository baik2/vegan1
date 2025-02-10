from flask import Flask, request, render_template, jsonify
import pandas as pd
import json
from openai import OpenAI

app = Flask(__name__)

# OpenAI API 설정 
client = OpenAI(api_key=)

# 엑셀 파일 로드
file_path = "vegetarian_substitutes_translated.xlsx"
df = pd.read_excel(file_path)

# 채식 대체 식재료 매핑
substitutes_dict = {
   row["동물성 식재료"].strip().lower(): row["채식 대체 식품"].strip()
   for _, row in df.iterrows()
}

# HTML 렌더링
@app.route('/')
def index():
   return render_template("index.html")

# JSON 데이터 처리 API
@app.route('/convert', methods=['POST'])
def convert():
   data = request.get_json()
   
   if not data or "counts" not in data:
      return jsonify({"error": "Invalid input JSON"}), 400
   
   # 동물성 식재료 대체 리스트 매칭
   output_dict = {
      key: substitutes_dict[key] for key in data["counts"] if key in substitutes_dict
      }
   
   return jsonify(output_dict)

# OpenAI API를 사용하여 추가 추천
@app.route('/recommend', methods=['POST'])
def recommend():
   data = request.get_json()
   
   if not data or "counts" not in data:
      return jsonify({"error": "Invalid input JSON"}), 400
   
   output_json = json.dumps(data, ensure_ascii=False, indent=2)
   
   with open("chaesiktak_prompt.txt", "r", encoding="utf-8") as file:
      prompt_template = file.read()
      
      prompt = prompt_template.format(output_json=output_json, input_json=data)
      
      completion = client.chat.completions.create(
         model="gpt-3.5-turbo-1106",
         messages=[{"role": "user", "content": prompt}]
         )
      
      response_text = completion.choices[0].message.content
      return jsonify({"recommendation": response_text})

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)
