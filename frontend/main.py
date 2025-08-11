import streamlit as st
import requests
from typing import Dict, Any
import time

# =========================
# CONFIGURATION
# =========================
st.set_page_config(
    page_title="AI Study Helper",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8001"  # Change to your API URL

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .question-box {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNCTIONS
# =========================
def make_api_request(endpoint: str, method: str = "GET", **kwargs) -> Dict[Any, Any]:
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "POST":
            response = requests.post(url, **kwargs)
        else:
            response = requests.get(url, **kwargs)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Impossible de se connecter à l'API. Assurez-vous que le serveur FastAPI tourne sur le port 8001."}
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return {"success": False, "error": f"Erreur API: {error_detail}"}
    except Exception as e:
        return {"success": False, "error": f"Erreur inattendue: {str(e)}"}

def upload_pdf(file) -> Dict[Any, Any]:
    files = {"file": (file.name, file, "application/pdf")}
    return make_api_request("upload", method="POST", files=files)

def generate_quiz(topic: str, num_questions: int) -> Dict[Any, Any]:
    data = {"topic": topic, "num_questions": num_questions}
    return make_api_request("generate_quiz", method="POST", data=data)

def extract_option_text(option: str) -> str:
    """Extract option text, removing prefix like 'A. ', 'B. ', etc."""
    if len(option) >= 3 and option[1:3] == ". " and option[0].isalpha():
        return option[3:].strip()
    return option.strip()

def get_correct_answer_text(question: Dict) -> str:
    """Get the correct answer text based on question type"""
    if question["type"] == "mcq":
        answer_index = question["answer"]
        if isinstance(answer_index, int) and 0 <= answer_index < len(question["options"]):
            return extract_option_text(question["options"][answer_index])
        return "Réponse non trouvée"
    elif question["type"] == "true_false":
        return "Vrai" if question["answer"] else "Faux"
    else:  # short_answer
        return question.get("explanation", "Voir explication")

def check_answer_correctness(user_answer: str, question: Dict) -> bool:
    """Check if user answer is correct"""
    if not user_answer or user_answer == "Non répondu":
        return False
    
    if question["type"] == "mcq":
        correct_text = get_correct_answer_text(question)
        return user_answer.strip() == correct_text.strip()
    elif question["type"] == "true_false":
        correct_answer = "Vrai" if question["answer"] else "Faux"
        return user_answer.strip() == correct_answer.strip()
    else:  # short_answer - we can't automatically grade these
        return None  # Neither correct nor incorrect

# =========================
# SESSION STATE
# =========================
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "upload_success" not in st.session_state:
    st.session_state.upload_success = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = 0  # 0: Upload, 1: Quiz, 2: Results

# =========================
# HEADER
# =========================
st.markdown("""
<div class="main-header">
    <h1>📚 AI Study Helper</h1>
    <p>Téléversez un PDF, générez un quiz, et révisez vos réponses !</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Configuration")
    quiz_topic = st.text_input("Sujet du Quiz", value="général")
    num_questions = st.slider("Nombre de questions", min_value=1, max_value=20, value=5)

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📤 Téléverser PDF", "❓ Générer Quiz", "📊 Résultats"])

# ---- UPLOAD TAB ----
with tab1:
    uploaded_file = st.file_uploader("Choisissez un fichier PDF", type="pdf")

    if uploaded_file is not None:
        if st.button("🚀 Traiter le PDF", type="primary"):
            with st.spinner("Traitement du PDF..."):
                result = upload_pdf(uploaded_file)

            if result["success"]:
                st.session_state.upload_success = True
                st.success("✅ PDF traité avec succès ! Génération du quiz...")
                quiz_result = generate_quiz(quiz_topic, num_questions)
                if quiz_result["success"]:
                    st.session_state.quiz_data = quiz_result["data"]
                    st.session_state.quiz_submitted = False
                    st.session_state.active_tab = 1
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la génération du quiz : {quiz_result['error']}")
            else:
                st.error(result["error"])

# ---- QUIZ TAB ----
with tab2:
    if not st.session_state.upload_success:
        st.warning("⚠️ Veuillez téléverser un PDF d'abord.")
    else:
        if st.session_state.quiz_data:
            st.subheader("📝 Questions du Quiz")
            quiz_data = st.session_state.quiz_data

            if "questions" in quiz_data:
                questions = quiz_data["questions"]
                with st.form("quiz_form"):
                    user_answers = {}
                    for i, question in enumerate(questions):
                        st.markdown(f"**Question {i+1}:** {question['question']}")
                        
                        if question["type"] == "mcq":
                            # Extract clean option texts for display
                            clean_options = [extract_option_text(opt) for opt in question["options"]]
                            selected_index = st.radio(
                                "Votre réponse :", 
                                range(len(clean_options)),
                                format_func=lambda x: clean_options[x],
                                index=None, 
                                key=f"q_{i}"
                            )
                            # Store the selected text, not the index
                            user_answers[f"question_{i}"] = clean_options[selected_index] if selected_index is not None else None
                            
                        elif question["type"] == "true_false":
                            user_answers[f"question_{i}"] = st.radio(
                                "Votre réponse :", 
                                ["Vrai", "Faux"], 
                                index=None, 
                                key=f"q_{i}"
                            )
                            
                        else:  # short_answer
                            user_answers[f"question_{i}"] = st.text_area(
                                "Votre réponse :", 
                                key=f"q_{i}"
                            )

                    submitted = st.form_submit_button("📤 Soumettre")
                    if submitted:
                        st.session_state.user_answers = user_answers
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_submitted = True
                        st.session_state.active_tab = 2
                        st.rerun()

# ---- RESULTS TAB ----
with tab3:
    if not st.session_state.quiz_submitted:
        st.info("Soumettez un quiz pour voir la revue ici.")
    else:
        st.subheader("📋 Revue de vos réponses")
        questions = st.session_state.quiz_questions
        user_answers = st.session_state.user_answers
        
        # Calculate score
        total_questions = len(questions)
        correct_answers = 0
        gradable_questions = 0  # Questions that can be automatically graded

        for i, q in enumerate(questions):
            st.markdown(f"**Question {i+1}:** {q['question']}")
            user_ans = user_answers.get(f"question_{i}")
            
            # Display user answer
            if user_ans is None or user_ans == "":
                st.markdown("**Votre réponse:** *Non répondu*")
                user_ans = "Non répondu"
            else:
                st.markdown(f"**Votre réponse:** {user_ans}")

            # Display correct answer
            correct_ans = get_correct_answer_text(q)
            st.markdown(f"**Réponse correcte:** {correct_ans}")

            # Display explanation if available
            if q.get("explanation"):
                st.markdown(f"**Explication:** {q['explanation']}")

            # Check correctness and display result
            is_correct = check_answer_correctness(user_ans, q)
            
            if q["type"] in ["mcq", "true_false"]:
                gradable_questions += 1
                if is_correct:
                    correct_answers += 1
                    st.success("✅ Correct")
                else:
                    st.error("❌ Incorrect")
            else:  # short_answer
                st.info("📝 Réponse ouverte - Vérifiez avec l'explication ci-dessus")
                
            st.divider()

        # Display score summary
        if gradable_questions > 0:
            score_percentage = (correct_answers / gradable_questions) * 100
            st.markdown("---")
            st.markdown(f"### 📊 Score Final")
            st.markdown(f"**{correct_answers}/{gradable_questions}** questions correctes ({score_percentage:.1f}%)")
            
            # Score interpretation
            if score_percentage >= 80:
                st.success("🎉 Excellent travail !")
            elif score_percentage >= 60:
                st.info("👍 Bon travail, mais il y a de la place pour l'amélioration.")
            else:
                st.warning("📚 Continuez à étudier, vous pouvez faire mieux !")

# ---- FOOTER ----
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📚 PDF Quiz Generator | Construit avec Streamlit & FastAPI</p>
</div>
""", unsafe_allow_html=True)