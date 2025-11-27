import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# Load intents file
with open('intents for app.json', 'r') as file:
    intents = json.load(file)

# Load the trained model
FILE = "data.pth"
data = torch.load(FILE)


# Extract model details
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]
model_state = data["model_state"]

# Recreate the model and load the state
model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(model_state)
model.eval()

# Set device compatibility
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)

# Bot name
bot_name = "Spidey"

# Define the get_response function
def get_response(user_input):
    """
    Process the user input and generate a response from the chatbot.
    """
    # Tokenize and preprocess input
    tokenized_sentence = tokenize(user_input)
    bow = bag_of_words(tokenized_sentence, all_words)
    bow = torch.from_numpy(bow).unsqueeze(0).to(device).float()

    # Get model prediction
    output = model(bow)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    # Confidence check
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:  # Confidence threshold
        for intent in intents['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    else:
        return "I'm not sure I understand. Can you try rephrasing?"

# Main chat function (for command-line use, if needed)
def chat():
    """
    Command-line chat interface.
    """
    print(f"{bot_name}: Hello! I’m here to help. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            print(f"{bot_name}: Goodbye! Have a great day.")
            break

        response = get_response(user_input)
        print(f"{bot_name}: {response}")

# Run the chat function if this script is executed directly
if __name__ == "__main__":
    chat()
