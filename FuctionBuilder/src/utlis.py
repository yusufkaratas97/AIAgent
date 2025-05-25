from google import genai
from google.genai import types

def generate_response_gemini(content):
    client = genai.Client(
        api_key="", # add your key here
    )

    model = "gemini-2.5-flash-preview-05-20"
    contents = content
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="You are a Python expert helping to develop a function."),
        ],
    )
    text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        text += chunk.text
        #print(chunk.text, end="")
    return text
    

def extract_code_block(response: str) -> str:
   """Extract code block from response"""

   if not '```' in response:
      return response
      
   code_block = response.split('```')[1].strip()
   # Check for "python" at the start and remove

   if code_block.startswith("python"):
      code_block = code_block[6:]

   return code_block

def develop_custom_function():
   # Get user input for function description
   print("\nWhat kind of function would you like to create?")
   print("Example: 'A function that calculates the factorial of a number'")
   print("Your description: ", end='')
   function_description = input().strip()

   # Initialize conversation with system prompt
   messages = []
   
    # First prompt - Basic function
   messages.append(types.Content(role="user", parts=[types.Part.from_text(text=f"Write a Python function that {function_description}. Output the function in a ```python code block```.")]))
   initial_function = generate_response_gemini(messages)

   # Parse the response to get the function code
   initial_function = extract_code_block(initial_function)

   print("\n=== Initial Function ===")
   print(initial_function)

   # Add assistant's response to conversation
   # Notice that I am purposely causing it to forget its commentary and just see the code so that
   # it appears that is always outputting just code.
   messages.append(types.Content(role="model", parts=[types.Part.from_text(text="\`\`\`python\n\n"+initial_function+"\n\n\`\`\`")]))
   # Second prompt - Add documentation
   messages.append(types.Content(role="user", parts=[types.Part.from_text(text="Add comprehensive documentation to this function, including description, parameters, "
                 "return value, examples, and edge cases. Output the function in a ```python code block```.")]))

   documented_function = generate_response_gemini(messages)
   documented_function = extract_code_block(documented_function)
   print("\n=== Documented Function ===")
   print(documented_function)

   # Add documentation response to conversation
   messages.append(types.Content(role="model", parts=[types.Part.from_text(text="\`\`\`python\n\n"+documented_function+"\n\n\`\`\`")]))


   # Third prompt - Add test cases
   messages.append(types.Content(role="user", parts=[types.Part.from_text(text="Add unittest test cases for this function, including tests for basic functionality, "
                 "edge cases, error cases, and various input scenarios. Output the code in a \`\`\`python code block\`\`\`.")]))

   test_cases = generate_response_gemini(messages)
   # We will likely run into random problems here depending on if it outputs JUST the test cases or the
   # test cases AND the code. This is the type of issue we will learn to work through with agents in the course.
   test_cases = extract_code_block(test_cases)
   print("\n=== Test Cases ===")
   print(test_cases)

   # Generate filename from function description
   filename = function_description.lower()
   filename = ''.join(c for c in filename if c.isalnum() or c.isspace())
   filename = filename.replace(' ', '_')[:30] + '.py'

   # Save final version
   with open("output/"+filename, 'w') as f:
      f.write(test_cases)

   return documented_function, test_cases, filename