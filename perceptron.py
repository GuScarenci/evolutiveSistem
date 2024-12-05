import numpy as np

# Neural Network Class
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        """
        Initialize a perceptron object.

        Args:
            input_size (int): Number of inputs (e.g., ray distances).
            hidden_size (int): Number of nodes in the hidden (middle) layer.
            output_size (int): Number of outputs (e.g., turn, accelerate).
        """
        self.input_to_hidden = np.random.uniform(-1, 1, (input_size, hidden_size))
        self.hidden_to_output = np.random.uniform(-1, 1, (hidden_size, output_size))
        self.hidden_bias = np.zeros(hidden_size)
        self.output_bias = np.zeros(output_size)

    def forward(self, inputs):
        """
        Perform a forward pass through the perceptron.

        Args:
            inputs (np.ndarray): Input vector (e.g., ray distances).

        Returns:
            np.ndarray: Output vector (e.g., turn, accelerate).
        """
        hidden_layer = np.tanh(np.dot(inputs, self.input_to_hidden) + self.hidden_bias)
        output_layer = np.tanh(np.dot(hidden_layer, self.hidden_to_output) + self.output_bias)
        return output_layer
    
    def crossover(parent1, parent2):
        """
        Crossover two perceptrons' genes to get another perceptron.

        Args:
            parent1 (NeuralNetwork): first parent.
            parent2 (NeuralNetwork): second parent.
        
        Returns:
            NeuralNetwork: the crossover between the two parents.
        """
        child = NeuralNetwork(input_size=4, hidden_size=6, output_size=2)
        child.input_to_hidden = (parent1.input_to_hidden + parent2.input_to_hidden) / 2
        child.hidden_to_output = (parent1.hidden_to_output + parent2.hidden_to_output) / 2
        return child
    
    def mutate(self, mutation_rate=0.1):
        """
        Mutate the perceptron's weights and biases.

        Args:
            mutation_rate (float): Probability of mutating each weight/bias.
        """
        for i in range(self.weights.shape[0]):
            for j in range(self.weights.shape[1]):
                if random.random() < mutation_rate:
                    self.weights[i, j] += np.random.uniform(-0.5, 0.5)
        for i in range(self.biases.shape[0]):
            if random.random() < mutation_rate:
                self.biases[i] += np.random.uniform(-0.5, 0.5)
