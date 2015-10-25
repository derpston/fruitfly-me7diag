#3rd party
import fruitfly
import me7

class me7diag(fruitfly.Module):
    """A Fruitfly module for interacting with a Bosch ME7 ECU."""

    def init(self):
        self.ecu = me7.ECU()

    def open(self):
        variables = []
        for cvar in self.config['variables']:
            var = me7.Variable(cvar['name'], cvar['addr'], **cvar['options'])
            variables.append(var)
            self.logger.info("Loaded variable %s" % repr(var))

        self.ecu.open()
        self.ecu.startdiagsession(19200)
        # TODO This belongs in the me7.ECU class.
        response = self.ecu.writemembyaddr(0x00e228, [0x00, 0x3a, 0xe1, 0x00])
        self.ecu.prepareLogVariables(*variables)

        self.logger.info("connected!")
        return True
 
    @fruitfly.repeat(1)
    def _poll(self):
        if self.ecu.connected:
            try:
                # Fetch all the variables, and emit them as fruitfly events.
                for name, var in self.ecu.getLogValues().items():
                    self.send_event("me7diag.%s" % name, var)
            except:
                self.ecu.close()
                raise
        else:
            self.open()

