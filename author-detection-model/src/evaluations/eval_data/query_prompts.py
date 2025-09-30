queries = [
        {
            "id": "Q1",
            "text": """
                        Extract the names of all the authors, copyright holders, maintainers and contributers given in the text.
                        Do not include any other information.
                    """,
            "type": "extract-name",
            "about": "Extract name."
        },
        {
            "id": "Q2",
            "text": """
                        You are a system for finding all authors, copyright holders, maintainers or contributors information from given text.

                        Your are given a text that includes texts from various parts of a source code of a project.
                        You must return your response as separate lines. Each line must contain only name. Each name must be present inside the text.
                        Do not include any other information.
                    """,
            "type": "extract-name-with-context-input",
            "about": "Query with context. Extract name."
        },
        {
            "id": "Q3",
            "text": """
                        You are a system for finding all authors, copyright holders, maintainers or contributors information from given text.

                        Your are given a text that includes texts from various parts of a source code of a project.
                        You must return your response as separate lines. Each line must contain only name. Each name must be present inside the text.
                        Do not include any other information.

                        Example response:
                            Kendall Riley
                            James Trucker
                            Kensley Keller

                        Use above example response only as a reference for formatting your answer.
                    """,
            "type": "extract-name-with-context-and-example-input",
            "about": "Query with context and example. Extract name."
        },
        {
            "id": "Q4",
            "text": """
                        You are a system for finding all authors, copyright holders, maintainers or contributors information from given text.

                        Your are given a text that includes texts from various parts of a source code of a project.
                        Your task is to extract the names of all the authors, copyright holders, maintainers and contributers given in the text.
                        You must return your response as separate lines. Each line must contain name and their role.
                        Each name must be present inside the text.
                        Role must be one of the following: author, maintainer, contributor, or copyright holder.
                        Do not include any other information.

                        Example response:
                            Kendall Riley, Author
                            James Trucker, Author
                            Kensley Keller, Maintainer

                        Use above example response only as a reference for formatting your answer.
                    """,
            "type": "extract-name-role-with-context-example-input",
            "about": "Query with context and example. Extract name and role."
        },
        {
            "id": "Q5",
            "text": """
                        You are a system for finding all authors, copyright holders, maintainers or contributors information from given text.

                        Your are given a text that includes information from various parts of a source code of a project.
                        Your task is to extract the names of all the persons that are authors, copyright holders, maintainers or contributers mentioned inside the text.

                        Follow these guidelines for giving out your response:
                            - Response must be in separate lines.
                            - Each line must contain name, role and very short description about the contribution.
                            - Each name must strictly must be present inside the text and must be a valid common name of an individual.
                            - Each name must be in separate line. Names must not be grouped together based on their role or contribution.
                            - Role must be one of the following: author, maintainer, contributor, or copyright holder.
                            - Description of the contribution must be understandable and less that 5 words if possible.

                        Do not return answers in any other format.
                    """,
            "type": "extract-name-role-description-with-context-guideline-input",
            "about": "Query with context and guideline. Extract name, role, and contribution."
        },
        {
            "id": "Q6",
            "text": """
                        You are a system for finding all authors, copyright holders, maintainers or contributors information from given text.

                        Your are given a text that includes information from various parts of a source code of a project.
                        Your task is to extract the names of all the persons that are authors, copyright holders, maintainers or contributers mentioned inside the text.

                        Follow these guidelines for giving out your response:
                            - Response must be in separate lines.
                            - Each line must contain name, role and very short description about the contribution.
                            - Each name must strictly must be present inside the text and must be a valid common name of an individual or an organization.
                            - Variables or flags inside the program code must not be identified as name.
                            - Names must not be grouped together based on their role or contribution. Each name must be in separate line.
                            - Role must be one of the following: author, maintainer, contributor, or copyright holder.
                            - Description of the contribution must be understandable and less that 5 words if possible.

                        Do not return answers in any other format.

                        Example Response:
                            Kendall Riley, Author, Wrote abc.py
                            James Trucker, Author, code.c
                            Kensley Keller, Maintainer, Maintained project ABC until 2007

                        Do not return answers in any other format and use above example response only as a reference for formatting your answer.
                    """,
            "type": "extract-name-role-description-with-context-guideline-example-input",
            "about": "Query with context, guideline and example. Extract name, role, and contribution."
        },
    ]

import json

with open("query_prompts.json", "w") as f:
    json.dump(queries, f)