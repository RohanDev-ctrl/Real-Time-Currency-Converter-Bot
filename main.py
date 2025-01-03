import re
import json
import time
import requests
import os
from datetime import datetime

class AdvancedCurrencyConverter:
    def __init__(self):
        # Configuration
        self.api_url = "https://open.er-api.com/v6/latest/USD" # Free public API (no key needed for basic use)
        self.cache_file = "rates_cache.json"
        self.cache_duration = 3600  # 1 hour in seconds
        
        # Symbol mapping for natural language
        self.currency_symbols = {
            '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₹': 'INR',
            '₿': 'BTC', '₽': 'RUB', '₩': 'KRW', 'fr': 'CHF'
        }
        
        # Common text aliases
        self.aliases = {
            'buck': 'USD', 'bucks': 'USD', 'dollar': 'USD', 'dollars': 'USD',
            'euro': 'EUR', 'euros': 'EUR',
            'pound': 'GBP', 'pounds': 'GBP', 'quid': 'GBP',
            'yen': 'JPY',
            'rupee': 'INR', 'rupees': 'INR',
            'bitcoin': 'BTC', 'bitcoins': 'BTC'
        }

        self.rates = self.load_rates()

    def load_rates(self):
        """Loads rates from cache or fetches new ones if expired."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    # Check if cache is still valid
                    if time.time() - data['timestamp'] < self.cache_duration:
                        return data['rates']
            except (json.JSONDecodeError, KeyError):
                pass
        
        print(">> [System] Fetching live rates from API...")
        return self.fetch_rates()

    def fetch_rates(self):
        """Fetches fresh rates from the open API."""
        try:
            response = requests.get(self.api_url)
            data = response.json()
            if data['result'] == 'success':
                # Save to cache with timestamp
                cache_data = {'timestamp': time.time(), 'rates': data['rates']}
                with open(self.cache_file, 'w') as f:
                    json.dump(cache_data, f)
                return data['rates']
        except Exception as e:
            print(f">> [Error] Could not fetch rates: {e}")
            return None

    def normalize_currency(self, text):
        """Converts symbols ($) or names (dollars) to codes (USD)."""
        text = text.strip().lower()
        
        # Check explicit symbols first
        for symbol, code in self.currency_symbols.items():
            if symbol in text:
                return code
        
        # Check aliases
        if text in self.aliases:
            return self.aliases[text]
            
        # Return uppercase code (assuming it's a standard code like 'AUD')
        return text.upper()

    def parse_input(self, user_input):
        """
        Uses Regex to find patterns like:
        - "100 USD to EUR"
        - "convert $50 to yen"
        - "50000 satoshis in usd"
        """
        # Pattern 1: "100 USD to EUR" or "100 USD in EUR"
        # Matches number, optional space, source string, separator, target string
        pattern = r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*([a-zA-Z$€£¥₿]+)\s*(?:to|in|->)\s*([a-zA-Z$€£¥₿]+)"
        match = re.search(pattern, user_input, re.IGNORECASE)
        
        if match:
            amount = float(match.group(1).replace(',', ''))
            from_curr = self.normalize_currency(match.group(2))
            to_curr = self.normalize_currency(match.group(3))
            return amount, from_curr, to_curr

        # Pattern 2: "$100 to EUR" (Symbol attached to number)
        pattern_symbol = r"([$€£¥₿])(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:to|in|->)\s*([a-zA-Z$€£¥₿]+)"
        match = re.search(pattern_symbol, user_input, re.IGNORECASE)
        
        if match:
            from_curr = self.normalize_currency(match.group(1)) # The symbol is group 1
            amount = float(match.group(2).replace(',', ''))
            to_curr = self.normalize_currency(match.group(3))
            return amount, from_curr, to_curr

        return None, None, None

    def convert(self, amount, from_curr, to_curr):
        if not self.rates:
            return "Error: Exchange rate data unavailable."
        
        if from_curr not in self.rates or to_curr not in self.rates:
            return f"Error: Currency '{from_curr}' or '{to_curr}' not supported."

        # Convert to USD first (Base), then to Target
        # Formula: (Amount / Rate_From) * Rate_To
        usd_value = amount / self.rates[from_curr]
        final_value = usd_value * self.rates[to_curr]
        
        return f"{amount:,.2f} {from_curr} = {final_value:,.2f} {to_curr}"

    def run(self):
            print("--- Advanced Text Currency Converter ---")
            print("Examples: '100 USD to EUR', 'Convert $50 to Yen', '500 GBP in CAD'")
            print("Type 'quit' to exit.\n")
            
            while True:
                try:
                    user_input = input(">> ").strip()
                except (EOFError, KeyboardInterrupt):
                    # Handles Ctrl+D, Ctrl+C, or non-interactive environments
                    print("\nExiting...")
                    break

                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                # Skip empty inputs (e.g., just pressing Enter)
                if not user_input:
                    continue
                    
                amount, from_curr, to_curr = self.parse_input(user_input)
                
                if amount is not None:
                    result = self.convert(amount, from_curr, to_curr)
                    print(result)
                else:
                    print(">> Could not understand input. Try format: '100 USD to EUR'")

if __name__ == "__main__":
    converter = AdvancedCurrencyConverter()
    converter.run()

print("Log: User session started.")