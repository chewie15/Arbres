import streamlit as st
import random
import unicodedata
import string
from tree_data import TREES, HELP_TEXT, DIFFICULTY_LEVELS

# Initialisation de la session
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {
        "correct_answers": 0,
        "total_questions": 0,
        "current_tree": None,
        "difficulty": "facile",
        "attempts": 0,
        "expected_answers": []
    }

def normalize_answer(text):
    """Normalise le texte pour comparaison"""
    if not text:
        return ""

    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = ''.join(c for c in text if c not in string.punctuation)
    text = ' '.join(text.split())
    text = text.rstrip('s')

    return text

def get_new_question():
    """Génère une nouvelle question"""
    st.session_state.quiz_data["attempts"] = 0
    tree = random.choice(TREES)
    name, genus, species = tree[:3]

    st.session_state.quiz_data["current_tree"] = tree

    # Sélectionner une question en fonction du niveau
    question_type = random.choice(["nom", "genre", "espèce"])
    expected_answer = {"nom": name, "genre": genus, "espèce": species}[question_type]
    st.session_state.quiz_data["expected_answers"] = [(question_type, expected_answer)]

    return f"Quel est le {question_type} de cet arbre ?"

# Interface utilisateur Streamlit
st.title("Quiz de Taxonomie des Arbres 🌳")

# Choix de difficulté
difficulty = st.selectbox("Sélectionne la difficulté :", list(DIFFICULTY_LEVELS.keys()))
st.session_state.quiz_data["difficulty"] = difficulty

# Bouton pour nouvelle question
if st.button("Nouvelle Question"):
    question = get_new_question()
    st.session_state.quiz_data["question"] = question

# Afficher la question
if "question" in st.session_state.quiz_data:
    st.write(st.session_state.quiz_data["question"])
    answer = st.text_input("Votre réponse :")

    if st.button("Valider"):
        correct_type, correct_answer = st.session_state.quiz_data["expected_answers"][0]
        normalized_user_answer = normalize_answer(answer)
        normalized_correct_answer = normalize_answer(correct_answer)

        if normalized_user_answer == normalized_correct_answer:
            st.session_state.quiz_data["correct_answers"] += 1
            st.success("Bonne réponse ! 🎉")
        else:
            st.error(f"Mauvaise réponse 😢. La bonne réponse était : {correct_answer}")

        st.session_state.quiz_data["total_questions"] += 1

# Score
st.write(f"Score : {st.session_state.quiz_data['correct_answers']} / {st.session_state.quiz_data['total_questions']}")

# Afficher l'aide
if st.button("Besoin d'aide ?"):
    st.write(HELP_TEXT)
