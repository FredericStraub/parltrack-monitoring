import panel as pn
import requests
import logging
from io import BytesIO
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
import random
import os
import json
from datetime import datetime
from panel.template import BootstrapTemplate  # Import the template
from keys import OPENAI_API_KEY
# Initialize Panel extension with Tabulator for advanced tables
pn.extension('tabulator')

# Configure LoggingEU Legislative Acts Analysis 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables


if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Pydantic Models
class RelevanceResult(BaseModel):
    """Result of the relevance analysis."""
    is_relevant: bool = Field(description="Is the law relevant to the company?")
    reason: str = Field(description="Reason for relevance or irrelevance")

class TopicAnalysis(BaseModel):
    """Analysis of a thematic area."""
    topic: str = Field(description="The thematic area")
    relevant: bool = Field(description="Is the law relevant for this thematic area?")
    reason: str = Field(description="Reason for relevance or irrelevance")

class AnalysisResult(BaseModel):
    """Result of the automatic analysis."""
    summary: str = Field(description="Summary of the law")
    analyses: List[TopicAnalysis] = Field(description="List of thematic area analyses")

# Functions to fetch data
def load_json_data():
    json_file_path = '/Volumes/External/Project Simone/ELO/ep_dossiers.json'  # Update with your actual path
    try:
        dossiers = []
        with open(json_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line in ('[', ']'):
                    continue
                if line.startswith(','):
                    line = line[1:]
                try:
                    dossier = json.loads(line)
                    dossiers.append(dossier)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding JSON: {e}")
                    continue
        return dossiers
    except Exception as e:
        logger.error(f"Error loading JSON data: {e}")
        return []

def get_vorgaenge():
    logger.info("Loading list of laws from JSON data.")
    data = load_json_data()
    # Filter for 'COD' type
    documents = [
        item for item in data
        if item.get('procedure', {}).get('type') == 'COD - Ordinary legislative procedure (ex-codecision procedure)'
    ]
    # Randomly select 100 documents if more are available
    if len(documents) > 100:
        documents = random.sample(documents, 100)
    logger.info(f"Retrieved {len(documents)} laws of type COD.")
    return documents

def fetch_document_text(url):
    try:
        logger.info(f"Fetching document from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type:
            # If it's a PDF, extract text using PyPDF2
            with BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
            logger.info("Text extraction from PDF successful.")
            return text
        elif 'text/html' in content_type or 'text/plain' in content_type:
            # If it's HTML or plain text
            text = response.text
            logger.info("Text extraction from HTML/plain text successful.")
            return text
        else:
            logger.warning("Unknown content type, cannot extract text.")
            return None
    except Exception as e:
        logger.error(f"Error fetching document text: {e}")
        return None

# Helper functions to format each section
def format_meta(meta):
    if not meta:
        return "No meta data available.\n"
    source = meta.get('source', 'N/A')
    updated = meta.get('updated', 'N/A')
    try:
        updated = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    return f"**Source**: [{source}]({source})\n**Updated**: {updated}\n"

def format_procedure(procedure):
    if not procedure:
        return "No procedure data available.\n"
    fields = [
        f"**Reference**: {procedure.get('reference', 'N/A')}",
        f"**Title**: {procedure.get('title', 'N/A')}",
        f"**Type**: {procedure.get('type', 'N/A')}",
        f"**Subtype**: {procedure.get('subtype', 'N/A')}",
        f"**Instrument**: {procedure.get('instrument', 'N/A')}",
        f"**Stage Reached**: {procedure.get('stage_reached', 'N/A')}",
    ]
    # Legal basis
    legal_basis = procedure.get('legal_basis', [])
    if legal_basis:
        fields.append(f"**Legal Basis**: {', '.join(legal_basis)}")
    # Subjects
    subjects = procedure.get('subject', {})
    if subjects:
        subject_list = ', '.join(subjects.values())
        fields.append(f"**Subjects**: {subject_list}")
    return '\n'.join(fields) + '\n'

def format_committees(committees):
    if not committees:
        return "No committees data available.\n"
    output = ""
    for committee in committees:
        output += f"- **Type**: {committee.get('type', 'N/A')}\n"
        output += f"  - **Committee**: {committee.get('committee_full', 'N/A')}\n"
        rapporteurs = committee.get('rapporteur', [])
        if rapporteurs:
            r_list = ', '.join([r.get('name', 'N/A') for r in rapporteurs])
            output += f"  - **Rapporteur(s)**: {r_list}\n"
        shadows = committee.get('shadows', [])
        if shadows:
            s_list = ', '.join([s.get('name', 'N/A') for s in shadows])
            output += f"  - **Shadows**: {s_list}\n"
    return output

def format_council(council):
    if not council:
        return "No council data available.\n"
    output = ""
    for item in council:
        date = item.get('date', 'N/A')
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            pass
        output += f"- **Date**: {date}\n"
        output += f"  - **Council**: {item.get('council', 'N/A')}\n"
        output += f"  - **Type**: {item.get('type', 'N/A')}\n"
    return output

def format_commission(commission):
    if not commission:
        return "No commission data available.\n"
    output = ""
    for item in commission:
        output += f"- **DG**: {item.get('dg', 'N/A')}\n"
        output += f"  - **Commissioner**: {item.get('commissioner', 'N/A')}\n"
    return output

def format_events(events):
    if not events:
        return "No events data available.\n"
    output = ""
    for event in events:
        date = event.get('date', 'N/A')
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            pass
        output += f"- **Date**: {date}\n"
        output += f"  - **Type**: {event.get('type', 'N/A')}\n"
        output += f"  - **Body**: {event.get('body', 'N/A')}\n"
        # Summaries
        summaries = event.get('summary', [])
        if summaries:
            output += f"  - **Summary**:\n"
            for summary in summaries:
                output += f"    - {summary}\n"
    return output

def format_docs(docs):
    if not docs:
        return "No documents available.\n"
    output = ""
    for doc in docs:
        date = doc.get('date', 'N/A')
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            pass
        output += f"- **Date**: {date}\n"
        output += f"  - **Type**: {doc.get('type', 'N/A')}\n"
        output += f"  - **Body**: {doc.get('body', 'N/A')}\n"
        # Document links
        doc_items = doc.get('docs', [])
        if doc_items:
            output += f"  - **Documents**:\n"
            for d in doc_items:
                title = d.get('title', 'Document')
                url = d.get('url', None)
                if url:
                    output += f"    - [{title}]({url})\n"
                else:
                    output += f"    - {title}\n"
        # Summaries
        summaries = doc.get('summary', [])
        if summaries:
            output += f"  - **Summary**:\n"
            for summary in summaries:
                output += f"    - {summary}\n"
    return output

# Analysis Functions
def analyze_relevance(law_text, company_description):
    logger.info("Starting relevance analysis.")
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
    structured_llm = llm.with_structured_output(RelevanceResult)
    prompt_template = """
Given the following law text:

{law_text}

And the following description of a company:

{company_description}

Question: Is this law relevant for the described company? Briefly justify your answer.
"""
    prompt = PromptTemplate(
        input_variables=["law_text", "company_description"],
        template=prompt_template,
    )
    inputs = {
        "law_text": law_text[:3000],  # Limit to avoid exceeding token limit
        "company_description": company_description,
    }
    try:
        response = structured_llm.invoke(prompt.format(**inputs))
        logger.info("Received response from LLM for relevance analysis.")
        return response
    except Exception as e:
        logger.error(f"Error during LLM relevance analysis: {e}")
        return None

def perform_predefined_analysis(law_text):
    logger.info("Starting predefined analysis.")
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)
    structured_llm = llm.with_structured_output(AnalysisResult)
    prompt_template = """
It is intended to develop an AI-based tool whose purpose is to analyze and summarize current and ongoing legislative procedures of the EU and the Federal Republic of Germany. The goal is to inform users (which include legal professionals and private businesses) about upcoming legislative changes and legislative procedures.

However, only laws and legislative procedures relevant to the users should be analyzed and processed.

Therefore, your task is to review the content of the law to determine whether it falls under one or more of the following (legal) subject areas. Briefly justify your answer:
	•	Data Protection: This includes laws that serve to protect personal data and privacy, and which, among other things, determine how data may be collected, processed, stored, and shared. This includes, but is not limited to, the following laws: General Data Protection Regulation (also GDPR or Regulation (EU) 2016/679); the Law Enforcement Directive or Directive (EU) 2016/680); the Federal Data Protection Act as well as the data protection laws of the federal states; social data protection; health data protection.
	•	Data Regulation: This encompasses laws that establish the legal frameworks and requirements regarding the handling of data, the usability of data, and the exchange of data across various sectors. This includes, but is not limited to, the following laws: Digital Markets Act (also DMA or Regulation (EU) 2022/1925); Digital Services Act (also DSA or Regulation (EU) 2022/2065); Data Act (also DA or Regulation (EU) 2023/2854); Data Governance Act (also DGA or Regulation (EU) 2022/868); European Health Data Space (also European Health Data Space or EHDS); Health Data Usage Act (also GDNG).
	•	Digital Products and Services: This includes laws that set conditions regarding intermediary services such as host providers, online marketplaces, social networks, and cloud systems or applications (Digital Services), as well as regarding products that are created and provided in digital form, such as computer programs, apps, music files, e-books, or digital video games (Digital Products). This includes, but is not limited to, the following laws: Digital Services Act (also DSA or Regulation (EU) 2022/2065); AI Regulation (also AI Act or Regulation (EU) 2024/1689); AI Liability Directive (also AI Liability Directive or RL (EU) 2022/0303); Digital Services Law.
	•	Artificial Intelligence: This encompasses laws that regulate Artificial Intelligence. This includes, but is not limited to, the following laws: AI Regulation (also AI Act or Regulation (EU) 2024/1689); AI Liability Directive (also AI Liability Directive or RL (EU) 2022/0303); Product Liability Directive (also Directive (EU) 2022/0302).
	•	Cybersecurity: This includes laws that deal with the requirements and standards of cybersecurity, IT security, and/or security in information technology. This includes, but is not limited to, the following laws: Cyber Resilience Regulation (also Cyber Resilience Act, CRA); Cyber Solidarity Regulation (also Cyber Solidarity Act, CSA); Network and Information Security Directive (also NIS-2 or Directive (EU) 2022/2555); Regulation on Digital Operational Resilience (also DORA or Regulation (EU) 2022/2554).

Create a brief summary of the following law text:

{law_text}

Then analyze whether the law falls into the above-mentioned subject areas, and if it is relevant for each subject area. Briefly justify your answers.
"""
    prompt = PromptTemplate(
        input_variables=["law_text"],
        template=prompt_template,
    )
    inputs = {
        "law_text": law_text[:3000],  # Limit to avoid exceeding token limit
    }
    try:
        response = structured_llm.invoke(prompt.format(**inputs))
        logger.info("Received response from LLM for predefined analysis.")
        return response
    except Exception as e:
        logger.error(f"Error during LLM predefined analysis: {e}")
        return None

# Initialize Widgets
search_button = pn.widgets.Button(name='Get Laws', button_type='primary')
message_pane = pn.pane.Markdown()
laws_table = pn.widgets.Tabulator(pagination='remote', page_size=20, sizing_mode='stretch_both')
details_pane = pn.pane.Markdown(sizing_mode='stretch_both', height=400)
company_description = pn.widgets.TextAreaInput(
    name='Company Description',
    placeholder='Enter a description of your company.',
    height=150,
    sizing_mode='stretch_width'
)
relevance_check_button = pn.widgets.Button(name='Check Relevance', button_type='success')
relevance_result_pane = pn.pane.Markdown(sizing_mode='stretch_width', height=200)
automatic_analysis_button = pn.widgets.Button(name='Perform Analysis', button_type='primary')
automatic_analysis_result_pane = pn.pane.Markdown(sizing_mode='stretch_width', height=400)

# Define Callbacks
def search_laws(event):
    logger.info("Get Laws button clicked.")
    message_pane.object = 'Loading data...'
    vorgaenge = get_vorgaenge()
    if vorgaenge:
        df = pd.DataFrame([
            {
                'ID': v.get('procedure', {}).get('reference', 'No ID'),
                'Title': v.get('procedure', {}).get('title', 'No Title')
            }
            for v in vorgaenge
        ])
        laws_table.value = df
        message_pane.object = f"{len(vorgaenge)} laws loaded."
        pn.state.vorgaenge = vorgaenge  # Store the list of laws for later use
        logger.info(f"{len(vorgaenge)} laws loaded into table.")
    else:
        message_pane.object = "No laws found."
        logger.warning("No laws found to display.")

search_button.on_click(search_laws)

def on_law_select(event):
    selected_row = laws_table.selection
    if selected_row:
        selected_index = selected_row[0]
        vorgang_id = laws_table.value.iloc[selected_index]['ID']
        logger.info(f"Law with ID {vorgang_id} selected.")
        # Retrieve the selected law from pn.state.vorgaenge
        vorgaenge = pn.state.vorgaenge
        vorgang_details = next((item for item in vorgaenge if item.get('procedure', {}).get('reference') == vorgang_id), None)
        if vorgang_details:
            # Extract sections
            meta = vorgang_details.get('meta', {})
            procedure = vorgang_details.get('procedure', {})
            committees = vorgang_details.get('committees', [])
            council = vorgang_details.get('council', [])
            commission = vorgang_details.get('commission', [])
            events = vorgang_details.get('events', [])
            docs = vorgang_details.get('docs', [])
            
            # Build the details markdown
            details = f"# Details of the Selected Law\n\n"
            details += f"## Meta\n{format_meta(meta)}\n"
            details += f"## Procedure\n{format_procedure(procedure)}\n"
            details += f"## Committees\n{format_committees(committees)}\n"
            details += f"## Council\n{format_council(council)}\n"
            details += f"## Commission\n{format_commission(commission)}\n"
            details += f"## Events\n{format_events(events)}\n"
            details += f"## Documents\n{format_docs(docs)}\n"
            
            # Extract the most recent proposal link from 'docs'
            proposal_url = None
            if docs:
                # Find the latest document with type 'Legislative proposal'
                legislative_proposals = [doc for doc in docs if doc.get('type') == 'Legislative proposal']
                if legislative_proposals:
                    # Sort by date descending
                    legislative_proposals.sort(key=lambda x: x.get('date', ''), reverse=True)
                    latest_proposal = legislative_proposals[0]
                    proposal_docs = latest_proposal.get('docs', [])
                    # Find the URL in 'docs'
                    for d in proposal_docs:
                        if 'url' in d:
                            proposal_url = d['url']
                            break
                    if proposal_url:
                        details += f"\n## Latest Proposal Link\n[View Proposal]({proposal_url})\n"
                        # Store the content for analysis
                        pn.state.law_text = fetch_document_text(proposal_url)
                        logger.info(f"Stored law text for analysis from {proposal_url}")
                    else:
                        details += "\n**No link to the latest proposal found.**\n"
                        pn.state.law_text = None
                        logger.warning("No proposal URL found.")
                else:
                    details += "\n**No legislative proposals found.**\n"
                    pn.state.law_text = None
                    logger.warning("No legislative proposals found in docs.")
            else:
                details += "\n**No documents available.**\n"
                pn.state.law_text = None
                logger.warning("No docs found.")

            details_pane.object = details

            # Store selected vorgang_id
            pn.state.vorgang_id = vorgang_id
            logger.info(f"Law ID {vorgang_id} stored in state.")
        else:
            details_pane.object = "Could not load details."
            logger.error(f"Could not load details for law ID {vorgang_id}.")
    else:
        details_pane.object = "Please select a law."
        logger.warning("No law selected.")

laws_table.param.watch(on_law_select, 'selection')

def check_relevance(event):
    logger.info("Relevance check button clicked.")
    if hasattr(pn.state, 'law_text') and pn.state.law_text:
        law_text = pn.state.law_text
        company_desc = company_description.value
        logger.info("Performing relevance analysis.")
        result = analyze_relevance(law_text, company_desc)
        if result:
            relevance_result_pane.object = f"""
### Relevance Analysis Result

**Relevance**: {'Yes' if result.is_relevant else 'No'}  
**Justification**: {result.reason}  
"""
            logger.info("Relevance analysis completed and result displayed.")
        else:
            relevance_result_pane.object = "Could not perform relevance analysis."
            logger.error("Relevance analysis failed.")
    else:
        relevance_result_pane.object = "No valid law text available."
        logger.warning("No valid law text available for relevance analysis.")

relevance_check_button.on_click(check_relevance)

def perform_analysis(event):
    logger.info("Automatic analysis button clicked.")
    if hasattr(pn.state, 'law_text') and pn.state.law_text:
        law_text = pn.state.law_text
        logger.info("Performing automatic analysis.")
        result = perform_predefined_analysis(law_text)
        if result:
            analyses_markdown = ""
            for analysis in result.analyses:
                analyses_markdown += f"- **Thematic Area**: {analysis.topic}\n"
                analyses_markdown += f"  - **Relevant**: {'Yes' if analysis.relevant else 'No'}\n"
                analyses_markdown += f"  - **Justification**: {analysis.reason}\n"
            automatic_analysis_result_pane.object = f"""
### Automatic Analysis Result

**Summary**: {result.summary}

**Analyses**:
{analyses_markdown}
"""
            logger.info("Automatic analysis completed and result displayed.")
        else:
            automatic_analysis_result_pane.object = "Could not perform analysis."
            logger.error("Automatic analysis failed.")
    else:
        automatic_analysis_result_pane.object = "No valid law text available."
        logger.warning("No valid law text available for automatic analysis.")

automatic_analysis_button.on_click(perform_analysis)

# Create the Template
template = BootstrapTemplate(title='REG Monitoring')

# Header
template.header.append(pn.Row(pn.pane.Markdown("# EU Legislative Acts Analysis")))

# Tabs
tabs = pn.Tabs(tabs_location='above')

# Law Search Tab
law_search_tab = pn.Column(
    pn.Row(search_button, message_pane),
    pn.layout.Divider(),
    pn.Row(
        pn.Column('## List of Laws', laws_table),
        pn.Column('## Law Details', details_pane)
    )
)

# Analysis Tab
analysis_tab = pn.Column(
    pn.Row(
        pn.Column('### Company Description', company_description),
        pn.Column('### Relevance Analysis', relevance_check_button, relevance_result_pane)
    ),
    pn.layout.Divider(),
    pn.Row(
        pn.Column('### Automatic Analysis', automatic_analysis_button, automatic_analysis_result_pane)
    )
)

# Add Tabs to the main area
tabs.extend([
    ('Law Search', law_search_tab),
    ('Analysis', analysis_tab)
])

# Add Tabs to the template
template.main.append(tabs)

# Serve the Panel App
template.servable()
