# main.py

import streamlit as st
import openai
import ai_utils  # Importing the AI utilities module
import logging

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
        'pico_generated': False
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
    steps = ["Title", "PICO", "Concept Extraction"]

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
    else:
        st.success("All steps completed!")

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
                st.rerun()
                
            except Exception as e:
                st.error(str(e))

    elif generate_pico and not title_input:
        st.warning("Please enter a title to generate PICO elements.")

    elif proceed_to_pico:
        # Mark Title step as completed even if skipped
        if "Title" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Title")
        st.session_state.pico_generated = False
        st.rerun()

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
        refine_pico = st.button("Refine using AI", key="refine_pico")
    with col2:
        next_step = st.button("Next", key="next_step")

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

                st.success("PICO elements have been refined.")
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
            st.success("PICO input completed. Proceeding to the next step.")
            st.rerun()
        else:
            st.warning("Please fill in all PICO elements before proceeding.")

def step_concept_extraction():
    """
    Placeholder for the Concept Extraction step.
    """
    st.header("Step 3: Concept Extraction")

    st.info("Concept Extraction functionality will be implemented here.")

    # Button to simulate completing this step
    if st.button("Mark Step as Completed", key="concept_extraction_complete"):
        if "Concept Extraction" not in st.session_state.completed_steps:
            st.session_state.completed_steps.append("Concept Extraction")
        st.success("Concept Extraction step marked as completed.")
        st.rerun()

if __name__ == "__main__":
    main()
