import streamlit as st
from pathlib import Path
import uuid

from app.pipeline import ask
from app.indexer import update_index
from app.config import DOCUMENTS_DIR
from app.vector_store import get_indexed_filenames, get_document_chunks
from app.quiz_generator import generate_quiz
from app.flashcard_generator import generate_flashcards
from app.bullet_points_generator import generate_bullet_points

st.title("DocuRAG")
st.write("Ask questions based on your documents")

mode=st.radio(
    "Choose Mode:",
    ["Document Q&A","Study Mode"],
    captions=[
        "Answer your Questions from the documents",
        "Study your documents with quizzes and flashcards",
    ])
    

uploaded_files= st.file_uploader(
    "Upload Documents",
    type=["pdf",'txt','docx'],
    accept_multiple_files=True
)

documents_dir=Path(DOCUMENTS_DIR)
documents_dir.mkdir(parents=True, exist_ok=True)

if st.button("Upload Documents"):
    if not uploaded_files:
        st.warning("Upload atleast one file")
    else:
        for uploaded_file in uploaded_files:
            filename=Path(
                uploaded_file.name.replace("\\","/")
            ).name
            
            destination= documents_dir/filename
            
            if destination.exists():
                st.warning(f"{filename} already exists. Skipping it.")
                continue
            
            destination.write_bytes(uploaded_file.getvalue())
            st.success(f"Saved: {filename}")
            
        try:
            with st.spinner("Indexing Documents..."):
                update_index()
                
            st.success("Indexing Complete.")
            
        except Exception as error:
            st.error(f"Indexing Failed. Your documents are saved in documents folder. Details : {error}")
            

if mode== "Document Q&A":
    
    if "messages" not in st.session_state:
        st.session_state.messages=[]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            sources= message.get("sources",[])
            
            if sources:
                with st.expander("Sources"):
                    for source in sources:
                        st.write(f"Filename : {source['filename']}")
                        
                        if source['page_number'] is not None:
                            st.caption(f"Page Number : {source['page_number']}")
                        
                        st.caption(f"Chunk : {source['chunk_id']}")
                        

    prompt=st.chat_input("Ask DocuRAG a Question...")

    if prompt:
        
        history= st.session_state.messages.copy()
        
        st.session_state.messages.append({
            "role":"user",
            "content":prompt
        })
        
        with st.chat_message("user"):
            st.write(prompt)
            
        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    response= ask(prompt,history)
                    
                st.write(response["answer"])
                
                if response['sources']:
                    with st.expander("Sources"):
                        for source in response['sources']:
                            st.write(f"Filename : {source['filename']}")
                            
                            if source['page_number'] is not None:
                                st.caption(f"Page Number: {source['page_number']}")
                            
                            st.caption(f"Chunk : {source['chunk_id']}")


                st.session_state.messages.append({
                    "role":"assistant",
                    "content":response['answer'],
                    "sources":response['sources']
                })      
                
            except Exception as error:
                st.error(f"Unable to generate an Answer : {error}")
                
else:
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Document Q&A",
        "Quiz", 
        "Flash Cards", 
        "Bullet points"
        ])
    
    with tab1:
        st.subheader("Document Q&A")
        
        if "study_messages" not in st.session_state:
            st.session_state.study_messages=[]
            
        for message in st.session_state.study_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
        prompt=st.chat_input("Ask your doubts from the doocuments...")
        
        if prompt:
            history = st.session_state.study_messages.copy()
            
            st.session_state.study_messages.append({
                "role":"user",
                "content":prompt
            })
            
            with st.chat_message("user"):
                st.write(prompt)
                
            with st.chat_message("assistant"):
                try:
                    with st.spinner("Thinking..."):
                        response=ask(prompt,history)
                        
                    st.write(response["answer"])
                    
                    st.session_state.study_messages.append({
                        "role":"assistant",
                        "content":response["answer"],
                        "sources":response["sources"]
                    })
                    
                except Exception as error:
                    st.error(f"Unable to generate an answer: {error}")
            
        
    
    with tab2:
        st.subheader("Quiz")

        filenames = sorted(get_indexed_filenames())

        if not filenames:
            st.warning("No indexed documents found.")

        else:
            selected_file = st.selectbox(
                "Choose a document",
                filenames,
                key="quiz_document"
            )

            num_questions = st.slider(
                "Number of questions",
                min_value=1,
                max_value=10,
                value=5,
                key="quiz_num_questions"
            )

            if st.button("Generate Quiz"):
                try:
                    with st.spinner("Generating your quiz..."):
                        chunks = get_document_chunks(selected_file)

                        if not chunks:
                            raise ValueError(
                                "No chunks found for this document."
                            )

                        context = "\n\n".join(
                            chunk["content"] for chunk in chunks
                        )

                        quiz = generate_quiz(
                            context,
                            num_questions=num_questions
                        )

                        st.session_state.quiz = quiz
                        st.session_state.quiz_id = str(uuid.uuid4())
                        st.session_state.quiz_submitted = False
                        st.session_state.pop("quiz_score", None)
                        
                        
                except Exception as error:
                    st.error(f"Quiz generation failed: {error}")
            
        if "quiz" in st.session_state:
            quiz = st.session_state.quiz

            with st.form("quiz_form"):
                user_answers = {}

                for index, question in enumerate(
                    quiz["questions"], start=1
                ):
                    st.markdown(f"### Question {index}")
                    st.write(question["question"])

                    user_answers[index] = st.radio(
                        "Choose your answer:",
                        question["options"],
                        key=f"quiz_answer_{st.session_state.quiz_id}_{index}"
                    )

                submitted = st.form_submit_button("Submit Answers")

            
            if submitted:
                score = 0
                saved_answers = {}

                for index, question in enumerate(
                    quiz["questions"], start=1
                ):
                    selected_answer = user_answers[index]
                    saved_answers[index] = selected_answer

                    if selected_answer == question["correct_answer"]:
                        score += 1

                st.session_state.quiz_answers = saved_answers
                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True



            if st.session_state.get("quiz_submitted", False):
                total = len(quiz["questions"])
                score = st.session_state.quiz_score

                st.subheader("Your Results")
                st.write(f"Score: {score}/{total}")
                st.progress(score / total)

                for index, question in enumerate(
                    quiz["questions"], start=1
                ):
                    st.markdown(f"### Question {index}")
                    st.write(question["question"])

                    selected_answer = st.session_state.quiz_answers.get(index)

                    correct_answer = question["correct_answer"]

                    if selected_answer == correct_answer:
                        st.success(f"Your answer: {selected_answer} — Correct!")
                    else:
                        st.error(f"Your answer: {selected_answer} — Incorrect")
                        st.info(f"Correct answer: {correct_answer}")

                    st.write(f"**Explanation:** {question['explanation']}")
                    st.divider()



        
    
    with tab3:
        st.subheader("Flash Cards")

        filenames = sorted(get_indexed_filenames())

        if not filenames:
            st.warning("No indexed documents found.")

        else:
            selected_file = st.selectbox(
                "Choose a document",
                filenames,
                key="flashcard_document"
            )

            num_cards = st.slider(
                "Number of flashcards",
                min_value=3,
                max_value=20,
                value=10,
                key="flashcard_count"
            )

            if st.button("Generate Flashcards"):
                try:
                    with st.spinner("Creating your flashcards..."):
                        chunks = get_document_chunks(selected_file)

                        if not chunks:
                            raise ValueError(
                                "No chunks found for this document."
                            )

                        context = "\n\n".join(
                            chunk["content"] for chunk in chunks
                        )

                        flashcards = generate_flashcards(
                            context,
                            num_cards=num_cards
                        )

                        st.session_state.flashcards = flashcards
                        st.session_state.flashcard_deck_id = str(uuid.uuid4())

                except Exception as error:
                    st.error(f"Flashcard generation failed: {error}")

            if "flashcards" in st.session_state:
                cards = st.session_state.flashcards["flashcards"]

                for index, card in enumerate(cards, start=1):
                    with st.container(border=True):
                        st.markdown(f"### Card {index}")
                        st.write(card["question"])

                        deck_id = st.session_state.flashcard_deck_id
                        reveal_key = f"flashcard_revealed_{deck_id}_{index}"

                        if st.button(
                            "Reveal Answer",
                            key=f"reveal_flashcard_{deck_id}_{index}"
                        ):
                            st.session_state[reveal_key] = True

                        if st.session_state.get(reveal_key, False):
                            st.info(card["answer"])

        
    with tab4:
        st.subheader("Bullet Points")

        filenames = sorted(get_indexed_filenames())

        if not filenames:
            st.warning("No indexed documents found.")

        else:
            selected_file = st.selectbox(
                "Choose a document",
                filenames,
                key="bullet_points_document"
            )

            num_points = st.slider(
                "Number of bullet points",
                min_value=3,
                max_value=20,
                value=10,
                key="bullet_points_count"
            )

            if st.button("Generate Bullet Points"):
                try:
                    with st.spinner("Summarizing your document..."):
                        chunks = get_document_chunks(selected_file)

                        if not chunks:
                            raise ValueError(
                                "No chunks found for this document."
                            )

                        context = "\n\n".join(
                            chunk["content"] for chunk in chunks
                        )

                        result = generate_bullet_points(
                            context,
                            num_points=num_points
                        )

                        st.session_state.bullet_points = result
                        st.session_state.bullet_points_source = selected_file

                except Exception as error:
                    st.error(f"Bullet point generation failed: {error}")

        if "bullet_points" in st.session_state:
            st.markdown(
                f"**Source document:** "
                f"{st.session_state.bullet_points_source}"
            )

            for point in st.session_state.bullet_points["bullet_points"]:
                st.markdown(f"- {point}")