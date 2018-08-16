import ImageProcessor as ip
from Note import *
import sys
from operator import attrgetter


class BMSFactory:

    MUSIC_NAME = '正解はひとつ！じゃない！！(expert)'
    ARTIST = 'ミルキィホームズ'
    BPM = 170
    PLAY_LEVEL: int = 25

    BAR_NUM = 74

    FILE_NAME = '正解はひとつ！じゃない！！(expert).bms'

    def __init__(self):

        with open(self.FILE_NAME, mode='w') as f:   # 新規作成または上書きモードで開く

            f.write('\n*---------------------- HEADER FIELD\n')
            f.write('\n#PLAYER 1\n')
            f.write('#TITLE ' + self.MUSIC_NAME + '\n')
            f.write('#ARTIST ' + self.ARTIST + '\n')
            f.write('#BPM ' + str(self.BPM) + '\n')
            f.write('#PLAYLEVEL ' + str(self.PLAY_LEVEL) + '\n')

            # f.write('\n#LNTYPE 1\n')
            # f.write('\n#WAV01 タップ.mp3\n')
            # f.write('#WAV02 フリック.mp3\n')
            # f.write('#WAV03 始め１.mp3\n')
            # f.write('#WAV04 途中１.mp3\n')
            # f.write('#WAV05 離し１.mp3\n')
            # f.write('#WAV06 フリック離し１.mp3\n')
            # f.write('#WAV07 始め２.mp3\n')
            # f.write('#WAV08 途中２.mp3\n')
            # f.write('#WAV09 離し２.mp3\n')
            # f.write('#WAV0A フリック離し２.mp3\n')
            # f.write('#WAV10 ' + self.MUSIC_NAME + '.mp3\n')
            # f.write('#WAV11 15sec.mp3\n')

            f.write('\n*---------------------- MAIN DATA FIELD\n')

    def write_main(self, notes):

        # print(notes[0])

        with open(self.FILE_NAME, mode='a') as f:   # 追記モードで開く

            # 曲の始まりを指定（現時点では適当）
            f.write('\n#00101:00001000\n')

            start_indexes = [0, 0, 0, 0, 0, 0, 0]
            for bar in range(1, ip.ImageProcessor.BAR_NUM + 1):  # 小節ループ
                for lane_index in range(0, 7):  # レーンループ
                    lane_num = lane_index+1

                    # 1行(1小節)分のノーツを取得し、一行分書き込み
                    bar_notes = list()

                    # bar_num = int(notes[lane_index][start_indexes[lane_index]].pos / 4.0) + 1
                    for note in notes[lane_index][start_indexes[lane_index]:]:
                        if note.pos/4.0 < bar:
                            bar_notes.append(note)
                            # print(note)
                            if notes[lane_index].index(note) == len(notes[lane_index])-1:
                                start_indexes[lane_index] = len(notes[lane_index])
                        else:
                            start_indexes[lane_index] = notes[lane_index].index(note)
                            break

                    if len(bar_notes) == 0:
                        continue

                    bar_notes = sorted(bar_notes, key=lambda n: n.pos)  # pos順ではない事があるのでソートする

                    # if bar == 6:
                        # print(sorted(bar_notes, key=lambda n: n.pos))
                        # for note in bar_notes:
                        #     print(note.pos)

                    # 1行あたりのユニット数を数える
                    is_writable = False
                    unit_num = 1
                    # print(unit_num)
                    had_multiplied_three = False
                    while not is_writable:
                        is_writable = True
                        for note in bar_notes:
                            if abs(note.pos/4.0*unit_num - int(note.pos/4*unit_num)) > 0.01:  #場合分け？
                                dif = note.pos/4.0*unit_num - int(note.pos/4*unit_num)
                                # print('dif:' + str(dif))
                                is_writable = False
                                if not had_multiplied_three:
                                    if abs(dif - 1.0/3.0) < 0.01:
                                        unit_num *= 3
                                        had_multiplied_three = True
                                        # print(note.pos)
                                        # print(note.pos/4.0*unit_num - int(note.pos/4*unit_num))
                                    elif abs(dif - 2.0/3.0) < 0.01:
                                        unit_num *= 3
                                        had_multiplied_three = True
                                        # print(note.pos)
                                        # print(note.pos / 4.0 * unit_num - int(note.pos / 4 * unit_num))
                                    else:
                                        unit_num *= 2
                                else:
                                    unit_num *= 2

                                break

                    if lane_num < 6:
                        row_str = '\n#' + '{0:03d}'.format(int(bar)) + '1' + str(lane_num) + ':'
                    else:
                        row_str = '\n#' + '{0:03d}'.format(int(bar)) + '1' + str(lane_num+2) + ':'
                    writing_note_index = 0



                    # print(unit_num)
                    # if unit_num > 32:
                    #     for note in bar_notes:
                    #         print('pos:' + str(note.pos))

                    for i in range(1, unit_num+1):

                        # if lane_index + 1 == 5 and bar == 4 and i == 10:
                        #     print(abs((bar_notes[writing_note_index].pos - (bar-1) * 4) * unit_num / 4.0 + 1 - i))
                        #     print(str((bar_notes[writing_note_index].pos - (bar-1) * 4) * unit_num / 4.0 + 1))
                        #     print(str((bar_notes[writing_note_index+1].pos - (bar - 1) * 4) * unit_num / 4.0 + 1))
                        #     print(writing_note_index > len(bar_notes)-1)
                        #     for j in bar_notes:
                        #         print(j.pos)

                        if writing_note_index > len(bar_notes)-1:
                            row_str += '00'
                            continue

                        if abs((bar_notes[writing_note_index].pos - (bar-1) * 4) * unit_num / 4.0 + 1 - i) < 0.01:
                            note_type = bar_notes[writing_note_index].note_type
                            if note_type == NoteType.TAP:
                                row_str += '01'
                            elif note_type == NoteType.FLICK:
                                row_str += '02'
                            elif note_type == NoteType.START:
                                row_str += '03'
                            elif note_type == NoteType.MIDDLE:
                                row_str += '04'
                            elif note_type == NoteType.TAP_END:
                                row_str += '05'
                            elif note_type == NoteType.FLICK_END:
                                row_str += '06'
                            elif note_type == NoteType.START2:
                                row_str += '07'
                            elif note_type == NoteType.MIDDLE2:
                                row_str += '08'
                            elif note_type == NoteType.TAP_END2:
                                row_str += '09'
                            elif note_type == NoteType.FLICK_END2:
                                row_str += '0A'

                            writing_note_index += 1
                        else:
                            # print('dif2:' + str((bar_notes[writing_note_index].pos - (bar-1) * 4) * unit_num / 4.0 + 1 - i))
                            row_str += '00'

                    if writing_note_index != len(bar_notes):
                        print('書き込まれていないノーツがあります.@レーン, 小節:' + str(lane_index+1) + ', ' + str(bar))
                        for j in bar_notes[writing_note_index:]:
                            print(str(j.note_type) + ', ' + str((j.pos - (bar-1) * 4) * unit_num / 4.0 + 1))
                            print('unit_num:' + str(unit_num))
                        sys.exit("エラー終了")

                    row_str += '\n'
                    f.write(row_str)

