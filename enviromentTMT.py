import random
import math

class TMTTaskProvider:
    def __init__(self, task_type="A"):
        self.task_type = task_type
        # Full 25-item arrays
        if task_type == "A":
            self.targets = [str(i) for i in range(1, 26)]
        else:
            # 1, A, 2, B ... 13
            self.targets = ["1", "A", "2", "B", "3", "C", "4", "D", "5", "E", 
                            "6", "F", "7", "G", "8", "H", "9", "I", "10", "J", 
                            "11", "K", "12", "L", "13"]
            
        self.current_index = 0
        self.completed = False
        self.nodes = self._generate_spatial_layout()

    def _generate_spatial_layout(self):
        """Generates random X, Y coordinates (0-100) for 25 nodes, avoiding extreme overlaps."""
        nodes = {}
        for target in self.targets:
            placed = False
            while not placed:
                x, y = random.uniform(5, 95), random.uniform(5, 95)
                # Ensure minimum distance from other nodes
                if all(math.hypot(x - nx, y - ny) > 8 for nx, ny in nodes.values()):
                    nodes[target] = (x, y)
                    placed = True
        return nodes

    def get_current_target(self):
        if self.current_index < len(self.targets):
            return self.targets[self.current_index]
        return None

    def get_target_coords(self, target):
        return self.nodes.get(target, (50, 50))

    def submit_action(self, target):
        if self.completed: return False
        if target == self.targets[self.current_index]:
            self.current_index += 1
            if self.current_index >= len(self.targets):
                self.completed = True
            return True
        return False
        
    def get_uncompleted_targets(self):
        return self.targets[self.current_index:]