import random
import math

class CognitiveAgent:
    def __init__(self, search_speed, shift_speed, motor_speed, memory_speed, planning_speed, visual_capacity):
        self.search_speed = search_speed
        self.shift_speed = shift_speed
        self.motor_speed = motor_speed
        self.memory_speed = memory_speed
        self.planning_speed = planning_speed
        self.visual_capacity = visual_capacity # Number of items agent can process per fixation
        
        self.pen_pos = None
        self.eye_pos = (50, 50)
        self.log = []

    def run_simulation(self, env):
        self.pen_pos = env.get_target_coords(env.targets[0])
        self.eye_pos = self.pen_pos
        
        while not env.completed:
            target = env.get_current_target()
            target_coords = env.get_target_coords(target)
            
            # 1. Executive / Memory Steps
            yield self._frame("Goal Retrieval", env, time=self.memory_speed)
            if env.task_type == "B":
                yield self._frame("Maintain Alternation Rule", env, time=self.memory_speed)
                yield self._frame("Inhibit Previous Set", env, time=self.shift_speed)
                yield self._frame("Switch Cognitive Set", env, time=self.shift_speed)

            # 2. Visual Search Phase (Loops until target is found)
            found = False
            while not found:
                # Agent samples 'visual_capacity' number of items from the board
                pool = env.get_uncompleted_targets()
                sample_size = min(self.visual_capacity, len(pool))
                fixation_targets = random.sample(pool, sample_size)
                
                # Move eye to the center of the fixated items
                fx = sum(env.get_target_coords(t)[0] for t in fixation_targets) / sample_size
                fy = sum(env.get_target_coords(t)[1] for t in fixation_targets) / sample_size
                self.eye_pos = (fx, fy)
                
                yield self._frame("Visual Search (Scanning)", env, time=self.search_speed)
                
                if target in fixation_targets:
                    found = True
                    self.eye_pos = target_coords # Snap eye to target
                    yield self._frame("Target Identification", env, time=self.search_speed // 2)

            # 3. Visuomotor Planning
            yield self._frame("Visuomotor Planning", env, time=self.planning_speed)

            # 4. Motor Execution (Interpolate pen movement)
            start_x, start_y = self.pen_pos
            end_x, end_y = target_coords
            steps = 5 # Number of animation frames for drawing
            for i in range(1, steps + 1):
                interp_x = start_x + (end_x - start_x) * (i / steps)
                interp_y = start_y + (end_y - start_y) * (i / steps)
                self.pen_pos = (interp_x, interp_y)
                yield self._frame("Motor Execution", env, time=self.motor_speed // steps)

            # 5. Monitoring & Memory
            yield self._frame("Performance Monitoring", env, time=self.memory_speed // 2)
            env.submit_action(target)
            yield self._frame("Update Working Memory", env, time=self.memory_speed)

    def _frame(self, step_name, env, time):
        """Helper to package the current spatial state for the UI renderer."""
        state = {
            "step": step_name,
            "pen_pos": self.pen_pos,
            "eye_pos": self.eye_pos,
            "time_cost": time,
            "current_target": env.get_current_target(),
            "completed_index": env.current_index
        }
        self.log.append(state)
        return state