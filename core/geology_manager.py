import numpy as np

class GeologyManager:
    """
    COMPONENT: THE BODY
    
    WHY: 
    - Represents the physical reality of the ore body.
    - Manages the 'Playlist' of blocks (Year 1 Block, Year 2 Block, etc.).
    - Ensures we don't mine more gold than exists (Physical Constraint).
    """
    def __init__(self, config):
        self.total_reserves = config.TOTAL_RESERVE_TONNES
        self.current_reserve = config.TOTAL_RESERVE_TONNES
        self.geo_index = 0 
        
        # Load the Playlist (Geological Schedule)
        self.grade_schedule = getattr(config, 'GRADE_SCHEDULE', [config.AVERAGE_GRADE_GPT])
        if not isinstance(self.grade_schedule, list): self.grade_schedule = [self.grade_schedule]
            
        self.strip_schedule = getattr(config, 'STRIP_SCHEDULE', [config.STRIP_RATIO])
        if not isinstance(self.strip_schedule, list): self.strip_schedule = [self.strip_schedule]
        
        # Ramp Up Logic (Physical inefficiency in early years)
        self.ramp_factors = {
            0: getattr(config, 'RAMP_UP_YR1', 1.0),
            1: getattr(config, 'RAMP_UP_YR2', 1.0)
        }

    def get_next_block(self, force_stockpile=False):
        """
        WHY: Returns the properties of the rock we are about to mine.
        
        LOGIC:
        - If 'force_stockpile' is True, we overwrite the Strip Ratio to 0.0.
        - This is physically correct: Stockpiles are already on surface. No waste stripping needed.
        """
        if self.current_reserve <= 0:
            return None 
            
        # Get base values from the schedule
        safe_idx = min(self.geo_index, len(self.grade_schedule) - 1)
        safe_strip_idx = min(self.geo_index, len(self.strip_schedule) - 1)
        
        grade = self.grade_schedule[safe_idx]
        strip = self.strip_schedule[safe_strip_idx]
        
        # --- CRITICAL PHYSICS CHANGE ---
        if force_stockpile:
            strip = 0.0  # Stockpiles have NO strip ratio.
            
        return {
            "grade": grade,
            "strip_ratio": strip,
            "ramp_factor": self.ramp_factors.get(self.geo_index, 1.0)
        }

    def deplete(self, tonnes_mined):
        """
        WHY: Actually removes the rock from the ground.
        HOW: Decrements reserves and advances the 'Playlist' index.
        """
        self.current_reserve -= tonnes_mined
        self.geo_index += 1
        return self.current_reserve