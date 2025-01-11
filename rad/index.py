from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from ollama import chat
import json
import os

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample Data
data_json = [ {
        "_id": "299c616c-73ff-4dfe-bf15-a20e4d5f7dee",
        "auditInfo": {
            "createdDate": 1709679686,
            "createdUserID": "VCHA0005",
            "createdUserName": "Venkat",
            "updatedDate": 1709679686,
            "updatedUserName": "Venkat",
            "updatedUserid": "VCHA0005"
        },
        "subDetails": {
            "client": {
                "company_id": "C0000",
                "name": "Unknown",
                "recruiter": {
                    "contact": "1234567890",
                    "email": "recruiter1@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RC000"
                }
            },
            "comments": "Vendor name: nayan agrawal\nSubmission done on Friday",
            "date": 1706819365,
            "jobDescription": "Developer",
            "jobRole": "Data Engineer",
            "primeVendor": {
                "company_id": "V0001",
                "name": "Collabera",
                "recruiter": {
                    "contact": "1112223333",
                    "email": "recruiterA@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RV001"
                }
            },
            "profile": {
                "_id": "VCHA0005",
                "firstName": "Venkat Durga Prasad",
                "lastName": "chagganttipati"
            },
            "salesRecruiter": "Pushpak",
            "status": "Applied",
            "vendor": {
                "company_id": "V0001",
                "name": "Collabera",
                "recruiter": {
                    "contact": "1234532123",
                    "email": "nayan.agrawal@collabera.com",
                    "name": "Nayan Agrawal",
                    "rec_id": "R0013"
                }
            },
            "workLocation": "1000 Harbor Blvd, Weehawken, NJ 07086"
        },
        "tags": None
    },
    {
        "_id": "3989093e-56e9-4b1a-ae49-0eb6482c9845",
        "auditInfo": {
            "createdDate": 1711749337,
            "createdUserID": "NBAN0002",
            "createdUserName": "Narendra",
            "updatedDate": 1711749337,
            "updatedUserName": "NBAN0002",
            "updatedUserid": "NBAN0002"
        },
        "subDetails": {
            "client": {
                "company_id": "C0003",
                "name": "Ally Finacials",
                "recruiter": {
                    "contact": "1234567890",
                    "email": "recruiter1@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RC000"
                }
            },
            "comments": "Title: Python Developer\nLocation: NC, Charlotte/Detroit, MI\nDuration: 12+ Months\n          \nJob Description:\nAssists higher level developers, or may be responsible for coding, testing, supporting and debugging new or enhanced software and responding to business client issues. Works with higher level developers to learn about design and variety of problems that can exist with current software applications and technologies. Ability to work independently to define, manage, and complete activities. May interact directly with business clients for purposes of gathering and conveying information. Analyzes issues and uses judgment to make decisions. Provides constructive feedback to the team, suggesting actions to improve individual and team performance. Knowledge of coding, testing, supporting and debugging software. Ability to gather and convey information to business clients. Understands how the IT group operates and how his/her role meets customer needs and creates value. Outlines potential cost/savings outcomes of technology use. Tailors the information to appeal to the level and interest of others. To the extent that it is reasonable, goes the extra mile to make sure that each individuals needs are met. Identifies opportunities or problems and acts quickly and decisively to respond to the situation. Takes initiative to work on challenging or stretch work assignments. Takes full advantage of opportunities to develop his/her skills.\n\nMandatory:\nExtensive software engineering experience in Python; ** Extensive experience with AWS; ** Experience in MicroService design and architecture; **Must have excellent communication skills.",
            "date": 1709065242,
            "jobDescription": "Extensive software engineering experience in Python; ** Extensive experience with AWS; ** Experience in MicroService design and architecture; **Must have excellent communication skills and work well. ",
            "jobRole": "Immediate Hiring for Python Developer at NC, Charlotte / Detroit, MI",
            "primeVendor": {
                "company_id": "V0002",
                "name": "Pyramid Consulting",
                "recruiter": {
                    "contact": "2314212345",
                    "email": "Dimple.Hirani@pyramidci.com",
                    "name": "Dimple Hirani",
                    "rec_id": "R0002"
                }
            },
            "profile": {
                "_id": "NBAN0002",
                "firstName": "Narendra",
                "lastName": "Bandarupalli"
            },
            "salesRecruiter": "Tarun Gundu",
            "status": "Applied",
            "vendor": {
                "company_id": "V0002",
                "name": "Pyramid Consulting",
                "recruiter": {
                    "contact": "21433213454",
                    "email": "Dimple.Hirani@pyramidci.com",
                    "name": "Dimple Hirani",
                    "rec_id": "R0002"
                }
            },
            "workLocation": "Charlotte, NC / Detroit, MI"
        },
        "tags": None
    },
    {
        "_id": "58887810-54a9-4681-b20f-533182e46dc3",
        "auditInfo": {
            "createdDate": 1709679455,
            "createdUserID": "VCHA0005",
            "createdUserName": "Venkat",
            "updatedDate": 1709679455,
            "updatedUserName": "Venkat",
            "updatedUserid": "VCHA0005"
        },
        "subDetails": {
            "client": {
                "company_id": "C0000",
                "name": "Unknown",
                "recruiter": {
                    "contact": "1234567890",
                    "email": "recruiter1@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RC000"
                }
            },
            "comments": "Responsibilities\n\n·       Monitor and optimize the performance of cloud resources to ensure efficient utilization and cost-effectiveness.\n\n·       Implement and maintain security measures to protect data and systems within the AWS environment, including IAM policies, security groups, and encryption mechanisms.\n\n·       Migrate the application data from legacy databases to Cloud based solutions (Redshift, DynamoDB, etc) for high availability with low cost\n\n·       Develop application programs using Big Data technologies like Apache Hadoop, Apache Spark, etc with appropriate cloud-based services like Amazon AWS, etc.\n\n·       Build data pipelines by building ETL processes (Extract-Transform-Load)\n\n·       Implement backup, disaster recovery, and business continuity strategies for cloud-based applications and data.\n\n·       Responsible for analyzing business and functional requirements which involves a review of existing system configurations and operating methodologies as well as understanding evolving business needs\n\n·       Analyze requirements/User stories at the business meetings and strategize the impact of requirements on different platforms/applications, convert the business requirements into technical requirements\n\n·       Participating in design reviews to provide input on functional requirements, product designs, schedules and/or potential problems\n\n·       Understand current application infrastructure and suggest Cloud based solutions which reduces operational cost, requires minimal maintenance but provides high availability with improved security\n\n·       Perform unit testing on the modified software to ensure that the new functionality is working as expected while existing functionalities continue to work in the same way\n\n·       Coordinate with release management, other supporting teams to deploy changes in production environment",
            "date": 1709325161,
            "jobDescription": "Developer",
            "jobRole": "Data Engineer",
            "primeVendor": {
                "company_id": "V0017",
                "name": "Genpact",
                "recruiter": {
                    "contact": "1112223333",
                    "email": "recruiterA@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RV001"
                }
            },
            "profile": {
                "_id": "VCHA0005",
                "firstName": "Venkat Durga Prasad",
                "lastName": "chagganttipati"
            },
            "salesRecruiter": "Dileep",
            "status": "Applied",
            "vendor": {
                "company_id": "V0012",
                "name": "Elgebra",
                "recruiter": {
                    "contact": "324565432456",
                    "email": "shalinim@elgebra.com",
                    "name": "Shalini Mishra",
                    "rec_id": "R00010"
                }
            },
            "workLocation": "California"
        },
        "tags": None
    },
    {
        "_id": "6011a4b5-7012-4463-b5de-b3d9280b2178",
        "auditInfo": {
            "createdDate": 1709582960,
            "createdUserID": "NBAN0002",
            "createdUserName": "Narendra",
            "updatedDate": 1709582960,
            "updatedUserName": "Narendra",
            "updatedUserid": "NBAN0002"
        },
        "subDetails": {
            "client": {
                "company_id": "C0001",
                "name": "IBM/ Delta",
                "recruiter": {
                    "contact": "1234567890",
                    "email": "recruiter1@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RC000"
                }
            },
            "comments": "Python Developer\n\nAtlanta, GA\n\nNeed someone who is very strong with Python programming and work on the AWS services. Need DevOps exp. along with Python  \n\n•    5+ years of work experience in Software Engineering\n    •    3+ years of work/educational experience in Artificial Intelligence/Machine Learning\n    •    Experience with Agile Software Development Lifecycles and DevOps/DevSecOps\n    •    Development experience on AWS, AWS Sagemaker required\n    •    Experience with one or more general purpose programming languages including but not limited to: Python, R, Scala, Spark\n    •    Experience with one or more of the following: Natural Language Processing, sentiment analysis, classification, pattern recognition.\n    •    Development experience with AI frameworks such as TensorFlow, Microsoft CNTK, scikit, Keras, Caffe, Gluon, Torch.\n    •    Familiarity with GenAI technology stack, including frameworks for prompt engineering, guardrails for GenAI applications, and LLM fine-tuning\n    •    Experience working with VectorDBs and other data infrastructure required to efficiently support Generative AI training pipelines and production applications \n    •    Experience training and maintaining large language models\n    •    Experience with production-grade development, integration and support\n\n    •    Experience and familiarity presenting to technical and business audiences.",
            "date": 1709582845,
            "jobDescription": "Need someone who is very strong with Python programming and work on the AWS services. Need DevOps exp. along with Python",
            "jobRole": "IBM :: Python Position",
            "primeVendor": {
                "company_id": "V0001",
                "name": "Collabera",
                "recruiter": {
                    "contact": "324564324567",
                    "email": "varsha.agrawal@collabera.com",
                    "name": "Varsha Agarwal",
                    "rec_id": "R0001"
                }
            },
            "profile": {
                "_id": "NBAN0002",
                "firstName": "Narendra",
                "lastName": "Bandarupalli"
            },
            "salesRecruiter": "Pushpak",
            "status": "Applied",
            "vendor": {
                "company_id": "V0001",
                "name": "Collabera",
                "recruiter": {
                    "contact": "234564324567",
                    "email": "varsha.agrawal@collabera.com",
                    "name": "Varsha Agarwal",
                    "rec_id": "R0001"
                }
            },
            "workLocation": "Atlanta, GA"
        },
        "tags": None
    },
    {
        "_id": "f1c646cc-70cc-4978-8cbd-d1e1d2ef6bc0",
        "auditInfo": {
            "createdDate": 1709675653,
            "createdUserID": "NEND0009",
            "createdUserName": "NAVEEN SIVA KUMAR",
            "updatedDate": 1709675653,
            "updatedUserName": "NAVEEN SIVA KUMAR",
            "updatedUserid": "NEND0009"
        },
        "subDetails": {
            "client": {
                "company_id": "C0004",
                "name": "The State of Wisconsin Madison",
                "recruiter": {
                    "contact": "1234567890",
                    "email": "recruiter1@example.com",
                    "name": "Unknown Recruiter",
                    "rec_id": "RC000"
                }
            },
            "comments": "",
            "date": 1709589249,
            "jobDescription": "• JavaScript, KendoUI \u0026 JQuery – strong technical mastery is mandatory • .NET MVC with C# - strong technical mastery is mandatory • SQLServer - strong technical mastery is mandatory • Full stack development • Entity Framework",
            "jobRole": ".NET Web Developer III - N/A 12786",
            "primeVendor": {
                "company_id": "V0003",
                "name": "Focused HR Solutions",
                "recruiter": {
                    "contact": "234564324567",
                    "email": "recruiter4@fhr-solutions.com",
                    "name": "Monika",
                    "rec_id": "R0003"
                }
            },
            "profile": {
                "_id": "NEND0009",
                "firstName": "Naveen Shiva Kumar",
                "lastName": "Endeti"
            },
            "salesRecruiter": "Dileep",
            "status": "Applied",
            "vendor": {
                "company_id": "V0003",
                "name": "Focused HR Solutions",
                "recruiter": {
                    "contact": "23456543567",
                    "email": "recruiter4@fhr-solutions.com",
                    "name": "Monika",
                    "rec_id": "R0003"
                }
            },
            "workLocation": "Wisconsin, Madison"
        },
        "tags": None
    }]
# FAISS Index file name
INDEX_FILE = "think_index"

style = ""

def load_vectors(data):
    """
    Load the FAISS index or create one from the input data.
    """
    if os.path.exists(INDEX_FILE):
        print("Loading existing FAISS index...")
        index = faiss.read_index(INDEX_FILE)
    else:
        print("Creating FAISS index...")
        # Prepare documents for embedding
        documents = [", ".join(f"{key}: {value}" for key, value in item.items()) for item in data]
        embeddings = embedding_model.encode(documents)

        # Create FAISS index
        embedding_dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(embedding_dim)
        index.add(np.array(embeddings))

        # Save the FAISS index
        faiss.write_index(index, INDEX_FILE)
        print("FAISS index created and saved.")

    print("FAISS index loaded successfully.")
    return index

def similarity_search(query, index, data, top_k=1):
    """
    Perform similarity search to find the top_k most relevant documents.
    """
    try:
        query_embedding = embedding_model.encode([query])
        distances, indices = index.search(query_embedding, top_k)

        results = [data[idx] for idx in indices[0] if idx != -1]  # Avoid invalid indices
        return results
    except Exception as e:
        print(f"Error during similarity search: {e}")
        return []

def generate_response(filter_doc, user_query):
    """
    Generate a response using the llama model based on the filtered document and query.
    """
    context = f"Respond to the question based on given input. Input:{filter_doc}. Question:{user_query}"
    print(context)
    response = chat(model="llama3.1:8b", stream=True, messages=[
        {"role": "system", "content": "You are a helpful HR assistant. You should respond to user queries. based on user provided input."},
        {"role": "user", "content": context}
    ])

    print("\nResponse:")
    for message in response:
        print(message['message']['content'], end='', flush=True)

def main():
    # Load or create FAISS index
    index = load_vectors(data_json)

    print("\n--- Chat Interface ---")
    while True:
        try:
            user_query = input("\nEnter your question (or type 'exit' to quit): ").strip()
            if user_query.lower() == "exit":
                print("Goodbye!")
                break

            # Perform similarity search
            top_results = similarity_search(user_query, index, data_json, top_k=10)

            if top_results:
                print("\nMatching Records:")
                for record in top_results:
                    print(json.dumps(record, indent=4))

                # Generate a response based on the first result
                generate_response(top_results, user_query)
            else:
                print("No relevant data found for your query. Try rephrasing.")

        except KeyboardInterrupt:
            print("\nExiting. Have a nice day!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()