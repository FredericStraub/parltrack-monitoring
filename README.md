#EU Legislative Acts Analysis Tool

Overview

Disclaimer: super crapy and just used for experimentation. shoutout parltrack https://parltrack.org/

The EU Legislative Acts Analysis Tool is an interactive application designed to analyze EU legislative acts, focusing on their relevance to businesses and predefined legal topics. The tool uses OpenAI’s GPT-powered APIs for language analysis and is built with Panel for a seamless user interface. 

Features

1. Law Retrieval
	•	Load and display EU legislative acts of type “COD” (Ordinary legislative procedure).
	•	Display laws in a table with their ID and title.

2. Law Details
	•	View detailed information about a selected law, including:
	•	Metadata
	•	Legislative procedure details
	•	Committees involved
	•	Council updates
	•	Commission summaries
	•	Events timeline
	•	Documents (including the latest legislative proposal link, if available).

3. Relevance Analysis
	•	Input: A description of your company.
	•	AI-Powered Analysis: Determines if the law is relevant to the company and provides a justification.

4. Predefined Analysis
	•	Analyze the law against predefined legal topics, including:
	•	Data Protection
	•	Data Regulation
	•	Digital Products and Services
	•	Artificial Intelligence
	•	Cybersecurity
	•	Output: A summary and detailed topic analysis with justifications.

Installation

Prerequisites
	•	Python 3.8+
	•	OpenAI API Key

Steps
	1.	Clone the repository:

git clone https://github.com/your-username/eu-legislative-acts-analysis.git
cd eu-legislative-acts-analysis


	2.	Install dependencies:

pip install -r requirements.txt


	3.	Set your OpenAI API Key:
	•	Add it to an environment variable:

export OPENAI_API_KEY="your_openai_api_key"


	•	Or update the keys.py file:

OPENAI_API_KEY = "your_openai_api_key"


	4.	Run the application:

python app.py


	5.	Open the application in your browser at the address displayed in the terminal.

Usage

1. Search for Laws
	•	Click the Get Laws button to load and display laws in a table.
	•	Select a law to view its details.

2. View Law Details
	•	Review detailed information, including metadata, procedures, and associated documents.

3. Relevance Analysis
	•	Provide a description of your company.
	•	Click Check Relevance to analyze if the law is relevant for your company.

4. Predefined Analysis
	•	Click Perform Analysis to evaluate the law against predefined legal topics.
	•	View a summary and detailed analysis of relevance for each topic.

Components

Pydantic Models
	•	RelevanceResult: Captures the relevance and justification for a company.
	•	TopicAnalysis: Details topic-specific analysis with relevance and reasoning.
	•	AnalysisResult: Contains the law’s summary and all topic analyses.

Interactive Widgets
	•	Search Button: Fetches laws.
	•	Table: Displays laws with pagination.
	•	Details Pane: Shows metadata, procedures, and documents.
	•	Text Area: Input for company description.
	•	Buttons: Trigger relevance and predefined analyses.
	•	Markdown Panes: Display analysis results.

Technologies Used
	•	Panel: For building the interactive web app.
	•	OpenAI: Language model for relevance and topic analysis.
	•	PyPDF2: Text extraction from PDF documents.
	•	LangChain: Framework for AI-based workflows.
	•	Pandas: Data manipulation and tabular data display.
	•	Logging: Operational and error logging.

Contributing

Contributions Are Welcome!
	1.	Fork the repository.
	2.	Create a new branch:

git checkout -b feature-name


	3.	Make your changes and commit:

git commit -m "Description of changes"


	4.	Push your branch:

git push origin feature-name


	5.	Open a Pull Request.

License

This project is licensed under the MIT License.

Future Enhancements
	•	Integration with dynamic data sources (e.g., APIs for real-time legislative updates).
	•	Support for additional document formats.
	•	Enhanced topic customization for analysis.

Contact

For questions or feedback, please contact me.
