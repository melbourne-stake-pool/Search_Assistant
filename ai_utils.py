# ai_utils.py

import re
import logging
import streamlit as st
from gpt_helper import gpt_api_call


###################################################################################
def generate_pico_from_title(title):
    """
    Generates PICO elements from a given research title using OpenAI's API.

    Args:
        title (str): The research question title.

    Returns:
        dict: A dictionary containing the PICO elements.

    Raises:
        Exception: If an error occurs during the API call.
    """
    try:
        # Construct the AI prompt
        prompt = (
            f"Develop and create relevant PICO elements (Population, Intervention, Comparison, Outcome) "
            f"from the following research title:\n\n\"{title}\"\n\n"
            f"If the title does not provide enough to complete a PICO; please be create and relevant."
            f"Provide each element labeled accordingly, and only provide the PICO elements "
            f"in the following format:\n\n"
            f"Population: Population\n"
            f"Intervention: Intervention\n"
            f"Comparison: Comparison\n"
            f"Outcome: Outcome"
        )
        response = gpt_api_call(prompt) #call the gpt_api_call function from gpt_helper.py
        text = (response.get("content") or "").strip()
        pico_elements = parse_pico(text)
        return pico_elements

    except Exception as e:
        logging.error(f"Error in generate_pico_from_title: {e}")
        raise Exception("An error occurred while generating PICO elements from the title.")

###################################################################################
def refine_pico_elements(pico_elements):
    """
    Refines the provided PICO elements for clarity and specificity using OpenAI's API.

    Args:
        pico_elements (dict): A dictionary containing the PICO elements.

    Returns:
        dict: A dictionary containing the refined PICO elements.

    Raises:
        Exception: If an error occurs during the API call.
    """
    try:       
        # Prepare the PICO statement
        pico_statement = (
            f"Population: {pico_elements['Population']}\n"
            f"Intervention: {pico_elements['Intervention']}\n"
            f"Comparison: {pico_elements['Comparison']}\n"
            f"Outcome: {pico_elements['Outcome']}"
        )

        # Construct the AI prompt
        prompt = (
            f"Refine the following PICO elements for clarity and specificity. "
            f"Provide each element labeled accordingly, and only provide the PICO elements "
            f"in the following format:\n\n"
            f"Population: Refined Population\n"
            f"Intervention: Refined Intervention\n"
            f"Comparison: Refined Comparison\n"
            f"Outcome: Refined Outcome\n\n"
            f"PICO Elements:\n"
            f"Population: {pico_elements['Population']}\n"
            f"Intervention: {pico_elements['Intervention']}\n"
            f"Comparison: {pico_elements['Comparison']}\n"
            f"Outcome: {pico_elements['Outcome']}"
        )

        response = gpt_api_call(prompt) #call the gpt_api_call function from gpt_helper.py
        text = (response.get("content") or "").strip()
        refined_pico_elements = parse_pico(text)
        return refined_pico_elements

    except Exception as e:
        logging.error(f"Error in refine_pico_elements: {e}")
        raise Exception("An error occurred while refining the PICO elements.")

###################################################################################
def generate_concepts_from_pico(pico_elements):
    """
    Generates key concepts from the given PICO elements using OpenAI's API.

    Args:
        pico_elements (dict): A dictionary containing the PICO elements.

    Returns:
        list: A list of extracted concepts.

    Raises:
        Exception: If an error occurs during the API call.
    """
    try:
        # Construct the AI prompt
        prompt = (
            f"From the following PICO elements, extract between 3 to 6 key concepts that are highly relevant for developing an accurate and effective search strategy.\n\n"
            f"Ensure that the concepts are distinct and do not overlap unnecessarily. If the 'Comparison' is simply 'placebo' or 'no intervention,' omit it as a key concept.\n\n"
            f"Consider relevant search concepts and text words for developing search terms in databases like PubMed, MEDLINE, Cochrane, CINAHL, and Embase.\n\n"
            f"Population: {pico_elements['Population']}\n"
            f"Intervention: {pico_elements['Intervention']}\n"
            f"Comparison: {pico_elements['Comparison']}\n"
            f"Outcome: {pico_elements['Outcome']}\n\n"
            f"Provide the concepts as a numbered list, and rank them in terms of their relevance to defining an accurate search strategy."
            f"Please do not add any e.g. or i.e. in the concepts."
        )

        response = gpt_api_call(prompt) #call the gpt_api_call function from gpt_helper.py
        text = (response.get("content") or "").strip()
        concepts = parse_concepts(text)
        return concepts

    except Exception as e:
        logging.error(f"Error in generate_concepts_from_pico: {e}")
        raise Exception("An error occurred while generating concepts from the PICO elements.")

###################################################################################
def generate_search_terms_all(concepts_list):
    """
    Generates MeSH terms and Text terms for all concepts using OpenAI's API.

    Args:
        concepts_list (list): A list of concept strings.

    Returns:
        dict: A dictionary with concept texts as keys, and each value is a dict with 'MeSH Terms' and 'Text Terms' lists.

    Raises:
        Exception: If an error occurs during the API call.
    """
    try:
        # Construct the AI prompt
        concepts_text = "\n".join([f"{idx+1}. {concept}" for idx, concept in enumerate(concepts_list)])
        prompt = (
            f"For each of the following concepts, generate a list of relevant MeSH terms and Text terms to develop a high quality search strategy.\n"
            f"Provide the terms for each concept in the following format:\n\n"
            f"Concept: Concept Name\n"
            f"MeSH Terms:\n- MeSH term 1\n- MeSH term 2\n...\n"
            f"Text Terms:\n- Text term 1\n- Text term 2\n...\n\n"
            f"Here are the concepts:\n{concepts_text}\n\n"
            f"Please ensure that the output is properly formatted as specified."
        )

        response = gpt_api_call(prompt) #call the gpt_api_call function from gpt_helper.py
        text = (response.get("content") or "").strip()
        # Parse the output, passing the original concepts list
        search_terms_dict = parse_search_terms_all(text, concepts_list)
        return search_terms_dict

    except Exception as e:
        logging.error(f"Error in generate_search_terms_all: {e}")
        raise Exception("An error occurred while generating search terms.")

#########################################################################################
##########################PARSE######FUNCTIONS###########################################
def _strip_leading_markers(s: str) -> str:
    """
    Remove bullets and numbering like '-', '*', '•', '1.', '1)', '  2)  ' etc.
    """
    return re.sub(r'^\s*(?:[-*•]\s*)?(?:\d+\s*[\.\)]\s*)?', '', str(s)).strip()

##########################################################################################

def parse_pico(pico_text):
    """
    Parses PICO elements from a given text.

    Args:
        pico_text (str): Text containing PICO elements.

    Returns:
        dict: A dictionary with PICO elements extracted.
    """
    import re

    pico_elements = {'Population': '', 'Intervention': '', 'Comparison': '', 'Outcome': ''}

    # Remove any markdown formatting like ** or __
    pico_text = re.sub(r'\*\*|__', '', pico_text)

    # Split the text into lines
    lines = pico_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Remove bullet points and leading dashes or asterisks
        line = re.sub(r'^[-*\s]*', '', line)
        # Match 'Population: ...' (case-insensitive)
        match = re.match(r'^(Population|Intervention|Comparison|Outcome)\s*:\s*(.*)', line, re.IGNORECASE)
        if match:
            key = match.group(1).capitalize()
            value = match.group(2).strip()
            pico_elements[key] = value

    return pico_elements

###### parse_concepts (replace your current one) ###############################
def parse_concepts(concepts_text: str) -> list[str]:
    lines = (concepts_text or "").splitlines()
    concepts = []
    for line in lines:
        concept = _strip_leading_markers(line)
        if concept:
            concepts.append(concept)
    return concepts

###### parse_search_terms_all (drop-in replacement) ###########################
def parse_search_terms_all(terms_output: str, original_concepts: list[str]) -> dict:
    """
    Parse the LLM output into:
      { Concept: { 'MeSH Terms': [...], 'Text Terms': [...] } }
    Robust to numbered/bulleted variants from both the prompt and the model.
    """
    terms_output = (terms_output or "").replace('\r\n', '\n').replace('\r', '\n')

    # Map normalised original concepts -> original text
    def norm(s: str) -> str: return _strip_leading_markers(s).lower()
    concept_mapping = {norm(c): c for c in original_concepts}

    # Split by 'Concept:' headers (case-insensitive)
    concept_blocks = re.split(r'\n(?=Concept\s*:)', terms_output, flags=re.IGNORECASE)
    search_terms_dict = {}

    for block in concept_blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        concept_name = ''
        mesh_terms, text_terms = [], []
        current_section = None

        for line in lines:
            l = line.strip()

            # Concept header
            if re.match(r'^Concept\s*:', l, re.IGNORECASE):
                concept_name_ai = l.split(':', 1)[1].strip()
                # Use normalised name to look up the original concept text
                concept_name = concept_mapping.get(norm(concept_name_ai), _strip_leading_markers(concept_name_ai))

            # Section headers
            elif re.match(r'^MeSH\s*Terms\s*:', l, re.IGNORECASE):
                current_section = 'MeSH Terms'
            elif re.match(r'^Text\s*Terms\s*:', l, re.IGNORECASE):
                current_section = 'Text Terms'

            # Bullet terms
            elif l.startswith('-'):
                term = l[1:].strip()
                if current_section == 'MeSH Terms':
                    mesh_terms.append(term)
                elif current_section == 'Text Terms':
                    text_terms.append(term)

        if concept_name:
            search_terms_dict[concept_name] = {'MeSH Terms': mesh_terms, 'Text Terms': text_terms}

    return search_terms_dict