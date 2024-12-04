import numpy as np

class ThreeLayerPerceptron:
    def __init__(self, input_size, hidden1_size, hidden2_size, output_size):
        """
        Initialize the perceptron with random weights and biases.
        """
        # Hidden layer 1 weights and biases
        self.W1 = np.random.uniform(-1, 1, (hidden1_size, input_size))
        self.b1 = np.random.uniform(-1, 1, (hidden1_size,))
        
        # Hidden layer 2 weights and biases
        self.W2 = np.random.uniform(-1, 1, (hidden2_size, hidden1_size))
        self.b2 = np.random.uniform(-1, 1, (hidden2_size,))
        
        # Output layer weights and biases
        self.W3 = np.random.uniform(-1, 1, (output_size, hidden2_size))
        self.b3 = np.random.uniform(-1, 1, (output_size,))
    
    def set_weights(self, W1, b1, W2, b2, W3, b3):
        """
        Manually set the weights and biases of the network.
        """
        self.W1 = np.array(W1)
        self.b1 = np.array(b1)
        self.W2 = np.array(W2)
        self.b2 = np.array(b2)
        self.W3 = np.array(W3)
        self.b3 = np.array(b3)
    
    def relu(self, x):
        """
        ReLU activation function.
        """
        return np.maximum(0, x)
    
    def tanh(self, x):
        """
        Tanh activation function.
        """
        return np.tanh(x)
    
    def forward(self, inputs):
        """
        Perform a forward pass through the network.
        """
        # Hidden layer 1
        z1 = np.dot(self.W1, inputs) + self.b1
        a1 = self.relu(z1)
        
        # Hidden layer 2
        z2 = np.dot(self.W2, a1) + self.b2
        a2 = self.relu(z2)
        
        # Output layer
        z3 = np.dot(self.W3, a2) + self.b3
        outputs = self.tanh(z3)  # Output in range [-1, 1]
        
        return outputs

if __name__ == "__main__":
    # Example usage
    # Initialize perceptron
    input_size = 8   # Number of radial distances
    hidden1_size = 16
    hidden2_size = 16
    output_size = 2  # [acceleration, steering]
    perceptron = ThreeLayerPerceptron(input_size, hidden1_size, hidden2_size, output_size)
    
    # Example inputs (radial distances)
    inputs = np.random.uniform(0, 1, input_size)  # Normalized inputs
    
    # Perform forward pass
    outputs = perceptron.forward(inputs)
    print(f"Inputs: {inputs}")
    print(f"Outputs: {outputs}")
    
    # Example: Set custom weights (for evolutionary optimization)
    perceptron.set_weights(
        W1=np.random.uniform(-1, 1, (hidden1_size, input_size)),
        b1=np.random.uniform(-1, 1, (hidden1_size,)),
        W2=np.random.uniform(-1, 1, (hidden2_size, hidden1_size)),
        b2=np.random.uniform(-1, 1, (hidden2_size,)),
        W3=np.random.uniform(-1, 1, (output_size, hidden2_size)),
        b3=np.random.uniform(-1, 1, (output_size,))
    )
    
    # Perform another forward pass with new weights
    outputs = perceptron.forward(inputs)
    print(f"New Outputs: {outputs}")
