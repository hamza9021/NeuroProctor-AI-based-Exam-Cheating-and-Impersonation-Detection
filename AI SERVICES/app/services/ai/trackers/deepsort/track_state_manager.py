"""Track state manager for lifecycle events."""

from typing import Dict, Optional


class TrackStateManager:
    """Manages track state transitions for lifecycle events.
    
    Tracks previous states to emit events only on genuine transitions.
    """
    
    def __init__(self):
        """Initialize state manager."""
        self._previous_states: Dict[int, Dict] = {}
    
    def update_state(
        self,
        track_id: int,
        is_confirmed: bool,
        time_since_update: int,
        age: int,
        hits: int,
    ) -> Dict:
        """Update track state and detect transitions.
        
        Args:
            track_id: Track ID.
            is_confirmed: Whether track is confirmed.
            time_since_update: Time since last update.
            age: Track age.
            hits: Number of hits.
            
        Returns:
            Dict with transition flags: created, confirmed, lost, recovered, updated.
        """
        previous = self._previous_states.get(track_id)
        
        current = {
            "is_confirmed": is_confirmed,
            "time_since_update": time_since_update,
            "age": age,
            "hits": hits,
        }
        
        transitions = {
            "created": False,
            "confirmed": False,
            "lost": False,
            "recovered": False,
            "updated": False,
        }
        
        if previous is None:
            # New track
            transitions["created"] = True
        else:
            # Check for state transitions
            if not previous["is_confirmed"] and is_confirmed:
                transitions["confirmed"] = True
            elif previous["time_since_update"] == 0 and time_since_update > 0:
                transitions["lost"] = True
            elif previous["time_since_update"] > 0 and time_since_update == 0:
                transitions["recovered"] = True
            else:
                transitions["updated"] = True
        
        self._previous_states[track_id] = current
        return transitions
    
    def remove_track(self, track_id: int):
        """Remove track from state manager.
        
        Args:
            track_id: Track ID to remove.
        """
        self._previous_states.pop(track_id, None)
