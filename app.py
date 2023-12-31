#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import copy
import time
import argparse
import itertools
import datetime
import os
# from collections import Counter
from collections import deque

import cv2 as cv
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# from utils import CvFpsCalc
from model import KeyPointClassifier
# from model import PointHistoryClassifier


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument('--use_static_image_mode', action='store_true')
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    args = parser.parse_args()

    return args


def run_app():
    # 引数解析 #################################################################
    args = get_args()

    cap_device = args.device
    cap_width = args.width
    cap_height = args.height

    use_static_image_mode = args.use_static_image_mode
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    # use_brect = True

    # カメラ準備 ###############################################################
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # モデルロード #############################################################
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=use_static_image_mode,
        max_num_hands=1,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    keypoint_classifier = KeyPointClassifier()

    # point_history_classifier = PointHistoryClassifier()

    # ラベル読み込み ###########################################################
    with open('model/keypoint_classifier/keypoint_classifier_label.csv',
              encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        keypoint_classifier_labels = [
            row[0] for row in keypoint_classifier_labels
        ]
    with open(
            'model/point_history_classifier/point_history_classifier_label.csv',
            encoding='utf-8-sig') as f:
        point_history_classifier_labels = csv.reader(f)
        point_history_classifier_labels = [
            row[0] for row in point_history_classifier_labels
        ]

    # FPS計測モジュール ########################################################
    # cvFpsCalc = CvFpsCalc(buffer_len=10)

    # 座標履歴 #################################################################
    history_length = 16
    point_history = deque(maxlen=history_length)

    # フィンガージェスチャー履歴 ################################################
    # finger_gesture_history = deque(maxlen=history_length)

    #  ########################################################################
    number, mode = 0, 0

    # 逐次処理が始まる前の初期設定
    # Create a new Figure and Axes for the separate window
    fig, ax = plt.subplots(dpi=180)
    # 背景色の設定
    # ax.set_facecolor("blue")

    # fig.canvas.mpl_connect('key_press_event', on_key)

    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 600)
    ax.invert_yaxis()

    # X軸とY軸の目盛りラベルを非表示にする
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # 枠線は表示されるが目盛りラベルは表示されない
    ax.tick_params(axis='x', which='both', length=0)  # X軸の目盛りの長さを0に
    ax.tick_params(axis='y', which='both', length=0)  # Y軸の目盛りの長さを0に


    # ポインタを表示するための初期設定
    pointer, = ax.plot([], [], 'go', markersize=10, zorder=4, alpha=0.5)  # ポインタを緑色で透明度0.5で初期化

    ax.label_ax = fig.add_axes([0.35, 0.05, 0.3, 0.03])  # 位置と大きさは必要に応じて調整　[x位置、y位置、幅、高さ]
    ax.label_ax.axis('off')


    hand_sign_4_start_time = None
    hand_sign_4_duration = 2  # 2秒間

    hand_sign_2_start_time = None
    hand_sign_2_duration = 3  # 3秒間
    
    end_start_time = None
    hand_sign_2_duration_end = 2  # 5秒間 (3+2)
    hand_sign_2_end_triggered = False  # 新しい状態管理変数を導入

    # Turn on interactive mode to update the plot
    # ax.axis('off')
    plt.ion()
    plt.show()

    count = 0
    while True:

        # fps = cvFpsCalc.get()


        # カメラキャプチャ #####################################################
        ret, image = cap.read()
        if not ret:
            break
        image = cv.flip(image, 1)  # ミラー表示
        debug_image = copy.deepcopy(image)

        # Matplotlibのウィンドウを更新する
        plt.pause(0.01)

        # 検出実施 #############################################################
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        #  ####################################################################
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                
                # ランドマークの計算
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # 相対座標・正規化座標への変換
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)
                pre_processed_point_history_list = pre_process_point_history(
                    debug_image, point_history)
                # 学習データ保存
                logging_csv(number, mode, pre_processed_landmark_list,
                            pre_processed_point_history_list)

                # ハンドサイン分類
                hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                hand_sign_label = keypoint_classifier_labels[hand_sign_id]
                
                # update_hand_sign_label(hand_sign_label)

                point_history.append(landmark_list[8])  # 人差指座標
                # 指先の座標を取得
                fingertip_coord = landmark_list[8]
                # ポインタの位置を更新
                pointer.set_data(fingertip_coord[0], fingertip_coord[1])

                if hand_sign_id == 3:  # screen shot
                    hand_sign_2_start_time = None
                    hand_sign_2_end_triggered = False
                    end_start_time = None
                    if hand_sign_4_start_time is None:
                        hand_sign_4_start_time = time.time()
                    elif (time.time() - hand_sign_4_start_time) >= hand_sign_4_duration:
                        pointer.set_data([], [])
                        take_screenshot(ax, fig)
                        pointer.set_data(fingertip_coord[0], fingertip_coord[1])
                        hand_sign_4_start_time = None
                        

                elif hand_sign_id == 1:  #close all delete
                    hand_sign_4_start_time = None
                    
                    if hand_sign_2_start_time is None:
                        hand_sign_2_start_time = time.time()
                    elif (time.time() - hand_sign_2_start_time) >= hand_sign_2_duration:
                        destroy_all(ax, fig)
                        pointer, = ax.plot([], [], 'go', markersize=10, zorder=4, alpha=0.5)  # ポインタを緑色で透明度0.5で初期化
                        hand_sign_2_start_time = None
                        end_start_time = time.time()
                        hand_sign_2_end_triggered = True 
                    elif hand_sign_2_end_triggered and (time.time() - end_start_time) >= hand_sign_2_duration_end:
                        os.system("osascript -e 'beep 3'")

                        return

                elif hand_sign_id == 2:  # 指差しサイン
                    hand_sign_4_start_time = None
                    hand_sign_2_start_time = None
                    hand_sign_2_end_triggered = False
                    end_start_time = None
                    if len(point_history) >= 2:
                        # Get the two most recent coordinates
                        recent_two_coords = [
                            point_history[-1], point_history[-2]]

                        if not [0, 0] in point_history:
                            draw_points(recent_two_coords, fig, ax, count)
                            count += 1
                else:
                    hand_sign_4_start_time = None
                    hand_sign_2_start_time = None
                    hand_sign_2_end_triggered = False
                    end_start_time = None
                    point_history = deque(maxlen=history_length)
                
                # ランドマークの描画
                # debug_image = draw_landmarks(debug_image, landmark_list)

        else:
            pass
            point_history.append([0, 0])
            hand_sign_label=""
            pointer.set_data([], [])
        update_hand_sign_label(fig, ax, hand_sign_label, ax.label_ax)
        # debug_image = draw_point_history(debug_image, point_history)
        # debug_image = draw_info(debug_image, mode, number)

        # 画面反映 #############################################################
        # cv.imshow('Hand Gesture Recognition', debug_image)

    # Keep the window open after updating
    plt.ioff()
    plt.show()

    cap.release()
    cv.destroyAllWindows()



def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)

        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # キーポイント
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # 相対座標に変換
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # 1次元リストに変換
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # 正規化
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # 相対座標に変換
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # 1次元リストに変換
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history




def draw_info_text(image, brect, handedness, hand_sign_text,
                   finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    if finger_gesture_text != "":
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                   cv.LINE_AA)

    return image


def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


def draw_info(image, mode, number):
    cv.putText(image, "FPS:", (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:", (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv.LINE_AA)

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv.LINE_AA)
    return image


def draw_points(points, fig, ax, count):
    # Plot new points
    for i in range(len(points) - 1):
        x_values = [points[i][0], points[i+1][0]]
        y_values = [points[i][1], points[i+1][1]]

        # print(count)
        ax.plot(x_values, y_values, "black", alpha=1.0)
        
    # Draw the updated plot
    plt.draw()

# これいる？
# def on_key(event):
#     global all_points
#     if event.key == ' ':
#         all_points = []
#         ax.clear()


def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = 'model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (0 <= number <= 9):
        csv_path = 'model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])
    return


def draw_info_text(image, brect, handedness, hand_sign_text,
                   finger_gesture_text):
    cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv.LINE_AA)

    if finger_gesture_text != "":
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv.LINE_AA)
        cv.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                   cv.LINE_AA)

    return image


def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


def draw_info(image, mode, number):
    cv.putText(image, "FPS:", (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv.LINE_AA)
    cv.putText(image, "FPS:", (10, 30), cv.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv.LINE_AA)

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv.LINE_AA)
        if 0 <= number <= 9:
            cv.putText(image, "NUM:" + str(number), (10, 110),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv.LINE_AA)
    return image

def take_screenshot(ax, fig):
    # 現在のタイムスタンプでファイル名を生成
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'FD_{timestamp}.png'
    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    # デスクトップのパスを取得
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    full_path = os.path.join(desktop_path, filename)

    ax.axis('off')

    # 画像を保存
    plt.savefig(full_path, bbox_inches=extent, transparent=True)
    ax.axis('on')

    # サウンドを再生
    os.system("osascript -e 'beep 1'")


def destroy_all(ax, fig):
    
    os.system("osascript -e 'beep 2'")

    # 軸の内容をクリア
    ax.clear()

    # 軸の設定を再適用
    ax.set_xlim(0, 1000)
    ax.set_ylim(0, 600)
    ax.invert_yaxis()

    # X軸とY軸の目盛りラベルを非表示にする
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # 枠線は表示されるが目盛りラベルは表示されない
    ax.tick_params(axis='x', which='both', length=0)  # X軸の目盛りの長さを0に
    ax.tick_params(axis='y', which='both', length=0)  # Y軸の目盛りの長さを0に



     

    # 変更を反映
    fig.canvas.draw()


def update_hand_sign_label(fig, ax, label,label_ax):

    # 古いラベルを削除（あれば）
    if hasattr(label_ax, 'hand_sign_text'):
        ax.label_ax.hand_sign_text.remove()

    # 新しいラベルを表示
    ax.label_ax.hand_sign_text = ax.label_ax.text(0.5, 0.5, label, 
                                                  transform=ax.label_ax.transAxes, 
                                                  verticalalignment='center', 
                                                  horizontalalignment='center',
                                                  fontsize=12, color='black',
                                                  bbox=dict(facecolor='gray', edgecolor='none', alpha=0.5)
    )
    

    fig.canvas.draw_idle()

def remove_white_background(image):
    # BGR から HSV へ変換
    hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # 白色の範囲を定義（HSV空間）
    # HSVで白色は、低い彩度と高い明度で表されます。
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 55, 255])

    # 背景色（白色）のマスクを作成
    mask = cv.inRange(hsv, lower_white, upper_white)

    # マスクを反転して前景を取得
    foreground = cv.bitwise_and(image, image, mask=~mask)

    # 透明度アルファチャンネルの追加
    alpha_channel = cv.bitwise_not(mask)
    b, g, r = cv.split(foreground)
    rgba = [b, g, r, alpha_channel]
    dst = cv.merge(rgba)

    return dst



if __name__ == '__main__':

    run_app()
