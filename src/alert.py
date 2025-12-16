import time

class AlertSystem:
    def __init__(self):
        self.last_alert_time = 0
        self.alert_cooldown = 2.0 # Seconds between alerts

    def trigger(self, faces_count):
        """
        Triggers an alert if faces are detected.
        """
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_cooldown:
            print(f"\n[ALERT] Security Breach! {faces_count} face(s) detected!")
            # In a real system, this could send an email, SMS, or play a sound.
            # For now, we just print to console to avoid annoying system beeps during dev.
            self.last_alert_time = current_time
            return True
        return False
