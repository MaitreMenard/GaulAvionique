from numpy import radians, cos, sin


class Quaternion:

    def __init__(self, w=0, x=0, y=0, z=0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def set(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "w({}), x({}), y({}), z({})".format(self.w, self.x, self.y, self.z)

    def __eq__(self, other):
        if other is None or not isinstance(other, Quaternion):
            return False

        return self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        if other is None or not isinstance(other, Quaternion):
            return True

        return self.w != other.w or self.x != other.x or self.y != other.y or self.z != other.z

    def __cmp__(self, other):
        if other is None or not isinstance(other, Quaternion):
            return False

        return self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z

    @staticmethod
    def euler_radians_to_quaternion(yaw, pitch, roll):  # Z Y X
        cy = cos(yaw * 0.5)
        sy = sin(yaw * 0.5)
        cp = cos(pitch * 0.5)
        sp = sin(pitch * 0.5)
        cr = cos(roll * 0.5)
        sr = sin(roll * 0.5)

        qw = cy * cp * cr + sy * sp * sr
        qx = cy * cp * sr - sy * sp * cr
        qy = sy * cp * sr + cy * sp * cr
        qz = sy * cp * cr - cy * sp * sr

        return Quaternion(qw, qx, qy, qz)

    @staticmethod
    def euler_degrees_to_quaternion(yaw, pitch, roll):  # Z Y X
        yaw = radians(yaw)
        pitch = radians(pitch)
        roll = radians(roll)

        return Quaternion.euler_radians_to_quaternion(yaw, pitch, roll)
