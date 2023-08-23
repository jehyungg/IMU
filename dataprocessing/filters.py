class Kalman:
    def __init__(self):
        self.Q_angle = 0.01
        self.Q_bias = 0.03
        self.R_measure = 0.0003

        self.angle = 0.0
        self.bias = 0.0

        self.P = [[0.0, 0.0], [0.0, 0.0]]

    def getAngle(self, newAngle, newRate, dt):
        rate = newRate - self.bias
        self.angle += dt * rate

        self.P[0][0] += dt * (dt * self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        S = self.P[0][0] + self.R_measure
        K = [self.P[0][0] / S, self.P[1][0] / S]

        y = newAngle - self.angle
        self.angle += K[0] * y
        self.bias += K[1] * y

        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]

        self.P[0][0] -= K[0] * P00_temp
        self.P[0][1] -= K[0] * P01_temp
        self.P[1][0] -= K[1] * P00_temp
        self.P[1][1] -= K[1] * P01_temp

        return self.angle

    def setAngle(self, angle):
        self.angle = angle

    def getRate(self):
        return self.rate

    def setQangle(self, Q_angle):
        self.Q_angle = Q_angle

    def setQbias(self, Q_bias):
        self.Q_bias = Q_bias

    def setRmeasure(self, R_measure):
        self.R_measure = R_measure

    def getQangle(self):
        return self.Q_angle

    def getQbias(self):
        return self.Q_bias

    def getRmeasure(self):
        return self.R_measure
