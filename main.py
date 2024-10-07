# main.py

import streamlit as st
import openai
import ai_utils  # Importing the AI utilities module
import logging
import pandas as pd  # Import pandas for data manipulation
import base64  # For copy to clipboard functionality

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set up OpenAI API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

def initialize_session_state():
    """
    Initializes the session state variables.
    """
    default_keys = {
        'completed_steps': [],
        'population': '',
        'intervention': '',
        'comparison': '',
        'outcome': '',
        'pico_generated': False,
        'concepts': [],          # Added for Step 3
        'search_terms': {},      # Added for Step 4
        'search_strategy': '',   # Added for Step 5
    }
    for key, value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value

def update_sidebar(steps, placeholder):
    """
    Updates the sidebar with the navigation steps and their completion status.

    Args:
        steps (list): List of step names.
        placeholder: Streamlit container or placeholder for the sidebar.
    """
    with placeholder:
        st.title("Navigation")
        for step in steps:
            if step in st.session_state.completed_steps:
                st.write(f"✅ {step}")
            else:
                st.write(f"⬜ {step}")

def main():
    """
    Main function to run the Streamlit app.
    """
    # Initialize session state
    initialize_session_state()

    # Define the steps
    steps = ["Title", "PICO", "Concept Extraction", "Generate Search Terms", "Construct Search Strategy", "Complete"]

    # Create a placeholder for the sidebar
    sidebar_placeholder = st.sidebar.container()

    # Update the sidebar
    update_sidebar(steps, sidebar_placeholder)

    # Main content
    st.title("Systematic Review Search Assistant")

    # Workflow Control
    if "Title" not in st.session_state.completed_steps:
        step_title_input()
    elif "PICO" not in st.session_state.completed_steps:
        step_pico_input()
    elif "Concept Extraction" not in st.session_state.completed_steps:
        step_concept_extraction()
    elif "Generate Search Terms" not in st.session_state.completed_steps:
        step_generate_search_terms()
    elif "Construct Search Strategy" not in st.session_state.completed_steps:
        step_construct_search_strategy()
    elif "Complete" not in st.session_state.completed_steps:
        step_complete()
    else:
        st.success("All steps completed! 🎉")
        # Optionally provide a 'Start Again' button
        if st.button("Start Again 🔄"):
            # Clear session state and restart
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

#STEP 1
def step_title_input():
    """
    Handles the Title Input step.
    """
    st.header("Step 1: Input Title or Proceed to PICO")

    title_input = st.text_input("Enter the Title of your research question (optional):")

    col1, col2 = st.columns(2)
    with col1:
        proceed_to_pico = st.button("Skip to PICO", key="skip_to_pico")
    with col2:
        generate_pico = st.button("Generate PICO from Title", key="generate_pico")

    if generate_pico and title_input:
        with st.spinner("Generating PICO elements from Title..."):
            try:
                # Generate PICO elements from the title using OpenAI API
                pico_elements = ai_utils.generate_pico_from_title(title_input)
                
                # Update session state with generated PICO elements
                st.session_state.population = pico_elements['Population']
                st.session_state.intervention = pico_elements['Intervention']
                st.session_state.comparison = pico_elements['Comparison']
                st.session_state.outcome = pico_elements['Outcome']
                st.session_state.pico_generated = True

                # Mark step as completed
                if "Title" not in st.session_state.completed_steps:
                    st.session_state.completed_steps.append("Title")

                st.success("PICO elements generated from Title. Proceeding to PICO step.")
                st.rerun()  # Rerun the app
                
            except Exception as e:
                st.error(str(e))

    elif generate_pico and not title_input:
        st.warning("Please enter a title to generate PICO elements. ⚠️")

    elif proceed_to_pico:
        # Mark Title step as completed even if skipped
        if "Title" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Title")
        st.session_state.pico_generated = False
        st.rerun()

#STEP 2
def step_pico_input():
    """
    Handles the PICO Input step.
    """
    st.header("Step 2: Input PICO Elements")

    # PICO input fields with pre-filled values if available
    population_input = st.text_area(
        "Population:", value=st.session_state.population, key="population_input"
    )
    intervention_input = st.text_area(
        "Intervention:", value=st.session_state.intervention, key="intervention_input"
    )
    comparison_input = st.text_area(
        "Comparison:", value=st.session_state.comparison, key="comparison_input"
    )
    outcome_input = st.text_area(
        "Outcome:", value=st.session_state.outcome, key="outcome_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        refine_pico = st.button("Refine using AI 🤖", key="refine_pico")
    with col2:
        next_step = st.button("Next ➡️", key="next_step")

    if refine_pico:
        with st.spinner("Refining PICO elements..."):
            try:
                # Prepare PICO elements for refinement
                pico_elements = {
                    'Population': population_input,
                    'Intervention': intervention_input,
                    'Comparison': comparison_input,
                    'Outcome': outcome_input
                }

                # Refine PICO elements using OpenAI API
                refined_pico_elements = ai_utils.refine_pico_elements(pico_elements)

                # Update session state with refined PICO elements
                st.session_state.population = refined_pico_elements['Population']
                st.session_state.intervention = refined_pico_elements['Intervention']
                st.session_state.comparison = refined_pico_elements['Comparison']
                st.session_state.outcome = refined_pico_elements['Outcome']

                st.success("PICO elements have been refined. ✅")
                st.rerun()

            except Exception as e:
                st.error(str(e))

    elif next_step:
        # Update session state with the inputs
        st.session_state.population = population_input
        st.session_state.intervention = intervention_input
        st.session_state.comparison = comparison_input
        st.session_state.outcome = outcome_input

        # Ensure all PICO fields are filled
        if all([
            st.session_state.population.strip(),
            st.session_state.intervention.strip(),
            st.session_state.comparison.strip(),
            st.session_state.outcome.strip()
        ]):
            # Mark PICO step as completed
            if "PICO" not in st.session_state.completed_steps:
                st.session_state.completed_steps.append("PICO")
            st.success("PICO input completed. Proceeding to the next step. ✅")
            st.rerun()
        else:
            st.warning("Please fill in all PICO elements before proceeding. ⚠️")

#STEP 3
def step_concept_extraction():
    """
    Handles the Concept Extraction step with AI integration.
    """
    st.header("Step 3: Concept Extraction")

    st.write("Based on your PICO elements, here are some extracted concepts. You can edit or delete them as needed.")

    if 'concepts' not in st.session_state or not st.session_state.concepts:
        # Prepare PICO elements
        pico_elements = {
            'Population': st.session_state.population,
            'Intervention': st.session_state.intervention,
            'Comparison': st.session_state.comparison,
            'Outcome': st.session_state.outcome
        }

        # Run the concept AI function
        try:
            with st.spinner("Generating concepts from PICO elements..."):
                concepts_list = ai_utils.generate_concepts_from_pico(pico_elements)
                if not concepts_list:
                    st.error("No concepts were generated. Please check your PICO elements.")
                    return
                # Assign IDs and format as list of dicts
                st.session_state.concepts = [{'id': idx+1, 'text': concept} for idx, concept in enumerate(concepts_list)]
        except Exception as e:
            st.error(f"An error occurred while generating concepts: {str(e)}")
            return  # Exit the function if there's an error

    concepts = st.session_state.concepts

    for concept in concepts:
        with st.container():
            cols = st.columns([20, 1])  # Adjusted column widths for better alignment
            with cols[0]:
                new_text = st.text_input(
                    f"Concept {concept['id']}:", value=concept['text'], key=f"concept_{concept['id']}"
                )
                concept['text'] = new_text
            with cols[1]:
                # Adjust the button style for better alignment
                st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
                delete = st.button(
                    "❌",
                    key=f"delete_concept_{concept['id']}",
                    help="Delete concept",
                )
                if delete:
                    st.session_state.concepts = [c for c in concepts if c['id'] != concept['id']]
                    st.rerun()

    # Button to add a new concept
    if st.button("Add Concept ➕"):
        new_id = max([c['id'] for c in st.session_state.concepts] or [0]) + 1
        st.session_state.concepts.append({'id': new_id, 'text': ''})
        st.rerun()

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        back = st.button("⬅️ Back", key="concepts_back")
    with col2:
        next_step = st.button("Next ➡️", key="concepts_next")

    if next_step:
        # Mark Concept Extraction step as completed
        if "Concept Extraction" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Concept Extraction")
        st.rerun()
    elif back:
        # Go back to PICO step
        if "PICO" in st.session_state.completed_steps:
            st.session_state.completed_steps.remove("PICO")
        st.rerun()

#STEP 4
def step_generate_search_terms():
    """
    Handles the Generate Search Terms step with UI/UX enhancements and dummy data.
    """
    st.header("Step 4: Generate Search Terms")

    st.write("For each concept, here are the MeSH and Text terms. You can edit, add, or delete terms as needed.")

    if 'search_terms' not in st.session_state or not st.session_state.search_terms:
        # Initialize search terms with dummy data
        st.session_state.search_terms = {}
        for concept in st.session_state.concepts:
            concept_text = concept['text']
            st.session_state.search_terms[concept_text] = {
                'MeSH Terms': [f"MeSH Term 1 for {concept_text} (Dummy Data)", f"MeSH Term 2 for {concept_text} (Dummy Data)"],  # Dummy Data
                'Text Terms': [f"Text Term 1 for {concept_text} (Dummy Data)", f"Text Term 2 for {concept_text} (Dummy Data)"],  # Dummy Data
            }

    search_terms = st.session_state.search_terms

    # Create tabs for each concept
    concept_tabs = st.tabs([concept['text'] for concept in st.session_state.concepts])

    for idx, concept in enumerate(st.session_state.concepts):
        concept_text = concept['text']
        with concept_tabs[idx]:
            st.subheader(f"Concept: {concept_text}")

            # Split into two columns
            col1, col2 = st.columns(2)

            with col1:
                # MeSH Terms
                st.write("**MeSH Terms**")
                mesh_terms = search_terms[concept_text]['MeSH Terms']
                mesh_terms_df = pd.DataFrame(mesh_terms, columns=['MeSH Terms'])
                edited_mesh_terms = st.data_editor(
                    mesh_terms_df,
                    num_rows="dynamic",
                    key=f"mesh_terms_{concept['id']}"
                )
                # Update MeSH terms in session state
                search_terms[concept_text]['MeSH Terms'] = edited_mesh_terms['MeSH Terms'].tolist()

            with col2:
                # Text Terms
                st.write("**Text Terms**")
                text_terms = search_terms[concept_text]['Text Terms']
                text_terms_df = pd.DataFrame(text_terms, columns=['Text Terms'])
                edited_text_terms = st.data_editor(
                    text_terms_df,
                    num_rows="dynamic",
                    key=f"text_terms_{concept['id']}"
                )
                # Update Text terms in session state
                search_terms[concept_text]['Text Terms'] = edited_text_terms['Text Terms'].tolist()

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        back = st.button("⬅️ Back", key="search_terms_back")
    with col2:
        next_step = st.button("Next ➡️", key="search_terms_next")

    if next_step:
        # Mark Generate Search Terms step as completed
        if "Generate Search Terms" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Generate Search Terms")
        st.rerun()
    elif back:
        # Go back to Concept Extraction step
        if "Concept Extraction" in st.session_state.completed_steps:
            st.session_state.completed_steps.remove("Concept Extraction")
        st.rerun()

#STEP 5
def step_construct_search_strategy():
    """
    Handles the Construct Search Strategy step with UI/UX enhancements and dummy data.
    """
    st.header("Step 5: Construct Search Strategy")

    st.write("Below is your constructed search strategy. You can make final edits if needed.")

    if 'search_strategy' not in st.session_state or not st.session_state.search_strategy:
        # Generate a dummy search strategy (Dummy Data)
        strategy_components = []
        for concept in st.session_state.concepts:
            concept_text = concept['text']
            terms = st.session_state.search_terms[concept_text]
            # Combine MeSH terms
            mesh_terms = ' OR '.join([f'"{term}"[MeSH]' for term in terms['MeSH Terms']])
            # Combine Text terms
            text_terms = ' OR '.join([f'"{term}"[TIAB]' for term in terms['Text Terms']])
            # Combine MeSH and Text terms
            concept_terms = f"({mesh_terms}) OR ({text_terms})"
            strategy_components.append(f"({concept_terms})")
        # Combine all concepts using 'AND'
        search_strategy = ' AND '.join(strategy_components)
        # Removed filters as per request
        st.session_state.search_strategy = search_strategy

    # Display the search strategy in a large text area
    search_strategy_input = st.text_area(
        "Search Strategy:",
        value=st.session_state.search_strategy,
        height=300,
        key="search_strategy_input"
    )

    # Update the session state with any edits made by the user
    st.session_state.search_strategy = search_strategy_input

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        back = st.button("⬅️ Back", key="search_strategy_back")
    with col2:
        next_step = st.button("Complete ✅", key="search_strategy_next")

    if next_step:
        # Mark Construct Search Strategy step as completed
        if "Construct Search Strategy" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Construct Search Strategy")
        # Mark 'Complete' step as completed
        if "Complete" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Complete")
        st.rerun()
    elif back:
        # Go back to Generate Search Terms step
        if "Generate Search Terms" in st.session_state.completed_steps:
            st.session_state.completed_steps.remove("Generate Search Terms")
        st.rerun()

    # Note: Removed 'Start Again' button from this step as per request

#STEP 6
def step_complete():
    """
    Handles the Complete step.
    """
    st.header("Complete ✅")

    st.success("Thank you for using the Systematic Review Search Assistant! 🎉")

    # Display the final search strategy
    st.write("Here is your final search strategy:")
    st.text_area(
        "Search Strategy:",
        value=st.session_state.search_strategy,
        height=300,
        key="final_search_strategy",
        disabled=True
    )

    # Copy button to copy the search strategy to clipboard
    if st.button("Copy Search Strategy 📋"):
        # Implement copy to clipboard functionality using JavaScript
        search_strategy = st.session_state.search_strategy.replace('\n', '\\n').replace("'", "\\'")
        js = f"""
        <script>
        navigator.clipboard.writeText('{search_strategy}');
        </script>
        """
        st.components.v1.html(js, height=0)
        st.success("Search strategy copied to clipboard!")

    # 'Start Again' button
    if st.button("Start Again 🔄"):
        # Confirm before starting over
        confirm_reset = st.checkbox("Are you sure you want to start over? All progress will be lost.")
        if confirm_reset:
            # Clear session state and restart
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
