# Finger Drawing

## Usage
### Requirements
* Python 3.11.X
### How to use
```python
python app.py
```
And enjoy

## 製品概要
ウェブカメラ1つで空中の手の動きを捉え、PC上に絵を描くことができます。

<img width="500" alt="SCR-20230502-nedr" src="data/instruction_finger_drawing.png">

デモ動画(YouTube): https://www.youtube.com/watch?v=Gdhfze8IuLo

### 背景(製品開発のきっかけ、課題等）
- タッチパッドを操作せずに、描画したい
- iPadや液晶タブレットなどのデバイスに依存せずに、PC上に高精度な絵を描きたい

<img width="800" alt="SCR-20230502-nedr" src=data/image1.png>

### 製品説明（具体的な製品の説明）
ウェブカメラにより、人差し指を認識して、空中に描いた絵をディスプレイ上に反映させます。

<img width="800" alt="SCR-20230502-nedr" src=data/image2.png>

### 特長
#### 1. 簡単なセットアップ
ウェブカメラがあればすぐに利用開始できます。
#### 2. 直感的な操作
PCのタッチパッドを使用せずに描くことができるので、あたかも画面に直接描くような感覚で使用することができます。

### 解決出来ること
- タッチパッドを使用せずに、直感的に描くことができます。
- iPadや液晶タブレットなどの外部デバイスが不要です

### 今後の展望
- 消しゴム機能の実装
- 2人以上で共同作業
- 線の太さや色を自在に変えたい
- 他デバイスとの連携、または他デバイスでも同じような機能を実装したい。(スマホ、タブレットなど)
### 注力したこと（こだわり等）
* 高精度のポインター認識
* どこを指しているのかわかりやすい

## 開発技術
### 活用した技術
* MediaPipe（骨格検出）

#### API・データ

#### フレームワーク・ライブラリ・モジュール
* MediaPipe
* OpenCV
* mediapipe
* tensorflow
* scikit-learn
* matplotlib
* protobuf

#### デバイス
* ウェブカメラ

### 独自技術
#### ハッカソンで開発した独自機能・技術
* 人差し指のみを伸ばしているときのみ、キャンバス上に描画する機能

#### 製品に取り入れた研究内容（データ・ソフトウェアなど）（※アカデミック部門の場合のみ提出必須）
* 
* 
