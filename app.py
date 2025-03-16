import streamlit as st
import random
import unicodedata
import string
from tree_data import TREES, HELP_TEXT, DIFFICULTY_LEVELS

# Store session data in Streamlit state
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = {
        'correct_answers': 0,
        'total_questions': 0,
        'current_tree': None,
        'current_type': '',
        'current_answer': '',
        'difficulty': 'facile',  # Default difficulty
        'attempts': 0  # Track number of attempts for current question
    }

def normalize_answer(text):
    """Normalize text for comparison:
    - Remove accents
    - Convert to lowercase
    - Remove punctuation
    - Remove extra spaces
    - Handle singular/plural
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')

    # Remove punctuation
    text = ''.join(c for c in text if c not in string.punctuation)

    # Remove extra spaces
    text = ' '.join(text.split())

    # Handle singular/plural by removing trailing 's'
    text = text.rstrip('s')

    return text

def get_genus_species_count():
    """Count how many species exist for each genus"""
    genus_count = {}
    for _, genus, _, _ in TREES:
        genus_count[genus] = genus_count.get(genus, 0) + 1
    return genus_count

# Streamlit page setup
st.title("Quiz de Taxonomie des Arbres 🌳")
difficulty = st.selectbox("Sélectionne la difficulté :", list(DIFFICULTY_LEVELS.keys()))
st.session_state.quiz_data['difficulty'] = difficulty

# Generate a new question when the button is clicked
if st.button("Nouvelle Question"):
    st.session_state.quiz_data['attempts'] = 0
    tree = random.choice(TREES)
    st.session_state.quiz_data['current_tree'] = tree
    name, genus, species = tree[:3]  # Ignore image path for now

    # Check if this genus has multiple species
    genus_count = get_genus_species_count()
    has_multiple_species = genus_count[genus] > 1

    # All possible questions
    all_options = [
        ("nom français", "nom", name),
        ("genre (en latin)", "genre", genus) if not has_multiple_species else None,
        ("espèce (en latin)", "espèce", species)
    ]
    # Remove None values (when genre is excluded due to multiple species)
    all_options = [opt for opt in all_options if opt is not None]

    # Number of elements to guess based on difficulty
    num_questions = min(DIFFICULTY_LEVELS[st.session_state.quiz_data['difficulty']], len(all_options))

    # Randomly select which elements to ask
    selected_options = random.sample(all_options, num_questions)
    questions = []
    hints = []

    # Process each option as either a question or a hint
    for opt in all_options:
        if opt in selected_options:
            # Use "l'" instead of "le" for "espèce"
            question_text = f"l'{opt[0]}" if opt[0].startswith('e') else f"le {opt[0]}"
            questions.append(question_text)
            st.session_state.quiz_data[f'answer_{opt[1]}'] = opt[2]  # Store answer
        else:
            # Skip adding genre as hint if there are multiple species for this genus
            if has_multiple_species and opt[1] == 'genre':
                continue
            hints.append(f"🌳 {opt[0]}: {opt[2]}")

    # Join questions with proper French conjunction
    if len(questions) > 1:
        questions[-1] = "et " + questions[-1]
    question_text = ", ".join(questions)

    st.session_state.quiz_data['expected_answers'] = [opt[1] for opt in selected_options]

    st.write(f"Pour cet arbre, trouvez {question_text} :")
    st.write("Indices :")
    for hint in hints:
        st.write(hint)

# Check the submitted answers
answers = {}
answer = st.text_input("Votre réponse :")
if st.button("Valider"):
    answers = {key: answer for key in st.session_state.quiz_data['expected_answers']}
    if not answers:
        st.error('Veuillez entrer une réponse avant de valider.')
    else:
        st.session_state.quiz_data['attempts'] += 1
        show_answers = st.session_state.quiz_data['attempts'] >= 3  # Show answers after 3 attempts

        correct_count = 0
        results = {}

        # Check each expected answer
        for answer_type in st.session_state.quiz_data['expected_answers']:
            user_answer = normalize_answer(answers.get(answer_type, ''))
            correct_answer = normalize_answer(st.session_state.quiz_data[f'answer_{answer_type}'])

            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1

            results[answer_type] = {
                'is_correct': is_correct,
                'correct_answer': st.session_state.quiz_data[f'answer_{answer_type}'],
                'show_answer': show_answers  # Add flag to show answer after 3 attempts
            }

        # Only count as a completed question if either all answers are correct or we've used all attempts
        if correct_count == len(st.session_state.quiz_data['expected_answers']) or show_answers:
            st.session_state.quiz_data['total_questions'] += 1
            if correct_count == len(st.session_state.quiz_data['expected_answers']):
                st.session_state.quiz_data['correct_answers'] += 1

        percentage = int(st.session_state.quiz_data['correct_answers'] / st.session_state.quiz_data['total_questions'] * 100) if st.session_state.quiz_data['total_questions'] > 0 else 0

        st.write(f"Score: {st.session_state.quiz_data['correct_answers']}/{st.session_state.quiz_data['total_questions']} ({percentage}%)")

# Display help text
if st.button("Aide"):
    st.write(HELP_TEXT)
