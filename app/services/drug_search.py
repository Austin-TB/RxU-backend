import pandas as pd
import os
from typing import List, Dict, Optional

class DrugSearchService:
    """
    A service to search for drug information, powered by a pandas DataFrame.
    """
    def __init__(self):
        self.df: pd.DataFrame = pd.DataFrame()
        self.load_drug_data()

    def load_drug_data(self):
        try:
            csv_path = os.path.join(os.path.dirname(__file__), "../../data/drugs.csv")
        except NameError:
            csv_path = "data/drugs.csv" 

        if not os.path.exists(csv_path):
            print(f"Warning: Drug data file not found at {csv_path}")
            return

        try:
            self.df = pd.read_csv(csv_path)

            self.df.rename(columns={
                'DrugBank ID': 'drugbank_id',
                'Common name': 'name',
                'Synonyms': 'synonyms',
                'Generic name': 'generic_name',
                'Drug class': 'drug_class',
                'Description': 'description',
                'Alternatives': 'alternatives',
                'side-effects': 'side_effects'
            }, inplace=True)

            self.df['synonyms'] = self.df['synonyms'].fillna('')
            self.df['alternatives'] = self.df['alternatives'].fillna('')
            self.df['side_effects'] = self.df['side_effects'].fillna('')

            print(f"Loaded {len(self.df)} drugs from the dataset into a DataFrame.")

        except Exception as e:
            print(f"Error loading drug data: {e}")
            self.df = pd.DataFrame()

    def search_drugs(self, query: str, limit: int = 10) -> List[Dict]:

        if not query or not query.strip() or self.df.empty:
            return []
        query = query.strip().lower()

        # Create boolean masks for each column to search.
        name_mask = self.df['name'].str.lower().str.contains(query, na=False)
        generic_mask = self.df['generic_name'].str.lower().str.contains(query, na=False)
        synonyms_mask = self.df['synonyms'].str.lower().str.contains(query, na=False)

        combined_mask = name_mask | generic_mask | synonyms_mask

        results_df = self.df[combined_mask]

        return results_df.head(limit).to_dict('records')

    def get_drug_by_id(self, drugbank_id: str) -> Optional[Dict]:

        if self.df.empty:
            return None

        # Filter the DataFrame to find the matching drugbank_id
        result_df = self.df[self.df['drugbank_id'] == drugbank_id]

        if not result_df.empty:
            # Return the first match as a dictionary
            return result_df.iloc[0].to_dict()

        return None

    def get_random_drugs(self, count: int = 5) -> List[Dict]:

        if self.df.empty or len(self.df) < count:
            return self.df.to_dict('records')

        # Use the DataFrame's sample method to get random rows
        return self.df.sample(n=count).to_dict('records')

# Global instance for easy access
drug_search_service = DrugSearchService()

# --- Example Usage ---
if __name__ == '__main__':
    # Ensure the service loaded data before proceeding
    if not drug_search_service.df.empty:
        print("\n--- Searching for 'Aspirin' ---")
        aspirin_results = drug_search_service.search_drugs("Aspirin")
        for drug in aspirin_results:
            print(f"  - Found: {drug['name']} (ID: {drug['drugbank_id']})")

        print("\n--- Searching for 'Ibu' ---")
        ibu_results = drug_search_service.search_drugs("Ibu")
        for drug in ibu_results:
            print(f"  - Found: {drug['name']} (ID: {drug['drugbank_id']})")

        print("\n--- Getting drug by ID 'DB00945' ---")
        specific_drug = drug_search_service.get_drug_by_id('DB00945')
        if specific_drug:
            print(f"  - Found: {specific_drug['name']}")
        else:
            print("  - Drug not found.")

        print("\n--- Getting 3 random drugs ---")
        random_drugs = drug_search_service.get_random_drugs(3)
        for drug in random_drugs:
            print(f"  - Random Drug: {drug['name']} (ID: {drug['drugbank_id']})")
    else:
        print("\nCould not run examples because drug data failed to load.")
