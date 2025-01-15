import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from spacy.matcher import PhraseMatcher
from langchain_ollama import ChatOllama, OllamaEmbeddings
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor

class SkillKeywordExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.model = OllamaEmbeddings(base_url="http://localhost:11434", model="nomic-embed-text")
        # Initialize skill extractor
        self.skill_extractor = SkillExtractor(self.nlp, SKILL_DB, PhraseMatcher)
        self.multi_word_phrases = ["Mule soft", "Salesforce", "Machine Learning", "Data Science"]
        self.matcher = PhraseMatcher(self.nlp.vocab)
        self._add_multi_word_phrases()
    def _add_multi_word_phrases(self):
        # Add multi-word phrases to the PhraseMatcher
        patterns = [self.nlp.make_doc(phrase) for phrase in self.multi_word_phrases]
        self.matcher.add("MULTI_WORD_PHRASES", None, *patterns)

    def get_skills(self, text):
        annotations = self.skill_extractor.annotate(text)
        full_matched = annotations["results"]["full_matches"]
        semi_matched = annotations["results"]["ngram_scored"]
        skills = list()
        for skill in full_matched:
            skills.append(skill["doc_node_value"])
            
        for skill in semi_matched:
            skills.append(skill["doc_node_value"])
        return skills

    def tokenize_technologies(self, tech_list):
        tokens = []
        for tech in tech_list:
            doc = self.nlp(tech.lower())  # Lowercase to standardize
            tokens.extend([token.text for token in doc if not token.is_stop and not token.is_punct])
        return tokens

    # Function to calculate overall matching percentage
    def calculate_similarity(self, resume, job_description):
        # Tokenize both resume and job description lists of technologies
        tokens_resume = self.tokenize_technologies(resume)
        tokens_job_description = self.tokenize_technologies(job_description)
        print(tokens_resume)
        # Join tokens into strings before encoding
        text_resume = " ".join(tokens_resume)
        text_job_description = " ".join(tokens_job_description)
        
        # Generate embeddings using Ollama embeddings
        embeddings_resume = self.model.embed_documents([text_resume])  # Embed the entire text as a list of strings
        embeddings_job_description = self.model.embed_documents([text_job_description])  # Embed the entire text as a list of strings
        
        # Average the embeddings for each list to get a single vector representation
        avg_embedding_resume = np.mean(embeddings_resume, axis=0)
        avg_embedding_job_description = np.mean(embeddings_job_description, axis=0)
        
        # Calculate cosine similarity between the averaged embeddings
        similarity_score = cosine_similarity([avg_embedding_resume], [avg_embedding_job_description])[0][0]
        
        # Find matching and missing keywords
        matching_keywords = set(tokens_resume).intersection(set(tokens_job_description))
        missing_in_resume = set(tokens_job_description) - set(tokens_resume)
        
        return similarity_score, matching_keywords, missing_in_resume
if __name__ == "__main__":
    extractor = SkillKeywordExtractor()

    # Example job description and resume tech lists
    job_description_tech = ["Python", "Mule soft","Salenium","jira","Cloud"]
    resume_tech = ["Python", "Deep Learning", "Machine Learning", "SQL"]

    # Get similarity score and matching/missing skills
    similarity_score, matching_keywords, missing_in_resume = extractor.calculate_similarity(resume_tech, job_description_tech)

    print(f"Cosine Similarity: {similarity_score:.2f}")
    print(f"Matching Keywords: {matching_keywords}")
    print(f"Missing Keywords in Resume: {missing_in_resume}")