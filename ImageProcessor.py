import sys

import BMSFactory6
import Note
import Pixel
import PixelState
import Point
import cv2
import numpy as np
from Note import *
from Pixel import *
from PixelState import *
from Point import *


class ImageProcessor:
    FILE_NAME = "kimija_nakya_damemitai(expert).png"
    BPM = 131
    LANE_NUM = 7
    BAR_NUM = 53
    BAR_NUM_PER_COLUMN: int = 8
    COLUMN_NUM = 7

    LANE_WIDTH: int = 20
    COLUMN_WIDTH = 220  # 間の空白含む
    POS_LENGTH = 48
    BAR_LENGTH = POS_LENGTH * 4

    BASIC_START_POINT: Point = Point(80, 1662)  # 1小節目１レーン目の真ん中

    NOTE_CENTER_OFFSET_FROM_FRAME = 4

    @classmethod
    def process_score_image(cls):

        bms_factory = BMSFactory6.BMSFactory()

        notes = [[], [], [], [], [], [], []]  # レーン別のノーツの情報
        is_usable = [True, True]  # 長押しをいくつ追跡しているかをカウントする。

        img = cv2.imread(cls.FILE_NAME)

        states = list()  # レーン別の状態()
        for i in range(0, cls.LANE_NUM):
            states.append(PixelState(StateType.NONE, 0))

        #
        # ------- 画像解析開始 --------
        #

        for bar in range(1, cls.BAR_NUM+1):  # 小節に関するループ

            column_index = int((bar-1) / cls.BAR_NUM_PER_COLUMN)  # 何列目か

            for pixel_offset in range(0, cls.BAR_LENGTH):  # ピクセル単位のループ(縦)

                for lane_index in range(0, cls.LANE_NUM):  # レーンに関するループ

                    offset_x = lane_index * cls.LANE_WIDTH + column_index * cls.COLUMN_WIDTH
                    offset_y = -((bar-1) % cls.BAR_NUM_PER_COLUMN) * cls.BAR_LENGTH

                    lane_start_point = Point.sum(cls.BASIC_START_POINT, Point(offset_x, offset_y))
                    # print("bar, lane_index, startpoint")
                    # if bar == 1:
                    #     print(str(bar) + " " + str(lane_index) + "(" + str(lane_start_point.x) + ", " + str(lane_start_point.y) + ")")

                    bgr = img[int(lane_start_point.y) - pixel_offset, int(lane_start_point.x)]
                    b = bgr[0]
                    g = bgr[1]
                    r = bgr[2]

                    left_bgr = img[int(lane_start_point.y) - pixel_offset, int(lane_start_point.x - cls.LANE_WIDTH * 0.3)]
                    lb = left_bgr[0]
                    lg = left_bgr[1]
                    lr = left_bgr[2]

                    right_bgr = img[int(lane_start_point.y) - pixel_offset, int(lane_start_point.x + cls.LANE_WIDTH * 0.3)]
                    rb = right_bgr[0]
                    rg = right_bgr[1]
                    rr = right_bgr[2]

                    lane_state = states[lane_index]

                    # 各ノーツを識別する
                    if lane_state.state == StateType.NONE:

                        if Pixel.is_tap_frame(b, g, r):
                            lane_state.state = StateType.IN_TAP
                            lane_state.from_pixel_index = pixel_offset + (bar-1) * cls.BAR_LENGTH

                        elif Pixel.is_flick_frame(b, g, r):
                            lane_state.state = StateType.IN_PINK
                            lane_state.from_pixel_index = pixel_offset + (bar-1) * cls.BAR_LENGTH

                        elif Pixel.is_green(b, g, r):
                            lane_state.state = StateType.IN_GREEN
                            lane_state.from_pixel_index = pixel_offset + (bar-1) * cls.BAR_LENGTH

                        elif Pixel.is_middle_frame(b, g, r):
                            lane_state.state = StateType.IN_MIDDLE
                            lane_state.from_pixel_index = pixel_offset + (bar-1) * cls.BAR_LENGTH

                        elif Pixel.is_yellow_frame(b, g, r):
                            lane_state.state = StateType.IN_YELLOW
                            lane_state.from_pixel_index = pixel_offset + (bar - 1) * cls.BAR_LENGTH

                    elif lane_state.state == StateType.IN_PINK:

                        # 一番下の次のピクセルの横の色から終点であるかを判断
                        is_flick_end = False
                        for pixel_x in range(int(lane_start_point.x - cls.LANE_WIDTH / 2),
                                             int(lane_start_point.x + cls.LANE_WIDTH / 2)):

                            bgr_t = img[int(lane_start_point.y) - pixel_offset, int(pixel_x)]
                            b_t = bgr_t[0]
                            g_t = bgr_t[1]
                            r_t = bgr_t[2]
                            if Pixel.is_connecting_green(b_t, g_t, r_t):
                                is_flick_end = True

                        if is_flick_end:
                            lane_state.state = StateType.IN_FLICK_END
                        else:
                            lane_state.state = StateType.IN_FLICK

                    elif lane_state.state == StateType.IN_GREEN:

                        is_tap_end = False
                        for pixel_x in range(int(lane_start_point.x - cls.LANE_WIDTH / 2),
                                             int(lane_start_point.x + cls.LANE_WIDTH / 2)):

                            bgr_t = img[int(lane_start_point.y) - pixel_offset, int(pixel_x)]
                            b_t = bgr_t[0]
                            g_t = bgr_t[1]
                            r_t = bgr_t[2]
                            if Pixel.is_connecting_green(b_t, g_t, r_t):
                                is_tap_end = True

                        if is_tap_end:
                            lane_state.state = StateType.IN_TAP_END
                        else:
                            lane_state.state = StateType.IN_START
                            if is_usable[0]:
                                lane_state.following_long_num = 1
                                is_usable[0] = False
                            elif is_usable[1]:
                                lane_state.following_long_num = 2
                                is_usable[1] = False
                            else:
                                print("セマフォが0です")
                                tstr = "追跡状況："
                                for i in range(0, cls.LANE_NUM):
                                    tstr += str(states[i].following_long_num) + ", "
                                print(tstr)
                                print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                    lane_start_point.x))
                                print("レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                sys.exit("エラー終了")

                    elif lane_state.state == StateType.IN_TAP:

                        if Pixel.is_tap_frame(b, g, r):
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (bar-1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH
                            # pixel_from_this_bar =
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            notes[lane_index].append(Note(NoteType.TAP, pos, lane_index))
                            # if bar == 6:
                            #     print("Tap@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            #     print(pos)

                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset

                    elif lane_state.state == StateType.IN_START:

                        if Pixel.is_green(b, g, r):
                            # pixel_from_this_bar = (lane_state.from_pixel_index + pixel_offset + (
                            #             bar - 1) * cls.BAR_LENGTH) / 2
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH

                            if lane_state.following_long_num == 1:
                                notes[lane_index].append(Note(NoteType.START, pos, lane_index))
                            elif lane_state.following_long_num == 2:
                                notes[lane_index].append(Note(NoteType.START2, pos, lane_index))
                            else:
                                print("following_long_numが不正です.@start:" + str(lane_state.following_long_num))
                                print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                    lane_start_point.x))
                                print("レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                sys.exit("エラー終了")

                            # print("Start@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset

                    elif lane_state.state == StateType.IN_TAP_END:

                        if Pixel.is_green(b, g, r):
                            # pixel_from_this_bar = (lane_state.from_pixel_index + pixel_offset + (
                            #         bar - 1) * cls.BAR_LENGTH) / 2
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH

                            if lane_state.following_long_num == 1:
                                notes[lane_index].append(Note(NoteType.TAP_END, pos, lane_index))
                                is_usable[0] = True
                            elif lane_state.following_long_num == 2:
                                notes[lane_index].append(Note(NoteType.TAP_END2, pos, lane_index))
                                is_usable[1] = True
                            else:
                                print("following_long_numが不正です.@tapEnd:" + str(lane_state.following_long_num))
                                print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(lane_start_point.x))
                                print("レーン, 小節:" + str(lane_index+1) + ", " + str(bar))
                                sys.exit("エラー終了")

                            if bar == 8:
                                print("TapEnd@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                print(pos)
                            # print("TapEnd@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset
                            lane_state.following_long_num = 0

                    elif lane_state.state == StateType.IN_FLICK:

                        if Pixel.is_flick_frame(b, g, r):
                            # pixel_from_this_bar = (lane_state.from_pixel_index + pixel_offset + (
                            #         bar - 1) * cls.BAR_LENGTH) / 2
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH
                            notes[lane_index].append(Note(NoteType.FLICK, pos, lane_index))

                            # print("Flick@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset

                    elif lane_state.state == StateType.IN_FLICK_END:

                        if Pixel.is_flick_frame(b, g, r):
                            # pixel_from_this_bar = (lane_state.from_pixel_index + pixel_offset + (
                            #         bar - 1) * cls.BAR_LENGTH) / 2
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH

                            if lane_state.following_long_num == 1:
                                notes[lane_index].append(Note(NoteType.FLICK_END, pos, lane_index))
                                is_usable[0] = True
                            elif lane_state.following_long_num == 2:
                                notes[lane_index].append(Note(NoteType.FLICK_END2, pos, lane_index))
                                is_usable[1] = True
                            else:
                                print("following_long_numが不正です.@flickEnd:" + str(lane_state.following_long_num))
                                print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                    lane_start_point.x))
                                print("レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                sys.exit("エラー終了")

                            # print("FlickEnd@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset
                            lane_state.following_long_num = 0

                    elif lane_state.state == StateType.IN_MIDDLE:

                        if Pixel.is_middle_frame(b, g, r):
                            # pixel_from_this_bar = (lane_state.from_pixel_index + pixel_offset + (
                            #         bar - 1) * cls.BAR_LENGTH) / 2
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH

                            if lane_state.following_long_num == 1:
                                notes[lane_index].append(Note(NoteType.MIDDLE, pos, lane_index))
                            elif lane_state.following_long_num == 2:
                                notes[lane_index].append(Note(NoteType.MIDDLE2, pos, lane_index))
                            else:
                                print("following_long_numが不正です.@middle:" + str(lane_state.following_long_num))
                                print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                    lane_start_point.x))
                                print("レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                sys.exit("エラー終了")
                                # print("@lane_index:" + str(lane_index))

                            # print("Middle@レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset

                    elif lane_state.state == StateType.IN_YELLOW:
                        if Pixel.is_yellow_frame(b, g, r):
                            note_pixel_index = (lane_state.from_pixel_index + pixel_offset + (
                                        bar - 1) * cls.BAR_LENGTH) / 2
                            pos = note_pixel_index * 4 / cls.BAR_LENGTH

                            is_tap = True
                            for pixel_x in range(int(lane_start_point.x - cls.LANE_WIDTH / 2),
                                                 int(lane_start_point.x + cls.LANE_WIDTH / 2)):

                                bgr_t = img[int(lane_start_point.y) - pixel_offset, int(pixel_x)]
                                b_t = bgr_t[0]
                                g_t = bgr_t[1]
                                r_t = bgr_t[2]
                                if Pixel.is_connecting_green(b_t, g_t, r_t):
                                    is_tap = False

                            if is_tap:
                                notes[lane_index].append(Note(NoteType.TAP, pos, lane_index))
                            else:
                                if is_usable[1]:
                                    notes[lane_index].append(Note(NoteType.START2, pos, lane_index))
                                    lane_state.following_long_num = 2
                                    is_usable[1] = False

                                elif is_usable[0]:
                                    notes[lane_index].append(Note(NoteType.START, pos, lane_index))
                                    lane_state.following_long_num = 1
                                    is_usable[0] = False

                                else:
                                    print("セマフォが0です")
                                    tstr = "追跡状況："
                                    for i in range(0, cls.LANE_NUM):
                                        tstr += str(states[i].following_long_num) + ", "
                                    print(tstr)
                                    print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                        lane_start_point.x))
                                    print("レーン, 小節:" + str(lane_index + 1) + ", " + str(bar))
                                    sys.exit("エラー終了")

                            # pixel_from_this_bar =
                            # pos_from_this_bar: float = pixel_from_this_bar / cls.BAR_LENGTH * 4.0
                            # pos = pos_from_this_bar + (bar - 1) * 4.0

                            lane_state.state = StateType.NONE
                            lane_state.from_pixel_index = pixel_offset

                    # 辿っている長押しのレーン変更を識別する
                    if lane_state.will_stop_following and lane_state.state == StateType.NONE:
                        lane_state.following_long_num = 0
                        lane_state.will_stop_following = False

                    if lane_state.following_long_num > 0 and not lane_state.will_stop_following:
                        if lane_state.state == StateType.NONE or lane_state.state == StateType.IN_START:
                            if lane_state.left_state == SubStateType.FOLLOWING_LONG:
                                if not Pixel.is_following_color(lb, lg, lr):
                                    if lane_state.right_state == SubStateType.FOLLOWING_LONG and not Pixel.is_following_color(rb, rg, rr):
                                        print("両方！？")
                                        print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                            lane_start_point.x))
                                        sys.exit("エラー終了")
                                    else:
                                        # print("@laneIndex:" + str(lane_index) + ", @bar:" + str(bar))
                                        # print("@x:" + str(lane_start_point.x) + ", @y:" + str(lane_start_point.y - pixel_offset))
                                        # print("state:" + str(lane_state.state))
                                        # print("右(" + str(lane_index+1) + "→" + str(lane_index+2))
                                        # print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                        #     lane_start_point.x))
                                        states[lane_index + 1].following_long_num = lane_state.following_long_num
                                        if lane_state.state == StateType.NONE:
                                            lane_state.following_long_num = 0
                                        else:
                                            lane_state.will_stop_following = True

                            if lane_state.right_state == SubStateType.FOLLOWING_LONG:
                                if not Pixel.is_following_color(rb, rg, rr):
                                    # print(lane_index)
                                    # print("左(" + str(lane_index+1) + "→" + str(lane_index))
                                    # print("座標(y,x):" + str(int(lane_start_point.y) - pixel_offset) + ", " + str(
                                    #     lane_start_point.x))
                                    states[lane_index - 1].following_long_num = lane_state.following_long_num
                                    if lane_state.state == StateType.NONE:
                                        lane_state.following_long_num = 0
                                    else:
                                        lane_state.will_stop_following = True

                    if Pixel.is_following_color(lb, lg, lr):
                        lane_state.left_state = SubStateType.FOLLOWING_LONG
                    else:
                        lane_state.left_state = SubStateType.NONE

                    if Pixel.is_following_color(rb, rg, rr):
                        lane_state.right_state = SubStateType.FOLLOWING_LONG
                    else:
                        lane_state.right_state = SubStateType.NONE

        #
        # ------- ファイル作成 -------
        #

        bms_factory.write_main(notes)
