import openai
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
from dotenv import load_dotenv
from services.db import get_all_employees # Ensure this import path is correct

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_graph(prompt):
    employees = get_all_employees()
    df = pd.DataFrame(employees)

    # Handle case where employee data might be empty
    if df.empty:
        print("Warning: No employee data available to generate chart.")
        return None

    full_prompt = f"""
You are a Python data analyst.

Here is a list of employees as a JSON array (load this into a pandas DataFrame using pd.DataFrame(data)):
{df.to_dict(orient='records')}

Generate a COMPLETE Python script (no markdown, no explanation) that:

- Imports pandas as pd and matplotlib.pyplot as plt.
- Creates a pandas DataFrame from the provided JSON data.
- Creates a plot based on this instruction: \"{prompt}\"
- **Use `plt.style.use('ggplot')` for a clean look.** This style is widely available.
- Sets appropriate x-axis, y-axis labels and a descriptive title for the plot.
- Ensures the plot has a tight layout (`plt.tight_layout()`).
- Saves the plot to a BytesIO object called `buf` as a PNG image, without showing it.
- **Crucially, after saving, close the plot to free up memory using `plt.clf()` or `plt.close('all')`.**
- Encodes it to base64 as:
  base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

REQUIREMENTS:
- DO NOT use markdown.
- DO NOT wrap code in triple backticks.
- DO NOT explain anything.
- Just return plain Python code.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4", # Or "gpt-3.5-turbo" if you prefer
            messages=[{"role": "user", "content": full_prompt}]
        )

        ai_code = response.choices[0].message.content
        print("----- GPT Generated Code -----\n", ai_code, "\n-------------------------------")

        # 🧼 Clean up GPT response - crucial for exec
        cleaned_code = ai_code.strip().replace("```python", "").replace("```", "")

        global_env = {
            "pd": pd,
            "plt": plt,
            "io": io,
            "base64": base64,
            "buf": io.BytesIO(),
            # Pass the raw data so the generated script can create the DataFrame
            "data": df.to_dict(orient='records')
        }

        # Add initial setup code to create a figure and DataFrame, as GPT sometimes omits it
        initial_exec_code = """
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
# Ensure df is created from 'data' which is passed via global_env
df = pd.DataFrame(data)
# Create a figure before plotting (important for some matplotlib versions/backends)
plt.figure(figsize=(10, 6)) # You can adjust figsize as needed
"""
        full_code_to_execute = initial_exec_code + cleaned_code

        try:
            exec(full_code_to_execute, global_env)

            # Explicitly close all matplotlib figures to prevent memory leaks
            # This is essential after plot generation within exec
            plt.close('all') 

            # Check if base64_image was created by the executed code
            if "base64_image" in global_env:
                return global_env.get("base64_image")
            else:
                print("Error: Generated code did not produce 'base64_image'.")
                return None

        except Exception as e:
            print(f"⚠️ Error while running GPT generated code: {e}")
            # print("Failing code was:\n", full_code_to_execute) # Uncomment for deep debugging
            plt.close('all') # Attempt to close even on error
            return None

    except openai.APIError as e:
        print(f"❌ OpenAI API Error: Status Code: {e.status_code}, Response: {e.response}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during AI graph generation setup: {e}")
        return None