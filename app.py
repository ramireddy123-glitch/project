import json
from flask import Flask, render_template, request

# Initialize Flask app
app = Flask(__name__)

# Substitution map defines what can be substituted for a required item
SUBSTITUTION_MAP = {
    "vegetable broth": ["broth"],
    "chicken broth": ["broth"],
    "coconut milk": ["cream", "milk"],
    "milk": ["cream"],
    "olive oil": ["butter"],
    "butter": ["olive oil"],
    "spaghetti": ["noodles"],
    "rice": ["noodles"],
    "noodles": ["spaghetti", "rice"]
}

def load_recipes():
    """Loads recipe data from recipes.json."""
    try:
        with open('recipes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: recipes.json not found.")
        return []
    except Exception as e:
        print(f"Error loading recipes.json: {e}")
        return []

def get_substitutes(item_name):
    """
    Finds available substitutes for a required missing item.
    """
    substitutes = []
    for sub, targets in SUBSTITUTION_MAP.items():
        if item_name in targets:
            substitutes.append(sub)
    return substitutes

def analyze_recipe(recipe, available_set):
    """Analyzes a single recipe against the user's available ingredients."""
    required_ingredients = {item['item'] for item in recipe['required_ingredients']}
    
    missing_ingredients = []
    substitutable_missing = []
    
    for required_item in required_ingredients:
        if required_item not in available_set:
            # Check for available substitutes
            found_substitutes = [
                sub for sub in get_substitutes(required_item) if sub in available_set
            ]
            
            if found_substitutes:
                substitutable_missing.append({
                    "item": required_item,
                    "substitutes": found_substitutes
                })
            else:
                missing_ingredients.append(required_item)
    
    # Calculate gaps
    total_gap = len(missing_ingredients)
    is_perfect = total_gap == 0 and len(substitutable_missing) == 0
    is_makeable_with_subs = total_gap == 0 and len(substitutable_missing) > 0
    
    return {
        "recipe": recipe,
        "is_perfect": is_perfect,
        "is_makeable_with_subs": is_makeable_with_subs,
        "missing_count": total_gap,
        "missing_items": missing_ingredients,
        "substitutions_required": substitutable_missing
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route to display the form and results."""
    all_recipes = load_recipes()
    results = []
    available_input = ""
    
    if request.method == 'POST':
        user_input = request.form.get('ingredients', '')
        available_list = [item.strip().lower() for item in user_input.split(',') if item.strip()]
        available_set = set(available_list)
        
        results = [analyze_recipe(recipe, available_set) for recipe in all_recipes]
        
        # Sort results: best matches first
        results.sort(key=lambda x: (not x['is_perfect'], not x['is_makeable_with_subs'], x['missing_count']))
        available_input = user_input
    
    return render_template('index.html', results=results, available_input=available_input)

if __name__ == '__main__':
    app.run(debug=True)