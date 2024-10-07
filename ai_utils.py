# ai_utils.py

from openai import OpenAI
import re
import logging
import streamlit as st

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
        client = OpenAI()
        # Ensure OpenAI API key is set from Streamlit secrets
        client.api_key = st.secrets["OPENAI_API_KEY"]  # Securely fetch the API key
        
        # Construct the AI prompt
        prompt = (
            f"Develop relevant PICO elements (Population, Intervention, Comparison, Outcome) "
            f"from the following research title:\n\n\"{title}\"\n\n"
            f"Provide each element labeled accordingly, and only provide the PICO elements "
            f"in the following format:\n\n"
            f"Population: Population\n"
            f"Intervention: Intervention\n"
            f"Comparison: Comparison\n"
            f"Outcome: Outcome"
        )
        
        # Call the OpenAI API to generate PICO elements
        response = client.chat.completions.create(
            model='gpt-4o',  # Use the desired model
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that extracts PICO elements from research titles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.5,
            n=1,
            stop=None,
        )

        # Extract the AI's reply from the response
        pico_output = response.choices[0].message.content.strip()
        pico_elements = parse_pico(pico_output)
        return pico_elements

    except Exception as e:
        logging.error(f"Error in generate_pico_from_title: {e}")
        raise Exception("An error occurred while generating PICO elements from the title.")

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
        client = OpenAI()
        # Ensure OpenAI API key is set from Streamlit secrets
        client.api_key = st.secrets["OPENAI_API_KEY"]  # Securely fetch the API key

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

        # Call the OpenAI API to refine PICO elements
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that refines PICO elements for clarity and specificity."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.5,
            n=1,
            stop=None,
        )

        # Extract the AI's reply from the response
        refined_pico_output = response.choices[0].message.content.strip()
        refined_pico_elements = parse_pico(refined_pico_output)
        return refined_pico_elements

    except Exception as e:
        logging.error(f"Error in refine_pico_elements: {e}")
        raise Exception("An error occurred while refining the PICO elements.")

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
        client = OpenAI()
        # Ensure OpenAI API key is set from Streamlit secrets
        client.api_key = st.secrets["OPENAI_API_KEY"]  # Securely fetch the API key

        # Construct the AI prompt
        prompt = (
            f"From the following PICO elements, extract between 3 to 6 key concepts that are highly relevant for developing an accurate and effective search strategy. Ensure that the concepts are distinct and do not overlap unnecessarily. If the 'Comparison' is simply 'placebo' or 'no intervention,' omit it as a key concept.\n\n"
            f"Consider the use of Medical Subject Headings (MeSH) terms and text words for developing search terms in databases like PubMed, MEDLINE, Cochrane, CINAHL, and Embase.\n\n"
            f"Population: {pico_elements['Population']}\n"
            f"Intervention: {pico_elements['Intervention']}\n"
            f"Comparison: {pico_elements['Comparison']}\n"
            f"Outcome: {pico_elements['Outcome']}\n\n"
            f"Provide the concepts as a numbered list, and rank them in terms of their relevance to defining an accurate search strategy."
        )

        response = client.chat.completions.create(
            model='gpt-4o',  # Use the desired model
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that extracts key concepts from PICO elements."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=500,
            temperature=0.5,
            n=1,
            stop=None,
        )

        # Extract the AI's reply from the response
        concepts_output = response.choices[0].message.content.strip()
        concepts = parse_concepts(concepts_output)
        return concepts

    except Exception as e:
        logging.error(f"Error in generate_concepts_from_pico: {e}")
        raise Exception("An error occurred while generating concepts from the PICO elements.")



##########################PARSE######FUNCTIONS###########################################
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


def parse_concepts(concepts_text):
    """
    Parses the list of concepts from the AI's response.

    Args:
        concepts_text (str): Text containing the list of concepts.

    Returns:
        list: List of concepts.
    """
    lines = concepts_text.strip().split('\n')
    concepts = []
    for line in lines:
        # Remove numbering and extra spaces
        concept = re.sub(r'^\d+\.\s*', '', line).strip()
        if concept:
            concepts.append(concept)
    return concepts
