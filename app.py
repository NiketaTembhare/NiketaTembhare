from flask import Flask, render_template, request, jsonify
from plagiarism_detection import detect_plagiarism

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_plagiarism():
    input_text = request.form.get("text")
    
    if not input_text:
        return jsonify({"error": "Please enter some text to check plagiarism."})
    
    result = detect_plagiarism(input_text)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
