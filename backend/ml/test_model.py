"""
ml/test_model.py — Test ML score against known result
Run: python ml/test_model.py from backend/
"""

from predict import get_ml_score

# Your actual resume text (shortened for test)
resume_text = """
Swastiek Kala - ML/AI enthusiast
Skills: Python, JavaScript, SQL, Java
Frameworks: Next.js, React.js, Flask, Node.js
ML/GenAI: LangChain, Qdrant, OpenAI API, Gemini API, scikit-learn, NLP, RAG
Databases: MongoDB, MySQL, PostgreSQL
Projects:
- Semantic Document RAG Chatbot using LangChain, Qdrant, OpenAI, Gemini, Ollama
- Full-Stack Authentication System with Node.js, Express, MongoDB, JWT
- PDF Toolkit deployed on Render using Flask
Education: B.Tech Computer Science (Data Science), Manipal University Jaipur, CGPA 8.74
"""

# Infosys InStep JD
jd_text = """
InStep Global Internship Program by Infosys.
Positions: Software Engineering, Artificial Intelligence, Machine Learning, 
Data Analytics, Cybersecurity.
Skills required: Programming, AI/ML, Data Analysis, Software Engineering.
Currently pursuing Bachelor's or Master's in Computer Science or related field.
Hands-on projects in cutting-edge technologies.
"""

score = get_ml_score(resume_text, jd_text)
print(f"\nML Score       : {score:.4f}")
print(f"As percentage  : {round(score * 100)}%")
print(f"ChatGPT score  : 60%")
print(f"Difference     : {abs(round(score * 100) - 60)}%")