import math
import random
from datetime import datetime, timedelta

class CognitiveAgent:
    def __init__(
        self,
        search_speed=300,
        shift_speed=500,
        memory_speed=150,
        visual_capacity=3,
        visual_skip=0.1,
        click_overhead=120,
        mouse_speed=0.4,
    ):
        self.search_speed = search_speed
        self.shift_speed = shift_speed
        self.memory_speed = memory_speed
        self.visual_capacity = visual_capacity
        self.visual_skip = visual_skip
        self.click_overhead = click_overhead
        self.mouse_speed = mouse_speed

        self.pen_pos = None
        self.eye_pos = (50, 50)
        self.events = []
        self.current_time_ms = 0.0
        self.start_time = datetime.now()

    def run_simulation(self, env):
        self.pen_pos = env.get_target_coords(env.targets[0])
        self.eye_pos = self.pen_pos
        self.events = []
        self.current_time_ms = 0.0
        self.start_time = datetime.now()

        self._record_event(
            "task_started",
            env,
            {
                "targets": env.targets,
                "layout": [list(env.get_target_coords(target)) for target in env.targets],
            },
        )

        while not env.completed:
            target = env.get_current_target()
            target_coords = env.get_target_coords(target)

            yield self._frame("Goal Retrieval", env, self.memory_speed)
            if env.task_type == "B":
                yield self._frame("Maintain Alternation Rule", env, self.memory_speed)
                yield self._frame("Inhibit Previous Set", env, self.shift_speed)
                yield self._frame("Switch Cognitive Set", env, self.shift_speed)

            found = False
            while not found:
                pool = env.get_uncompleted_targets()
                sample_size = min(self.visual_capacity, len(pool))
                fixation_targets = random.sample(pool, sample_size)

                fx = sum(env.get_target_coords(t)[0] for t in fixation_targets) / sample_size
                fy = sum(env.get_target_coords(t)[1] for t in fixation_targets) / sample_size
                self.eye_pos = (fx, fy)

                self._record_event("mouse_move", env, {"x": fx, "y": fy})
                yield self._frame("Visual Search (Scanning)", env, self.search_speed)

                if target in fixation_targets:
                    if random.random() < self.visual_skip:
                        wrong_choices = [t for t in fixation_targets if t != target]
                        if wrong_choices:
                            wrong_target = random.choice(wrong_choices)
                            wrong_coords = env.get_target_coords(wrong_target)
                            self.eye_pos = wrong_coords
                            self._record_event(
                                "incorrect_click",
                                env,
                                {
                                    "x": wrong_coords[0],
                                    "y": wrong_coords[1],
                                    "target": wrong_target,
                                    "expected_target": target,
                                },
                            )
                        yield self._frame("Visual Skip", env, self.search_speed)
                        continue

                    found = True
                    self.eye_pos = target_coords
                    yield self._frame("Target Identification", env, self.search_speed // 2)

            self._record_event("planning_start", env, {})
            yield self._frame("Cognitive Planning", env, self.memory_speed)

            movement_distance = self._distance(self.pen_pos, target_coords)
            movement_time = max(20.0, movement_distance / self.mouse_speed)
            steps = max(3, int(round(movement_distance / 12.0)))
            for i in range(1, steps + 1):
                interp_x = self.pen_pos[0] + (target_coords[0] - self.pen_pos[0]) * (i / steps)
                interp_y = self.pen_pos[1] + (target_coords[1] - self.pen_pos[1]) * (i / steps)
                self.pen_pos = (interp_x, interp_y)
                self._record_event("mouse_move", env, {"x": interp_x, "y": interp_y})
                yield self._frame("Mouse Movement", env, movement_time / steps)

            self._record_event(
                "correct_click",
                env,
                {
                    "x": target_coords[0],
                    "y": target_coords[1],
                    "target": target,
                    "expected_target": target,
                },
            )
            yield self._frame("Correct Click", env, self.click_overhead)
            env.submit_action(target)

        self._record_event("task_completed", env, {})

    def _distance(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _frame(self, step_name, env, time_cost):
        state = {
            "step": step_name,
            "pen_pos": self.pen_pos,
            "eye_pos": self.eye_pos,
            "time_cost": time_cost,
            "current_target": env.get_current_target(),
            "completed_index": env.current_index,
        }
        return state

    def _record_event(self, event_type, env, payload):
        event_time_cost = payload.get("time_cost", 0)
        if isinstance(event_time_cost, (int, float)):
            self.current_time_ms += event_time_cost

        event = {
            "timestamp": (self.start_time + timedelta(milliseconds=self.current_time_ms)).isoformat(timespec="milliseconds"),
            "event_type": event_type,
            "task_type": env.task_type,
            "current_target": env.get_current_target(),
            "completed_count": env.current_index,
            "completed": env.completed,
            **payload,
        }
        self.events.append(event)
