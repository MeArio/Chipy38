class RAM:
    def __init__(self, mem_size):
        self.MEM_SIZE = mem_size  # Memory size
        self.memory = [0] * mem_size  # Memory array
