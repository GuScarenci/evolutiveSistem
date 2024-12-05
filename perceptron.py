import numpy as np

# Neural Network Class
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize weights
        self.input_to_hidden = np.random.uniform(-1, 1, (input_size, hidden_size))
        self.hidden_to_output = np.random.uniform(-1, 1, (hidden_size, output_size))
        self.hidden_bias = np.zeros(hidden_size)
        self.output_bias = np.zeros(output_size)

    def forward(self, inputs):
        # Forward pass
        hidden_layer = np.tanh(np.dot(inputs, self.input_to_hidden) + self.hidden_bias)
        output_layer = np.tanh(np.dot(hidden_layer, self.hidden_to_output) + self.output_bias)
        return output_layer
