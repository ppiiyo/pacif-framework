class DriftDetector:
    def __init__(self, threshold=0.15, slack=0.005):
        self.threshold, self.slack = threshold, slack
        self.cus_pos = self.cus_neg = 0.0
        self.history, self.baseline = [], None
        
    def update(self, value: float) -> dict:
        self.history.append(value)
        if len(self.history) < 50:
            return {'drift': False, 'reason': 'warming_up'}
        if len(self.history) == 50:
            self.baseline = sum(self.history[-50:]) / 50.0
        dev = value - self.baseline
        self.cus_pos = max(0, self.cus_pos + dev - self.slack)
        self.cus_neg = max(0, self.cus_neg - dev - self.slack)
        if self.cus_pos > self.threshold or self.cus_neg > self.threshold:
            self.cus_pos = self.cus_neg = 0.0
            self.baseline = value
            return {'drift': True, 'value': value, 'baseline': self.baseline}
        return {'drift': False}
