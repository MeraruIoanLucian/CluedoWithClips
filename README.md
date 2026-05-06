Project Overview: Murder-Mystery Puzzle Solver

Implement a system that takes a murder-mystery puzzle as input, converts it into a formal Knowledge Base (KB), and uses a reasoning engine to identify the solution.1
Phase 1: Data Selection & Acquisition

Source Selection: Choose between using an existing puzzle generator, using specific online puzzle datasets, or building a custom generator.2
Format Specification: Identify if the source data is in text, JSON, or another format that needs to be parsed.3
Phase 2: Reasoning Module Development (Core)

Language Choice: Implement the core reasoning logic exclusively in CLIPS or PROLOG.4
Knowledge Representation:
Design a schema to represent suspects, motives, evidence, and rules within the chosen language.5
Create logic rules that can process puzzle facts to deduce the culprit.4
Data Conversion: Develop a module to convert the raw puzzle data (txt/json) into facts compatible with the CLIPS/PROLOG environment.5
Phase 3: User Interface (UI) Development

Minimalist UI: Build an interface that allows the user to:
View the raw or converted puzzle data.5
Initiate the solving process.6
View the final solution or an error message if no solution exists.6
System Commands: Enable the user to select or add new puzzles through commands or prompts.7
Phase 4: Functional Workflow Implementation

Initialization: User starts the system.8
Input Handling: System parses and validates the puzzle input provided by the user.9
Error Management: If the input is invalid, display a clear error message.10
Execution: The system feeds the converted puzzle into the reasoning module to find the murderer.6
Output: Display the converted knowledge base and the final solution to the user.6

