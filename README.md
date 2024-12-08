# parltrack-monitoring

Documentation for EU Legislative Acts Analysis Tool

Overview

This tool facilitates the analysis of EU legislative acts with a focus on assessing relevance to businesses and predefined legal topics. Built with Panel and integrated with OpenAI’s GPT-powered APIs, it supports fetching, processing, and analyzing legislative documents.

Requirements

Libraries Used
	•	Panel: Used for building the interactive dashboard.
	•	Requests: Handles HTTP requests to fetch document content.
	•	Logging: Logs operational information and errors.
	•	PyPDF2: Extracts text from PDF documents.
	•	LangChain: Integrates AI-driven language analysis.
	•	Pydantic: Provides structured validation for models.
	•	Pandas: Manages tabular data in the laws table.
	•	BootstrapTemplate (Panel): A responsive template for the dashboard.

Features

1. Law Retrieval
	•	Load Laws: Retrieves legislative acts of type “COD” from a JSON dataset.
	•	Display in Table: Laws are displayed with their ID and title using Panel's Tabulator.

2. Law Details
	•	Interactive Selection: Users select a law to view metadata, procedure details, committee information, council updates, commission summaries, event timelines, and associated documents.
	•	Document Fetching: Retrieves the latest legislative proposal (PDF or HTML) for analysis.

3. Relevance Analysis
	•	Company Context: Users provide a company description.
	•	AI Evaluation: Determines the relevance of the law for the described company using a structured prompt and OpenAI’s language model.

4. Predefined Analysis
	•	Legal Topics: Analyzes if the law pertains to predefined areas like data protection, AI, cybersecurity, etc.
	•	Summary and Breakdown: Provides a summary of the law and justifies relevance for each topic.

Components

Pydantic Models
	•	RelevanceResult: Captures the relevance and justification for a company’s context.
	•	TopicAnalysis: Details topic-specific analysis with relevance and reasoning.
	•	AnalysisResult: Contains the law’s summary and all topic analyses.

Workflow

1. Search for Laws
	•	Button: Fetches laws using the Get Laws button.
	•	Table: Displays up to 100 laws in a table.

2. View Law Details
	•	Select from Table: Click a law to view details like:
	•	Metadata
	•	Legislative Procedure
	•	Committees
	•	Council Updates
	•	Commission Information
	•	Events
	•	Documents (latest legislative proposal link, if available)

3. Perform Relevance Analysis
	•	Input: Provide a company description.
	•	Process: Analyze the relevance of the selected law to the company.
	•	Output: Displays relevance and justification.

4. Predefined Analysis
	•	Process: Checks if the law falls under predefined legal topics.
	•	Output: Provides a summary and detailed topic analysis with relevance justifications.

Panels and Widgets

Law Search Panel
	•	Search Button: Fetches laws from a JSON dataset.
	•	Table: Displays laws with pagination.
	•	Details Panel: Shows metadata and associated documents.

Analysis Panel
	•	Company Description Input: Text area to describe the company.
	•	Relevance Button: Initiates AI-powered relevance analysis.
	•	Automatic Analysis Button: Starts predefined topic analysis.

Key Functions

Data Fetching
	•	load_json_data: Parses legislative acts from a JSON file.
	•	fetch_document_text: Fetches and extracts text from legislative proposal documents.

Formatting Helpers
	•	Functions like format_meta, format_procedure, and format_committees structure data for display in markdown format.

AI Analysis
	•	analyze_relevance: Determines if a law is relevant to the described company.
	•	perform_predefined_analysis: Analyzes the law against predefined legal topics.

Running the Application
	1.	Set API Key: Ensure the OPENAI_API_KEY is set in your environment or keys.py.
	2.	Serve the Dashboard: Run the script and access the application on the specified server address.

Sample Usage
	1.	Start the tool.
	2.	Fetch and view laws.
	3.	Select a law and review its details.
	4.	Provide a company description.
	5.	Perform relevance or topic analysis.

Error Handling
	•	Invalid API Key: Prompts to set the OPENAI_API_KEY.
	•	Document Errors: Logs issues with fetching or decoding data.
	•	Analysis Errors: Captures and logs errors during AI analysis.

Extending Functionality
	•	Add new legal topics for predefined analysis by updating the perform_predefined_analysis prompt.
	•	Integrate additional document formats for text extraction.
	•	Connect to dynamic data sources like APIs for legislative updates.
