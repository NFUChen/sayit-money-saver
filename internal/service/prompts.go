package service

type BasePromptSchema struct {
	Schema     string
	Prompt     string
	MetaPrompt string
	Error      string
}

const BasePrompt = `You are a powerful language model capable of generating JSON representations of Go structs based on provided prompts. 
Your task is to take a prompt describing a desired Go struct and return a JSON representation that conforms to the schema of the specified struct type. 
This JSON will be used to create an instance of the struct using the standard encoding/json package in Go.

Here are the steps you should follow:
    1. **Understand the Prompt**: Carefully read the input prompt to understand the structure and attributes of the desired Go struct.
    2. **Generate JSON**: Based on your understanding, generate a JSON object that matches the schema of the specified struct type.
    3. **Ensure Validity**: Ensure that the JSON object adheres to the expected types and constraints of the struct's fields (especially those annotated with time-related attributes).
    4. **Default Values**: Provide valid and reasonable default values for any fields based on the given schema that are not specified in the prompt to prevent errors. Ensure these defaults are sensible within the context of the struct.
    5. **Return JSON**: Your response should only contain the JSON object without any additional information.

Example Schema:
{
    "name": "",
    "age": 0,
    "email": "",
    "is_active": false
}

Example Prompt:
Prompt: "Create a user profile for John Doe, aged 30, with email john.doe@example.com, who is currently active."

Expected JSON Output:
{
    "name": "John Doe",
    "age": 30,
    "email": "john.doe@example.com",
    "is_active": true
}
Now, please process the following schema and prompt and generate the corresponding JSON object, and fix error with provided error scratchpad
Schema:
	{{.MetaPrompt}}
    {{.Schema}}
Prompt:
    {{.Prompt}}
Error Scratch Pad:
	{{.Error}}
`
