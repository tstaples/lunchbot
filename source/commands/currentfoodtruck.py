from command import Command
import streetfoodapp as sfa

class CurrentFoodTruck(Command):
    def run(self, args):
        msg = sfa.getCurrentFoodTruckInfo(self.config.region)
        if not msg:
            msg = "There are currently no foodtrucks open"
        return msg