from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class CodeEnforcementEntry():
    
    def __init__(self, caseNum, address, status, openDate, closeDate, owner, link):
        self.caseNum = caseNum
        self.address = address
        self.status = status
        self.openDate = openDate
        self.closeDate = closeDate
        self.owner = owner
        self.link = link
        self.violations = []
    
    def __str__(self):
        return f"Case Num: {self.caseNum}\t{self.address}\n" + \
                f"Opened: {self.openDate}\tClosed: {self.closeDate}\n" + \
                f"Owner/Occupant: {self.owner}"
    
    def to_dict(self):
        return {
            'caseNumber': self.caseNum,
            'status': self.status,
            'openDate': self.openDate,
            'closeDate': self.closeDate,
            'owner': self.owner,
            'link': self.link,
            'violations': self.violations
        }
    
    def isRecent(self, noMonths):
        date = datetime.strptime(self.openDate, '%m/%d/%Y')
        current_date = datetime.now()
        
        delta_date = current_date - relativedelta(months=noMonths)
        if delta_date <= date <= current_date:
            return True
        else:
            return False