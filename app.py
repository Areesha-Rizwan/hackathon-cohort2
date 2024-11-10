import streamlit as st
from groq import Groq

# Initialize Groq API
GROQ_API_KEY = st.secrets.key.G_api
client = Groq(api_key=GROQ_API_KEY)

# Streamlit app setup
st.title("Job Interview Assistant")
st.write("Select a field for your interview preparation.")

# Field input
field = st.text_input("Enter the field of interview (e.g., Data Science, Software Engineering)")
question_count = st.slider("Number of questions", min_value=10, max_value=15, value=10)

# Initialize session state for questions, answers, feedback, and current question index
if "questions" not in st.session_state:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.feedbacks = []
    st.session_state.current_question = 0
    st.session_state.show_next_question = False

# Generate first question if field is specified
if field and st.session_state.current_question < question_count:
    if not st.session_state.questions:
        # Generate the first question, which should not be a follow-up
        initial_prompt = (
            f"Generate an interview question in the field of {field}. "
            "This question should be an introductory question, not based on previous questions or answers. "
            "Directly go to the question without stating that it is the beginning of the interview or following the provided prompt."
        )
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": initial_prompt}],
            model="llama-3.1-70b-versatile",
        )
        first_question = response.choices[0].message.content
        st.session_state.questions.append(first_question)
    
    # Display the current question and collect the answer
    st.write(f"Question {st.session_state.current_question + 1}: {st.session_state.questions[st.session_state.current_question]}")
    answer = st.text_input("Your Answer:", key=f"answer_{st.session_state.current_question}")
    
    if st.button("Submit Answer"):
        st.session_state.answers.append(answer)
        
        # Generate feedback for the answer
        feedback_prompt = (
            f"Provide feedback on this answer for a {field} interview: '{answer}'. "
            "If answer field is empty, print: Feedback not generated."
        )
        feedback_response = client.chat.completions.create(
            messages=[{"role": "user", "content": feedback_prompt}],
            model="llama-3.1-70b-versatile",
        )
        feedback = feedback_response.choices[0].message.content

        st.session_state.feedbacks.append(feedback)
        
        # Display feedback
        st.write("Feedback:", feedback)
        st.session_state.show_next_question = True  # Enable "Next Question" button after feedback

    # Separate "Next Question" button
    if st.session_state.show_next_question and st.button("Next Question"):
        # Generate the next question if not the last
        if st.session_state.current_question < question_count - 1:
            follow_up_prompt = (
                f"Generate a follow-up or new question related to {field} for an interview. "
                "Take into account previous questions and answers if necessary. "
                "Directly provide the question without extra context or prompt explanation."
            )
            next_question_response = client.chat.completions.create(
                messages=[{"role": "user", "content": follow_up_prompt}],
                model="llama-3.1-70b-versatile",
            )
            next_question = next_question_response.choices[0].message.content
            st.session_state.questions.append(next_question)
            st.session_state.current_question += 1
            st.session_state.show_next_question = False  # Hide the "Next Question" button
        else:
            st.write("Interview complete! Thank you for participating.")
