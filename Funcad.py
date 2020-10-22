import ctypes
from numpy.ctypeslib import ndpointer
import os


class Funcad:
    def __init__(self):
        self.cos15 = 0.965926
        self.cos30 = 0.866
        self.cos45 = 0.7071
        self.cos60 = 0.5
        self.cos75 = 0.258819

        # init all func from dll
        path_to_dll = os.path.abspath(__file__)[:-10] + r"/data/CForPy.dll"
        self.rcad_dll = ctypes.cdll.LoadLibrary(path_to_dll)
        self.rcad_dll.rcad_new.restype = ctypes.c_void_p
        self.rcad_class = self.rcad_dll.rcad_new()

        self.rcad_dll.fmta.restype = ndpointer(ctypes.c_float, shape=(3,))
        self.rcad_dll.fmta.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_float]

        self.rcad_dll.fatm.restype = ndpointer(ctypes.c_float, shape=(3,))
        self.rcad_dll.fatm.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_float]

        self.rcad_dll.in_range_bool.restype = ctypes.c_bool
        self.rcad_dll.in_range_bool.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.c_float, ctypes.c_float]

        self.rcad_dll.transfunc_coda.restype = ctypes.c_float
        self.rcad_dll.transfunc_coda.argtypes = [ctypes.c_void_p, ctypes.c_float, ctypes.POINTER(ctypes.c_float),
                            ctypes.POINTER(ctypes.c_float), ctypes.c_int]

        # other
        self.__is_not_used = True

    def from_motors_to_axis(self, right: float, left: float, back: float):
        return self.rcad_dll.fmta(self.rcad_class, right, left, back)

    def from_axis_to_motors(self, x: float, y: float, z: float):
        return self.rcad_dll.fatm(self.rcad_class, x, y, z)

    def in_range_bool(self, val: float, min_v: float, max_v: float):
        """
        Func that checks that value in range min and max
        :param val: Value that needs to check
        :param min_v: Min limit
        :param max_v: Max limit
        :return: Value in range
        """
        return self.rcad_dll.in_range_bool(self.rcad_class, val, min_v, max_v)

    def transfunc_coda(self, val: float, in_arr: list, out_arr: list):
        """
        Not moronic transfer function
        Powered by Coda (Vitality)
        :param val: Input of value to conversion by transfer function
        :param in_arr: Input array
        :param out_arr: Output array
        :return: Output is conversed input
        """
        ndp = ctypes.c_float * len(in_arr)
        in_arr_c = ctypes.cast(ndp(*in_arr), ctypes.POINTER(ctypes.c_float))
        out_arr_c = ctypes.cast(ndp(*out_arr), ctypes.POINTER(ctypes.c_float))
        return self.rcad_dll.transfunc_coda(self.rcad_class, val, in_arr_c, out_arr_c, len(in_arr))
