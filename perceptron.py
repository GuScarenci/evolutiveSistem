import numpy as np

class Perceptron:
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

    def load_perceptron(self, filename):
        """
        Load the perceptron's weights and biases from a file.

        Args:
            filename (str): Name of the file to load the perceptron.
        """
        data = np.load(filename)
        self.input_to_hidden = data["input_to_hidden"]
        self.hidden_to_output = data["hidden_to_output"]
        self.hidden_bias = data["hidden_bias"]
        self.output_bias = data["output_bias"]

    def save_perceptron(self, filename):
        """
        Save the perceptron's weights and biases to a file.

        Args:
            filename (str): Name of the file to save the perceptron.
        """
        np.savez(filename, input_to_hidden=self.input_to_hidden, 
                           hidden_to_output=self.hidden_to_output, 
                           hidden_bias=self.hidden_bias, 
                           output_bias=self.output_bias)

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

    @staticmethod
    def crossover(parent1, parent2):
        """
        Crossover two perceptrons' genes to get another perceptron.

        Args:
            parent1 (Perceptron): First parent.
            parent2 (Perceptron): Second parent.
        
        Returns:
            Perceptron: The crossover between the two parents.
        """
        child = Perceptron(input_size=parent1.input_to_hidden.shape[0], 
                           hidden_size=parent1.input_to_hidden.shape[1], 
                           output_size=parent1.hidden_to_output.shape[1])
        child.input_to_hidden = (parent1.input_to_hidden + parent2.input_to_hidden) / 2
        child.hidden_to_output = (parent1.hidden_to_output + parent2.hidden_to_output) / 2
        child.hidden_bias = (parent1.hidden_bias + parent2.hidden_bias) / 2
        child.output_bias = (parent1.output_bias + parent2.output_bias) / 2
        return child

    def mutate(self, mutation_rate=0.1, mutation_modulus=0.5):
        """
        Mutate the perceptron's weights and biases.

        Args:
            mutation_rate (float): Probability of mutating each weight/bias.
        """
        for i in range(self.input_to_hidden.shape[0]):
            for j in range(self.input_to_hidden.shape[1]):
                if np.random.uniform(0, 1) < mutation_rate:
                    self.input_to_hidden[i, j] += np.random.uniform(-mutation_modulus, mutation_modulus)

        for i in range(self.hidden_to_output.shape[0]):
            for j in range(self.hidden_to_output.shape[1]):
                if np.random.uniform(0, 1) < mutation_rate:
                    self.hidden_to_output[i, j] += np.random.uniform(-mutation_modulus, mutation_modulus)

        for i in range(self.hidden_bias.shape[0]):
            if np.random.uniform(0, 1) < mutation_rate:
                self.hidden_bias[i] += np.random.uniform(-mutation_modulus, mutation_modulus)

        for i in range(self.output_bias.shape[0]):
            if np.random.uniform(0, 1) < mutation_rate:
                self.output_bias[i] += np.random.uniform(-mutation_modulus, mutation_modulus)

    def copy(self):
        """
        Create a deep copy of the perceptron instance.

        Returns:
            Perceptron: A new perceptron object with the same attributes.
        """
        copied = Perceptron(input_size=self.input_to_hidden.shape[0], 
                            hidden_size=self.input_to_hidden.shape[1], 
                            output_size=self.hidden_to_output.shape[1])
        copied.input_to_hidden = np.copy(self.input_to_hidden)
        copied.hidden_to_output = np.copy(self.hidden_to_output)
        copied.hidden_bias = np.copy(self.hidden_bias)
        copied.output_bias = np.copy(self.output_bias)
        return copied
