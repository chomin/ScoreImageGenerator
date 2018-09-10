
class Pixel:

    @classmethod
    def is_in_tap(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色がTapの中身のものであればTrueを返す.
        :rtype: bool
        """

        if b in range(128, 213) and g in range(128, 238) and r in range(128, 238):
            return True
        else:
            return False

    @classmethod
    def is_green(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色がStart,TapEndの枠またはmiddleの中身のものであればTrueを返す.
        :rtype: bool
        """

        if b == 50 and g == 205 and r == 50:
            return True
        else:
            return False

    @classmethod
    def is_connecting_green(cls, b: int, g: int, r: int) -> bool:
        """
        （startを識別するためのもの。）
        :return: 色が長押しの途中のものであればTrueを返す.
        :rtype: bool
        """

        if b == 13 and g == 51 and r == 13:
            return True
        elif b == 106 and g == 144 and r == 92:
            return True
        elif b == 37 and g == 51 and r == 13:
            return True
        # elif b == 25 and g == 103 and r == 25:    # TapStartの中身 or つながり緑の枠。終点と認識されるのでだめ。
        #     return True
        elif b == 31 and g == 128 and r == 31:
            return True
        elif b == 31 and g == 128 and r == 43:
            return True
        elif b == 37 and g == 75 and r == 13: # サビ
            return True
        elif b == 140 and g == 178 and r == 140: # 小節境界線と繋がり緑中身
            return True
        elif b == 109 and g == 187 and r == 109: # 小節境界線と繋がり緑枠
            return True
        else:
            return False

    @classmethod
    def is_middle_frame(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色がmiddleの枠のものであればTrueを返す.
        :rtype: bool
        """

        if b == 211 and g == 211 and r == 211:
            return True
        else:
            return False

    @classmethod
    def is_tap_frame(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色がTapの枠のものであればTrueを返す.
        :rtype: bool
        """

        if b == 255 and g == 255 and r == 255:
            return True
        else:
            return False

    @classmethod
    def is_flick_frame(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色がFlickの枠のものであればTrueを返す.
        :rtype: bool
        """

        if b == 255 and g == 0 and r == 255:
            return True
        else:
            return False

    @classmethod
    def is_yellow_frame(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色が黄色円枠のものであればTrueを返す.
        :rtype: bool
        """
        if b == 0 and g == 165 and r == 255:  # 黄色
            return True
        else:
            return False

    @classmethod
    def is_following_color(cls, b: int, g: int, r: int) -> bool:
        """
        :return: 色が追跡すべきものであればTrueを返す.
        :rtype: bool
        """

        bgr = [b, g, r]

        if max(bgr) == g and max(bgr) != b and max(bgr) != r:
            return True
        elif cls.is_middle_frame(r, g, b):
            return True
        else:
            return False

        # if cls.is_connecting_green(b, g, r) or cls.is_flick_frame(b, g, r):
        #     return True
        # elif cls.is_green(b, g, r) or cls.is_middle_frame(b, g, r):
        #     return True
        # elif b == 42 and g == 221 and r == 138: # TapEnd中身+同時押し黄色
        #     return True
        # elif b == 47 and g == 221 and r == 142: # TapEnd中身+同時押し黄色+サビ
        #     return True
        # elif b == 95 and g == 192 and r == 95:  # TapEnd中身+小節境界線
        #     return True
        # elif b == 115 and g == 193 and r == 109:  # TapEnd中身+小節境界線+サビ
        #     return True
        # else:
        #     return False